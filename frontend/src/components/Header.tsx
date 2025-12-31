interface HeaderProps {
  connected: boolean;
}

export function Header({ connected }: HeaderProps) {
  return (
    <header className="h-14 bg-background border-b border-border flex items-center justify-between px-6">
      <h1 className="text-xl font-bold text-red-primary tracking-tight">RED</h1>
      <div className="flex items-center gap-2 text-sm">
        <span
          className={`w-2 h-2 rounded-full ${
            connected ? 'bg-success' : 'bg-red-primary'
          }`}
        />
        <span className="text-text-secondary">
          {connected ? 'Backend Connected' : 'Disconnected'}
        </span>
      </div>
    </header>
  );
}
