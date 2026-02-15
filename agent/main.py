#!/usr/bin/env python3
"""
Kernox — eBPF Endpoint Agent

Main entry point. Ties together:
  - eBPF Process Monitor (execve / exit tracing)
  - Process Lineage Tree (parent→child DAG)
  - Event Emitter (JSON output)
  - Heartbeat (periodic health signals)

Usage:
    sudo python3 -m agent.main

Requires root privileges for eBPF operations.
"""

import os
import signal
import sys

# ── Ensure we can import the agent package ──────────────────────
# When run as `sudo python3 -m agent.main` from the Kernox directory,
# Python's cwd is already correct. But if run directly, we need to
# add the project root to sys.path.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.config import ENDPOINT_ID, HOSTNAME, PROCESS_TREE_MAX_SIZE
from agent.ebpf.process_monitor import ProcessMonitor
from agent.events.event_emitter import EventEmitter
from agent.tracking.process_tree import ProcessTree
from agent.health.heartbeat import Heartbeat


BANNER = r"""
  _  __                          
 | |/ / ___  _ __  _ __   ___ __  __
 | ' / / _ \| '__|| '_ \ / _ \\ \/ /
 | . \|  __/| |   | | | | (_) |>  < 
 |_|\_\\___||_|   |_| |_|\___//_/\_\

  eBPF Endpoint Agent — Process Monitor
"""


def main() -> None:
    # ── Check privileges ─────────────────────────────────────
    if os.geteuid() != 0:
        print("[ERROR] This agent requires root privileges.", file=sys.stderr)
        print("        Run with: sudo python3 -m agent.main", file=sys.stderr)
        sys.exit(1)

    print(BANNER, file=sys.stderr)
    print(f"[*] Hostname  : {HOSTNAME}", file=sys.stderr)
    print(f"[*] Endpoint  : {ENDPOINT_ID}", file=sys.stderr)
    print(f"[*] Tree limit: {PROCESS_TREE_MAX_SIZE}", file=sys.stderr)
    print("", file=sys.stderr)

    # ── Initialize components ────────────────────────────────
    tree = ProcessTree(max_size=PROCESS_TREE_MAX_SIZE)
    emitter = EventEmitter()
    heartbeat = Heartbeat(event_emitter=emitter, process_tree=tree)
    monitor = ProcessMonitor(emitter=emitter, tree=tree)

    # ── Graceful shutdown ────────────────────────────────────
    def shutdown(signum, frame):
        print("\n[*] Shutting down Kernox agent...", file=sys.stderr)
        monitor.stop()
        heartbeat.stop()
        print(f"[*] Total events emitted: {emitter.event_count}", file=sys.stderr)
        print(f"[*] Processes tracked   : {tree.size}", file=sys.stderr)
        print("[*] Agent stopped.", file=sys.stderr)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # ── Start ────────────────────────────────────────────────
    heartbeat.start()
    print("[*] Heartbeat started.", file=sys.stderr)

    try:
        monitor.start()  # Blocking — polls perf buffers
    except Exception as e:
        print(f"[ERROR] Monitor failed: {e}", file=sys.stderr)
        heartbeat.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
