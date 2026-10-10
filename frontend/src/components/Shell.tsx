import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, MapPinned, UserRound } from "lucide-react";

const links = [
  { to: "/", label: "Ride", icon: UserRound, end: true },
  { to: "/operator", label: "Operate", icon: LayoutDashboard, end: false },
  { to: "/compare", label: "Compare", icon: MapPinned, end: false },
];

export function Shell() {
  return (
    <div className="min-h-screen bg-canvas">
      <nav className="sticky top-0 z-10 border-b border-line/80 bg-canvas/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-[1080px] items-center justify-between px-6 py-4">
          <p className="text-[17px] font-semibold tracking-tight text-ink">MetroSync</p>
          <div className="flex gap-1">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-full px-3 py-2 text-[14px] transition-colors duration-200 ${
                    isActive ? "bg-white text-ink shadow-card" : "text-mute"
                  }`
                }
              >
                <link.icon size={16} strokeWidth={1.75} />
                {link.label}
              </NavLink>
            ))}
          </div>
        </div>
      </nav>
      <Outlet />
    </div>
  );
}
