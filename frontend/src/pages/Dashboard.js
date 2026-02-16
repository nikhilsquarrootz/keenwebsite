import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { BookOpen, Calendar, ArrowRight, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import axios from "axios";
import { API, useAuth } from "@/App";

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { type: "spring", stiffness: 100, damping: 20 }
};

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/enrollments`, { withCredentials: true })
      .then(r => { setEnrollments(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-beige pt-28 pb-16 px-6" data-testid="dashboard-page">
      <div className="max-w-5xl mx-auto">
        {/* Profile Header */}
        <motion.div {...fadeUp} className="glass-card rounded-3xl p-8 mb-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            {user?.picture ? (
              <img src={user.picture} alt="" className="w-16 h-16 rounded-2xl object-cover" />
            ) : (
              <div className="w-16 h-16 rounded-2xl bg-keen-black text-white flex items-center justify-center text-2xl font-heading font-bold">
                {user?.name?.[0]}
              </div>
            )}
            <div className="flex-1">
              <h1 className="font-heading font-extrabold text-2xl md:text-3xl text-keen-black tracking-tight" data-testid="dashboard-username">
                Welcome back, {user?.name?.split(' ')[0]}
              </h1>
              <p className="text-sm text-keen-tertiary mt-1">{user?.email}</p>
            </div>
            <Button onClick={logout} variant="ghost" className="rounded-full border border-keen-black/10 text-keen-secondary hover:text-keen-error hover:border-keen-error/20" data-testid="dashboard-logout">
              <LogOut size={16} className="mr-2" /> Sign Out
            </Button>
          </div>
        </motion.div>

        {/* Enrolled Courses */}
        <motion.div {...fadeUp}>
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-heading font-bold text-xl text-keen-black tracking-tight">
              My Courses ({enrollments.length})
            </h2>
            <Link to="/courses">
              <Button variant="ghost" className="rounded-full text-sm text-keen-secondary hover:text-keen-black" data-testid="browse-more-courses">
                Browse More <ArrowRight size={14} className="ml-1" />
              </Button>
            </Link>
          </div>

          {loading ? (
            <div className="flex justify-center py-20">
              <div className="w-8 h-8 border-2 border-keen-black border-t-transparent rounded-full animate-spin" />
            </div>
          ) : enrollments.length === 0 ? (
            <div className="glass-card rounded-3xl p-12 text-center" data-testid="no-enrollments">
              <BookOpen size={48} className="mx-auto mb-4 text-keen-tertiary" />
              <h3 className="font-heading font-bold text-lg text-keen-black mb-2">No courses yet</h3>
              <p className="text-sm text-keen-tertiary mb-6">Start your AI journey by enrolling in a course.</p>
              <Link to="/courses">
                <Button className="rounded-full bg-keen-black text-white hover:bg-keen-black/90 px-8 h-11" data-testid="start-learning-btn">
                  Explore Courses
                </Button>
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5" data-testid="enrollments-grid">
              {enrollments.map((enr, i) => (
                <motion.div
                  key={enr.enrollment_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08 }}
                  className="glass-card rounded-3xl overflow-hidden hover:bg-white/60 transition-all duration-300"
                >
                  {enr.course_image && (
                    <div className="aspect-[16/7] overflow-hidden">
                      <img src={enr.course_image} alt={enr.course_title} className="w-full h-full object-cover" />
                    </div>
                  )}
                  <div className="p-6">
                    <Badge className="mb-3 bg-keen-success/10 text-keen-success border-0 text-[10px]">
                      {enr.status === "active" ? "Active" : enr.status}
                    </Badge>
                    <h3 className="font-heading font-bold text-base text-keen-black tracking-tight mb-2">{enr.course_title}</h3>
                    <div className="flex items-center gap-2 text-xs text-keen-tertiary">
                      <Calendar size={12} />
                      <span>Enrolled {new Date(enr.enrolled_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
