// architect_frontend/src/components/Navbar.tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();
  const navItems = [
    { name: 'Status', path: '/' },
    { name: 'Generate', path: '/editor' },
  ];

  return (
    <nav className="aw-navbar">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="aw-navbar-title">Semantik Architect</span>
        </div>
        <div className="flex gap-1 overflow-x-auto pb-1 sm:pb-0">
          {navItems.map((item) => {
            const isActive = pathname === item.path;
            return (
              <Link key={item.path} href={item.path} className={isActive ? 'aw-nav-link aw-nav-link-active' : 'aw-nav-link'}>
                {item.name}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
