import { NavLink, Outlet } from 'react-router-dom';
import { Activity, AlertTriangle, Cloud, DollarSign, PlaySquare, Server } from 'lucide-react';

const links = [
  { to: '/', label: 'Dashboard', icon: Activity },
  { to: '/resources', label: 'Resources', icon: Cloud },
  { to: '/aws/resources', label: 'AWS EC2', icon: Server },
  { to: '/anomalies', label: 'Anomalies', icon: AlertTriangle },
  { to: '/actions', label: 'Actions', icon: PlaySquare },
];

export function Layout() {
  return (
    <div className="min-h-screen text-slate-100">
      <div className="mx-auto flex max-w-7xl gap-6 px-6 py-8">
        <aside className="sticky top-8 h-[calc(100vh-4rem)] w-72 rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-panel backdrop-blur">
          <div className="mb-8 flex items-center gap-3">
            <div className="rounded-2xl bg-blue-500/20 p-3 text-blue-300">
              <DollarSign className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-lg font-semibold">Cost Intelligence</h1>
              <p className="text-sm text-slate-400">Cloud optimization control plane</p>
            </div>
          </div>
          <nav className="space-y-2">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition ${
                    isActive
                      ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/20'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="flex-1">
          <header className="mb-6 rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-panel backdrop-blur">
            <p className="text-sm uppercase tracking-[0.2em] text-blue-300">Executive Cloud FinOps</p>
            <h2 className="mt-2 text-3xl font-semibold">Cloud Cost Intelligence Platform</h2>
            <p className="mt-2 max-w-3xl text-sm text-slate-400">
              Monitor live cloud utilization, estimate spend from real AWS telemetry, detect anomalies, and
              safely operationalize optimization workflows from a single control plane.
            </p>
          </header>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
