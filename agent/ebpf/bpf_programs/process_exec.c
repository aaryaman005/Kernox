/*
 * Kernox — eBPF Process Monitoring Program
 *
 * Attaches to:
 *   - tracepoint/syscalls/sys_enter_execve  (process execution)
 *   - tracepoint/sched/sched_process_exit   (process termination)
 *
 * Captures: PID, PPID, UID, comm, filename
 * Sends structured events to userspace via BPF_PERF_OUTPUT.
 *
 * NOTE: Large data structures are stored in per-CPU array maps
 * to avoid exceeding the 512-byte BPF stack limit.
 */

#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

#define ARGSIZE       128
#define TASK_COMM_LEN  16

/* ── Event types ─────────────────────────────────────────────── */
enum event_type {
    EVENT_PROCESS_EXEC = 1,
    EVENT_PROCESS_EXIT = 2,
};

/* ── Data structures sent to userspace ───────────────────────── */

struct exec_event_t {
    u32 pid;
    u32 ppid;
    u32 uid;
    u32 gid;
    u8  event_type;
    char comm[TASK_COMM_LEN];
    char filename[ARGSIZE];
};

struct exit_event_t {
    u32 pid;
    u32 ppid;
    u32 uid;
    u8  event_type;
    char comm[TASK_COMM_LEN];
    int  exit_code;
};

/* ── Perf output channels ────────────────────────────────────── */
BPF_PERF_OUTPUT(exec_events);
BPF_PERF_OUTPUT(exit_events);

/* ── Per-CPU scratch space to avoid stack overflow ────────────── */
BPF_PERCPU_ARRAY(exec_scratch, struct exec_event_t, 1);

/* ─────────────────────────────────────────────────────────────
 *  TRACEPOINT: sys_enter_execve
 *  Fires when any process calls execve().
 * ───────────────────────────────────────────────────────────── */
TRACEPOINT_PROBE(syscalls, sys_enter_execve) {
    int zero = 0;
    struct exec_event_t *event = exec_scratch.lookup(&zero);
    if (!event) return 0;

    struct task_struct *task;

    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;

    /* Filter kernel threads */
    if (pid == 0) return 0;

    event->pid = pid;
    event->uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    event->gid = bpf_get_current_uid_gid() >> 32;
    event->event_type = EVENT_PROCESS_EXEC;

    /* Get parent PID from task_struct */
    task = (struct task_struct *)bpf_get_current_task();
    event->ppid = task->real_parent->tgid;

    /* Get process comm */
    bpf_get_current_comm(&event->comm, sizeof(event->comm));

    /* Read filename (first arg to execve) */
    const char *filename = args->filename;
    bpf_probe_read_user_str(&event->filename, sizeof(event->filename), filename);

    exec_events.perf_submit(args, event, sizeof(*event));
    return 0;
}

/* ─────────────────────────────────────────────────────────────
 *  TRACEPOINT: sched_process_exit
 *  Fires when a process terminates.
 * ───────────────────────────────────────────────────────────── */
TRACEPOINT_PROBE(sched, sched_process_exit) {
    struct exit_event_t event = {};
    struct task_struct *task;

    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;

    /* Filter kernel threads */
    if (pid == 0) return 0;

    event.pid = pid;
    event.uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    event.event_type = EVENT_PROCESS_EXIT;

    /* Get parent PID */
    task = (struct task_struct *)bpf_get_current_task();
    event.ppid = task->real_parent->tgid;

    /* Get comm and exit code */
    bpf_get_current_comm(&event.comm, sizeof(event.comm));
    event.exit_code = task->exit_code >> 8;

    exit_events.perf_submit(args, &event, sizeof(event));
    return 0;
}
