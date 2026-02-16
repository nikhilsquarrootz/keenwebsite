import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "@/App";
import { Menu, X, User, LogOut, LayoutDashboard } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

const NAV_LINKS = [
  { href: "/courses", label: "Courses" },
  { href: "/pricing", label: "Pricing" },
  { href: "/about", label: "About" },
  { href: "/contact", label: "Contact" },
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, logout } = useAuth();
  const location = useLocation();

  const handleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <nav className="fixed top-5 left-1/2 -translate-x-1/2 z-50 w-[92%] md:w-auto" data-testid="navbar">
      <div className="glass-navbar rounded-full px-4 md:px-6 h-14 flex items-center gap-2 md:gap-6">
        <Link to="/" className="font-heading font-extrabold text-xl tracking-tight text-keen-black mr-2 md:mr-6" data-testid="nav-logo">
          KEEN
        </Link>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-1">
          {NAV_LINKS.map(link => (
            <Link
              key={link.href}
              to={link.href}
              data-testid={`nav-link-${link.label.toLowerCase()}`}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                location.pathname === link.href
                  ? 'bg-keen-black text-white'
                  : 'text-keen-secondary hover:text-keen-black hover:bg-black/5'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="flex-1" />

        {/* Auth */}
        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2 rounded-full px-3 py-1.5 hover:bg-black/5 transition-all" data-testid="user-menu-trigger">
                {user.picture ? (
                  <img src={user.picture} alt="" className="w-7 h-7 rounded-full object-cover" />
                ) : (
                  <div className="w-7 h-7 rounded-full bg-keen-black text-white flex items-center justify-center text-xs font-bold">
                    {user.name?.[0]}
                  </div>
                )}
                <span className="hidden md:inline text-sm font-medium text-keen-black">{user.name?.split(' ')[0]}</span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 glass-card rounded-2xl border-white/40 mt-2">
              <DropdownMenuItem asChild>
                <Link to="/dashboard" className="flex items-center gap-2 cursor-pointer" data-testid="menu-dashboard">
                  <LayoutDashboard size={16} /> Dashboard
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={logout} className="flex items-center gap-2 cursor-pointer text-keen-error" data-testid="menu-logout">
                <LogOut size={16} /> Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <Button
            onClick={handleLogin}
            className="rounded-full bg-keen-black text-white hover:bg-keen-black/90 hover:scale-105 transition-all duration-300 text-sm px-5 h-9"
            data-testid="nav-sign-in"
          >
            Sign In
          </Button>
        )}

        {/* Mobile Menu Toggle */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden p-2 rounded-full hover:bg-black/5"
          data-testid="mobile-menu-toggle"
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="md:hidden glass-card rounded-3xl mt-2 p-4 space-y-1" data-testid="mobile-menu">
          {NAV_LINKS.map(link => (
            <Link
              key={link.href}
              to={link.href}
              onClick={() => setMobileOpen(false)}
              className={`block px-4 py-3 rounded-2xl text-sm font-medium transition-all ${
                location.pathname === link.href
                  ? 'bg-keen-black text-white'
                  : 'text-keen-secondary hover:bg-black/5'
              }`}
            >
              {link.label}
            </Link>
          ))}
          {!user && (
            <button
              onClick={handleLogin}
              className="w-full mt-2 px-4 py-3 rounded-2xl bg-keen-black text-white text-sm font-medium"
            >
              Sign In with Google
            </button>
          )}
        </div>
      )}
    </nav>
  );
}
