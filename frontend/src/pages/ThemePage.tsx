import { useState } from 'react';
import { motion } from 'motion/react';
import { Palette, RotateCcw, Check } from 'lucide-react';
import { GlassCard } from '../components/GlassCard';
import { useTheme, defaultTheme, ThemeColors } from '../context/ThemeContext';

interface ColorSwatchProps {
  label: string;
  value: string;
  onChange: (val: string) => void;
  description?: string;
}

function ColorSwatch({ label, value, onChange, description }: ColorSwatchProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="flex items-center gap-4 p-4 rounded-xl border border-[#7A4832]/14 bg-[#040A18]/60 group hover:bg-[#040A18]/80 transition-colors">
      {/* Color picker swatch */}
      <div className="relative flex-shrink-0">
        <div
          className="w-12 h-12 rounded-xl border-2 border-white/10 shadow-lg cursor-pointer overflow-hidden"
          style={{ backgroundColor: value }}
        >
          <input
            type="color"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            title={`Pick color for ${label}`}
          />
        </div>
      </div>

      {/* Label and hex */}
      <div className="flex-1 min-w-0">
        <p className="text-sm mb-0.5" style={{ color: '#E2DED8' }}>{label}</p>
        {description && (
          <p className="text-xs text-[#5C6474]">{description}</p>
        )}
      </div>

      {/* Hex value + copy */}
      <div className="flex items-center gap-2">
        <code className="text-xs font-mono text-[#7A9AB8] bg-[#060D1A]/80 px-2 py-1 rounded-md border border-[#7A4832]/12">
          {value.toUpperCase()}
        </code>
        <button
          onClick={handleCopy}
          className="p-1.5 rounded-lg hover:bg-[#7A4832]/15 transition-colors text-[#5C6474] hover:text-[#E2DED8]"
          title="Copy hex"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : (
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}

function SeverityPreview({ colors }: { colors: ThemeColors }) {
  const items = [
    { label: 'Critical', key: 'critical' as const, example: 'ALT-2026-001' },
    { label: 'High', key: 'high' as const, example: 'ALT-2026-003' },
    { label: 'Medium', key: 'medium' as const, example: 'ALT-2026-005' },
    { label: 'Low', key: 'low' as const, example: 'ALT-2026-007' },
  ];

  return (
    <div className="space-y-2">
      {items.map((item) => {
        const color = colors.severity[item.key];
        return (
          <div key={item.key} className="flex items-center gap-3 p-3 rounded-lg bg-[#040A18]/60 border border-[#7A4832]/10">
            <span
              className="text-xs px-2.5 py-1 rounded-full capitalize"
              style={{ color, backgroundColor: `${color}18`, border: `1px solid ${color}30` }}
            >
              {item.label}
            </span>
            <span className="text-xs font-mono text-[#5C6474]">{item.example}</span>
            <div className="flex-1 h-1 rounded-full bg-[#09152A] overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{
                  width: item.key === 'critical' ? '95%' : item.key === 'high' ? '78%' : item.key === 'medium' ? '58%' : '28%',
                  backgroundColor: color,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function ThemePage() {
  const { colors, setColors, resetColors } = useTheme();
  const [saved, setSaved] = useState(false);

  const updateSeverity = (key: keyof typeof colors.severity, value: string) => {
    setColors({
      ...colors,
      severity: { ...colors.severity, [key]: value },
    });
  };

  const updateAccent = (value: string) => {
    setColors({ ...colors, accent: value });
  };

  const handleReset = () => {
    resetColors();
    setSaved(false);
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="min-h-screen pb-16 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{ scale: [1, 1.15, 1], opacity: [0.03, 0.05, 0.03] }}
          transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute top-0 left-0 w-3/4 h-3/4 bg-gradient-to-br from-[#7A4832]/10 to-transparent rounded-full blur-3xl"
        />
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center justify-between mb-10"
        >
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2.5 bg-[#7A4832]/15 rounded-xl border border-[#7A4832]/20">
                <Palette className="w-5 h-5 text-[#C4855A]" />
              </div>
              <h1 className="text-4xl tracking-tight">Theme Settings</h1>
            </div>
            <p className="text-[#5C6474]">Customize severity colors and UI palette from one place</p>
          </div>

          <div className="flex items-center gap-3">
            <motion.button
              onClick={handleReset}
              whileTap={{ scale: 0.96 }}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-[#7A4832]/20 bg-[#060D1A]/60 hover:bg-[#060D1A]/90 transition-colors text-[#5C6474] hover:text-[#E2DED8]"
            >
              <RotateCcw className="w-4 h-4" />
              <span className="text-sm">Reset</span>
            </motion.button>

            <motion.button
              onClick={handleSave}
              whileTap={{ scale: 0.96 }}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl border transition-colors text-sm"
              style={{
                background: saved
                  ? 'linear-gradient(135deg, #1a4a2e, #1a4a2e)'
                  : 'linear-gradient(135deg, rgba(122,72,50,0.3), rgba(122,72,50,0.15))',
                borderColor: saved ? '#2d6b43' : 'rgba(122,72,50,0.3)',
                color: saved ? '#4ade80' : '#C4855A',
              }}
            >
              {saved ? <Check className="w-4 h-4" /> : null}
              <span>{saved ? 'Applied!' : 'Apply Theme'}</span>
            </motion.button>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Severity Colors */}
          <GlassCard delay={0.1}>
            <h2 className="text-xl mb-1">Severity Colors</h2>
            <p className="text-sm text-[#5C6474] mb-6">
              Used across alerts, badges, risk bars, and charts
            </p>
            <div className="space-y-3">
              <ColorSwatch
                label="Critical"
                value={colors.severity.critical}
                onChange={(v) => updateSeverity('critical', v)}
                description="Highest severity alerts"
              />
              <ColorSwatch
                label="High"
                value={colors.severity.high}
                onChange={(v) => updateSeverity('high', v)}
                description="High risk detections"
              />
              <ColorSwatch
                label="Medium"
                value={colors.severity.medium}
                onChange={(v) => updateSeverity('medium', v)}
                description="Moderate severity events"
              />
              <ColorSwatch
                label="Low"
                value={colors.severity.low}
                onChange={(v) => updateSeverity('low', v)}
                description="Low priority observations"
              />
            </div>
          </GlassCard>

          {/* Right column */}
          <div className="space-y-6">
            {/* Accent Color */}
            <GlassCard delay={0.15}>
              <h2 className="text-xl mb-1">Accent Color</h2>
              <p className="text-sm text-[#5C6474] mb-4">
                Nav highlights, borders, icon tints
              </p>
              <ColorSwatch
                label="Accent / Brand"
                value={colors.accent}
                onChange={updateAccent}
                description="Primary brand accent"
              />
            </GlassCard>

            {/* Live Preview */}
            <GlassCard delay={0.2}>
              <h2 className="text-xl mb-1">Live Preview</h2>
              <p className="text-sm text-[#5C6474] mb-4">
                How severity badges and bars look with current colors
              </p>
              <SeverityPreview colors={colors} />
            </GlassCard>

            {/* Palette Reference */}
            <GlassCard delay={0.25}>
              <h2 className="text-xl mb-3">Current Palette</h2>
              <div className="flex gap-2 flex-wrap">
                {[
                  { label: 'Critical', color: colors.severity.critical },
                  { label: 'High', color: colors.severity.high },
                  { label: 'Medium', color: colors.severity.medium },
                  { label: 'Low', color: colors.severity.low },
                  { label: 'Accent', color: colors.accent },
                ].map((item) => (
                  <div key={item.label} className="flex flex-col items-center gap-1.5">
                    <div
                      className="w-10 h-10 rounded-lg shadow-md border border-white/10"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-xs text-[#5C6474]">{item.label}</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          </div>
        </div>

        {/* Default Values Reference */}
        <GlassCard delay={0.3} className="mt-6">
          <h2 className="text-xl mb-3">Default Values</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: 'Critical (Red)', color: defaultTheme.severity.critical },
              { label: 'High (Orange)', color: defaultTheme.severity.high },
              { label: 'Medium (Yellow)', color: defaultTheme.severity.medium },
              { label: 'Low (Blue)', color: defaultTheme.severity.low },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-3 p-3 rounded-lg bg-[#040A18]/60 border border-[#7A4832]/10">
                <div className="w-6 h-6 rounded-md flex-shrink-0" style={{ backgroundColor: item.color }} />
                <div>
                  <p className="text-xs text-[#E2DED8]">{item.label}</p>
                  <code className="text-xs font-mono text-[#5C6474]">{item.color}</code>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
