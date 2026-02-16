import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Brain, Zap, Users, Trophy, ChevronRight, GraduationCap, Code2, Layers } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import axios from "axios";
import { API } from "@/App";

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { type: "spring", stiffness: 100, damping: 20 }
};

const stagger = {
  initial: { opacity: 0, y: 15 },
  animate: { opacity: 1, y: 0 },
};

const STATS = [
  { value: "10,000+", label: "Learners", icon: Users },
  { value: "10", label: "AI Courses", icon: Brain },
  { value: "95%", label: "Placement Rate", icon: Trophy },
  { value: "4.9/5", label: "Avg Rating", icon: Zap },
];

const WHY_KEEN = [
  { title: "Industry-Led Curriculum", desc: "Courses designed by engineers at Google, Meta, and Microsoft.", icon: Code2, span: "md:col-span-2" },
  { title: "Hands-On Projects", desc: "Build 50+ real-world AI projects from day one. No theory-only fluff.", icon: Layers, span: "" },
  { title: "Lifetime Access", desc: "Pay once, learn forever. All future updates included.", icon: GraduationCap, span: "" },
  { title: "Career Acceleration", desc: "Dedicated placement support, mock interviews, and resume reviews from FAANG engineers.", icon: Trophy, span: "md:col-span-2" },
];

const TESTIMONIALS = [
  { name: "Ananya R.", role: "ML Engineer at Google", text: "KEEN's ML course was the turning point. The hands-on projects prepared me better than my entire CS degree.", avatar: "A" },
  { name: "Rahul M.", role: "AI Consultant", text: "The Agentic AI course is simply unmatched. I went from zero to building production agents in 12 weeks.", avatar: "R" },
  { name: "Sneha K.", role: "NLP Researcher", text: "The depth of NLP curriculum here rivals graduate programs. And the community is incredible.", avatar: "S" },
];

export default function Home() {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    axios.get(`${API}/courses`).then(r => setCourses(r.data.slice(0, 6))).catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-beige" data-testid="home-page">
      {/* Hero */}
      <section className="min-h-[92vh] flex flex-col items-center justify-center px-6 pt-24 pb-16 relative overflow-hidden" data-testid="hero-section">
        <div className="absolute top-20 right-[10%] w-[300px] h-[300px] md:w-[400px] md:h-[400px] opacity-40 pointer-events-none">
          <div className="liquid-orb w-full h-full" />
        </div>
        <div className="absolute bottom-20 left-[5%] w-[180px] h-[180px] opacity-20 pointer-events-none">
          <div className="liquid-orb w-full h-full" style={{ animationDelay: '-3s' }} />
        </div>

        <motion.div {...fadeUp} className="relative z-10 text-center max-w-4xl">
          <Badge variant="outline" className="mb-6 rounded-full px-4 py-1.5 text-xs font-mono border-keen-black/10 bg-white/50 backdrop-blur-sm">
            The Future of AI Education
          </Badge>
          <h1 className="font-heading font-extrabold text-5xl sm:text-6xl lg:text-8xl text-keen-black tracking-[-0.04em] leading-[0.95] text-balance mb-6">
            Learn AI.<br />Build the Future.
          </h1>
          <p className="text-base md:text-lg text-keen-secondary max-w-2xl mx-auto leading-relaxed mb-4 font-body">
            Master Machine Learning, Deep Learning, Generative AI, and Agentic AI with
            industry-led courses designed for the real world.
          </p>
          <p className="text-sm text-keen-tertiary max-w-xl mx-auto mb-10 font-body italic">
            Founded by top-tier engineers from IIT &amp; AWS with a singular vision — upskill every professional in the era of AI.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/courses">
              <Button className="rounded-full bg-keen-black text-white hover:bg-keen-black/90 hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl px-8 h-12 text-base font-medium" data-testid="hero-explore-btn">
                Explore Courses <ArrowRight className="ml-2" size={18} />
              </Button>
            </Link>
            <Link to="/about">
              <Button variant="ghost" className="rounded-full bg-white/50 border border-keen-black/10 hover:bg-white hover:border-keen-black/20 backdrop-blur-md px-8 h-12 text-base font-medium" data-testid="hero-learn-more-btn">
                Learn More
              </Button>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Stats */}
      <section className="py-16 px-6" data-testid="stats-section">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4">
          {STATS.map((s, i) => (
            <motion.div
              key={s.label}
              {...stagger}
              transition={{ type: "spring", stiffness: 100, damping: 20, delay: i * 0.1 }}
              className="glass-card rounded-3xl p-6 text-center hover:bg-white/60 transition-all duration-300"
            >
              <s.icon size={24} className="mx-auto mb-3 text-keen-black/70" />
              <div className="font-heading font-extrabold text-2xl md:text-3xl text-keen-black tracking-tight">{s.value}</div>
              <div className="text-xs text-keen-tertiary font-medium mt-1">{s.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Featured Courses */}
      <section className="py-20 px-6" data-testid="featured-courses-section">
        <div className="max-w-7xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-14">
            <h2 className="font-heading font-extrabold text-3xl md:text-4xl lg:text-5xl text-keen-black tracking-tight text-balance">
              Featured Courses
            </h2>
            <p className="text-base md:text-lg text-keen-secondary mt-4 max-w-xl mx-auto">
              Industry-leading AI programs designed by engineers who build AI at scale.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course, i) => (
              <motion.div
                key={course.course_id}
                {...stagger}
                transition={{ type: "spring", stiffness: 100, damping: 20, delay: i * 0.08 }}
              >
                <Link to={`/courses/${course.slug}`} data-testid={`course-card-${course.slug}`}>
                  <div className="group glass-card rounded-3xl overflow-hidden hover:bg-white/60 hover:shadow-2xl hover:shadow-black/5 hover:-translate-y-1 transition-all duration-500">
                    <div className="aspect-[16/9] overflow-hidden bg-beige-subtle">
                      <img
                        src={course.image_url}
                        alt={course.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                        loading="lazy"
                      />
                    </div>
                    <div className="p-6">
                      <div className="flex items-center gap-2 mb-3">
                        <Badge variant="outline" className="rounded-full text-[10px] border-keen-black/10 bg-beige/80 font-mono">
                          {course.category}
                        </Badge>
                        <Badge variant="outline" className="rounded-full text-[10px] border-keen-black/10 bg-beige/80">
                          {course.level}
                        </Badge>
                      </div>
                      <h3 className="font-heading font-bold text-lg text-keen-black tracking-tight mb-1">{course.title}</h3>
                      <p className="text-sm text-keen-tertiary mb-4 line-clamp-2">{course.subtitle}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-baseline gap-2">
                          <span className="font-mono font-bold text-keen-black">&#8377;{course.price?.toLocaleString('en-IN')}</span>
                          <span className="font-mono text-xs text-keen-tertiary line-through">&#8377;{course.original_price?.toLocaleString('en-IN')}</span>
                        </div>
                        <span className="text-xs text-keen-secondary font-medium">{course.duration}</span>
                      </div>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>

          <motion.div {...fadeUp} className="text-center mt-12">
            <Link to="/courses">
              <Button variant="ghost" className="rounded-full bg-white/50 border border-keen-black/10 hover:bg-white px-8 h-11 font-medium" data-testid="view-all-courses-btn">
                View All Courses <ChevronRight className="ml-1" size={16} />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Why KEEN Bento Grid */}
      <section className="py-20 px-6 bg-beige-subtle" data-testid="why-keen-section">
        <div className="max-w-5xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-14">
            <h2 className="font-heading font-extrabold text-3xl md:text-4xl lg:text-5xl text-keen-black tracking-tight">
              Why KEEN?
            </h2>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {WHY_KEEN.map((item, i) => (
              <motion.div
                key={item.title}
                {...stagger}
                transition={{ type: "spring", stiffness: 100, damping: 20, delay: i * 0.1 }}
                className={`glass-card rounded-3xl p-8 hover:bg-white/60 hover:-translate-y-1 transition-all duration-500 ${item.span}`}
              >
                <div className="w-12 h-12 rounded-2xl bg-keen-black/5 flex items-center justify-center mb-5">
                  <item.icon size={22} className="text-keen-black" />
                </div>
                <h3 className="font-heading font-bold text-lg text-keen-black tracking-tight mb-2">{item.title}</h3>
                <p className="text-sm text-keen-secondary leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6" data-testid="testimonials-section">
        <div className="max-w-5xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-14">
            <h2 className="font-heading font-extrabold text-3xl md:text-4xl lg:text-5xl text-keen-black tracking-tight">
              What Our Learners Say
            </h2>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t, i) => (
              <motion.div
                key={t.name}
                {...stagger}
                transition={{ type: "spring", stiffness: 100, damping: 20, delay: i * 0.1 }}
                className="glass-card rounded-3xl p-8 hover:bg-white/60 transition-all duration-300"
              >
                <p className="text-sm text-keen-secondary leading-relaxed mb-6">"{t.text}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-keen-black text-white flex items-center justify-center font-heading font-bold text-sm">
                    {t.avatar}
                  </div>
                  <div>
                    <div className="font-heading font-semibold text-sm text-keen-black">{t.name}</div>
                    <div className="text-xs text-keen-tertiary">{t.role}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6" data-testid="cta-section">
        <motion.div {...fadeUp} className="max-w-3xl mx-auto text-center">
          <h2 className="font-heading font-extrabold text-3xl md:text-4xl lg:text-5xl text-keen-black tracking-tight text-balance mb-6">
            Ready to Master AI?
          </h2>
          <p className="text-base text-keen-secondary max-w-lg mx-auto mb-8">
            Join thousands of learners building the future with cutting-edge AI skills.
          </p>
          <Link to="/courses">
            <Button className="rounded-full bg-keen-black text-white hover:bg-keen-black/90 hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl px-10 h-13 text-base font-medium" data-testid="cta-get-started-btn">
              Get Started <ArrowRight className="ml-2" size={18} />
            </Button>
          </Link>
        </motion.div>
      </section>
    </div>
  );
}
