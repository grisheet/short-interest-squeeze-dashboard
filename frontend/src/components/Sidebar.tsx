import React from 'react';
import { NavLink } from 'react-router-dom';

interface SidebarProps {
  open: boolean;
}

const navItems = [
  { label: 'Dashboard', path: '/', icon: '📊' },
  { label: 'Top Squeeze Candidates', path: '/?sort=score', icon: '🔥' },
  { label: 'High Short Interest', path: '/?sort=shortPercent', icon: '📉' },
  { label: 'High Days to Cover', path: '/?sort=daysToCover', icon: '📅' },
];

const Sidebar: React.FC<SidebarProps> = ({ open }) => {
  if (!open) return null;

  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <span className="text-2xl">📈</span>
          <div>
            <p className="text-sm font-bold text-white">Squeeze Tracker</p>
            <p className="text-xs text-gray-500">v1.0.0</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Navigation</p>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`
            }
          >
            <span>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-800">
        <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-3">
          <p className="text-xs font-semibold text-amber-400 mb-1">Data Disclaimer</p>
          <p className="text-xs text-gray-400 leading-relaxed">
            Short interest data sourced from FINRA and updated twice monthly.
            Days-to-cover = Short Interest / Avg Daily Volume (20-day).
            Data may be 1-14 days stale.
          </p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
