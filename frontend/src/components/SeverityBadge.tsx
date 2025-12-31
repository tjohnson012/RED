interface SeverityBadgeProps {
  severity: string;
  className?: string;
}

const severityColors: Record<string, string> = {
  critical: 'bg-severity-critical text-white',
  high: 'bg-severity-high text-black',
  medium: 'bg-severity-medium text-black',
  low: 'bg-severity-low text-black',
  none: 'bg-failure text-white',
};

export function SeverityBadge({ severity, className = '' }: SeverityBadgeProps) {
  const colorClass = severityColors[severity.toLowerCase()] || severityColors.none;

  return (
    <span
      className={`px-2 py-0.5 text-xs font-medium uppercase tracking-wide ${colorClass} ${className}`}
    >
      {severity}
    </span>
  );
}
