import { useState, useEffect, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation, useNavigate, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import Home from "@/pages/Home";
import Courses from "@/pages/Courses";
import CourseDetail from "@/pages/CourseDetail";
import Dashboard from "@/pages/Dashboard";
import About from "@/pages/About";
import Contact from "@/pages/Contact";
import Pricing from "@/pages/Pricing";
import AuthCallback from "@/pages/AuthCallback";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const AuthContext = createContext(null);
export { API, BACKEND_URL };

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = async () => {
    try {
      const res = await axios.get(`${API}/auth/me`, { withCredentials: true });
      setUser(res.data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { checkAuth(); }, []);

  // Hide injected platform badges
  useEffect(() => {
    const hideInterval = setInterval(() => {
      document.querySelectorAll('a[href*="emergentagent"], div[class*="emergent"]').forEach(el => {
        if (!el.closest('[data-testid="navbar"]')) el.style.display = 'none';
      });
    }, 500);
    return () => clearInterval(hideInterval);
  }, []);

  const logout = async () => {
    await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, loading, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <div className="min-h-screen bg-beige flex items-center justify-center"><div className="w-8 h-8 border-2 border-keen-black border-t-transparent rounded-full animate-spin" /></div>;
  if (!user) return <Navigate to="/" state={{ from: location, needsAuth: true }} replace />;
  return children;
}

function AppRouter() {
  const location = useLocation();
  // Detect session_id synchronously before routes render
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/courses" element={<Courses />} />
        <Route path="/courses/:slug" element={<CourseDetail />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      </Routes>
      <Footer />
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRouter />
        <Toaster position="bottom-right" />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
