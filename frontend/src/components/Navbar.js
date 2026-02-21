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
        <Link to="/" className="font-heading font-extrabold text-xl tracking-tight text-Squarerootz-black mr-2 md:mr-6" data-testid="nav-logo">
 Squarerootz
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
                  ? 'bg-Squarerootz-black text-white'
                  : 'text-Squarerootz-secondary hover:text-Squarerootz-black hover:bg-black/5'
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
                  <div className="w-7 h-7 rounded-full bg-Squarerootz-black text-white flex items-center justify-center text-xs font-bold">
                    {user.name?.[0]}
                  </div>
                )}
                <span className="hidden md:inline text-sm font-medium text-Squarerootz-black">{user.name?.split(' ')[0]}</span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 glass-card rounded-2xl border-white/40 mt-2">
              <DropdownMenuItem asChild>
                <Link to="/dashboard" className="flex items-center gap-2 cursor-pointer" data-testid="menu-dashboard">
                  <LayoutDashboard size={16} /> Dashboard
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={logout} className="flex items-center gap-2 cursor-pointer text-Squarerootz-error" data-testid="menu-logout">
                <LogOut size={16} /> Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : ""
        //   (
        //   <Button
        //     onClick={handleLogin}
        //     className="rounded-full bg-Squarerootz-black text-white hover:bg-Squarerootz-black/90 hover:scale-105 transition-all duration-300 text-sm px-5 h-9 flex items-center gap-2"
        //     data-testid="nav-sign-in"
        //   >
        //     <svg viewBox="0 0 24 24" width="16" height="16" className="flex-shrink-0"><path fill="#fff" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#fff" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#fff" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#fff" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
        //     Sign in with Google
        //   </Button>
        // )
        }

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
                  ? 'bg-Squarerootz-black text-white'
                  : 'text-Squarerootz-secondary hover:bg-black/5'
              }`}
            >
              {link.label}
            </Link>
          ))}
          {!user && (
            <button
              onClick={handleLogin}
              className="w-full mt-2 px-4 py-3 rounded-2xl bg-Squarerootz-black text-white text-sm font-medium flex items-center justify-center gap-2"
            >
              <svg viewBox="0 0 24 24" width="16" height="16"><path fill="#fff" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#fff" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#fff" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#fff" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
              Sign in with Google
            </button>
          )}
        </div>
      )}
    </nav>
  );
}
