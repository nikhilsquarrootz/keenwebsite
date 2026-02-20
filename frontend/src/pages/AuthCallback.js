import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";

export default function AuthCallback() {
  const hasProcessed = useRef(false);
  const navigate = useNavigate();
  const { setUser } = useAuth();

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const hash = window.location.hash;
    const params = new URLSearchParams(hash.replace('#', ''));
    const sessionId = params.get('session_id');

    if (!sessionId) {
      navigate('/', { replace: true });
      return;
    }

    const exchangeSession = async () => {
      try {
        const res = await axios.post(`${API}/auth/session`, { session_id: sessionId }, { withCredentials: true });
        setUser(res.data);
        navigate('/dashboard', { replace: true, state: { user: res.data } });
      } catch (err) {
        console.error('Auth failed:', err);
        navigate('/', { replace: true });
      }
    };

    exchangeSession();
  }, [navigate, setUser]);

  return (
    <div className="min-h-screen bg-beige flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-2 border-Squarerootz-black border-t-transparent rounded-full animate-spin" />
        <p className="text-Squarerootz-secondary font-body text-sm">Signing you in...</p>
      </div>
    </div>
  );
}
