import { motion } from "framer-motion";
import { Target, Eye, Heart, Globe, Users, Lightbulb } from "lucide-react";

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { type: "spring", stiffness: 100, damping: 20 }
};

const TEAM = [
  { name: "Dr. Priya Sharma", role: "Head of ML Programs", image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=200&auto=format&fit=crop" },
  { name: "Arjun Mehta", role: "Head of Deep Learning", image: "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop" },
  { name: "Kavya Nair", role: "Head of GenAI Programs", image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=200&auto=format&fit=crop" },
  { name: "Rohan Gupta", role: "Head of Agentic AI", image: "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop" },
];

const VALUES = [
  { icon: Target, title: "Precision", desc: "Every course module is precision-engineered by practicing engineers, not just academics." },
  { icon: Eye, title: "Clarity", desc: "We believe complex AI concepts can be taught with elegance and simplicity." },
  { icon: Heart, title: "Passion", desc: "We're builders who love AI. That energy flows into every lesson." },
  { icon: Globe, title: "Access", desc: "World-class AI education accessible to everyone, everywhere." },
];

export default function About() {
  return (
    <div className="min-h-screen bg-beige pt-28 pb-16" data-testid="about-page">
      {/* Hero */}
      <section className="px-6 pb-20">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div {...fadeUp}>
            <h1 className="font-heading font-extrabold text-4xl sm:text-5xl lg:text-6xl text-keen-black tracking-tight text-balance mb-6">
              Building the World's Best AI Education
            </h1>
            <p className="text-base md:text-lg text-keen-secondary max-w-2xl mx-auto leading-relaxed">
              KEEN was founded with a singular vision: make world-class AI education accessible to every ambitious learner.
              We believe the next generation of AI engineers shouldn't need a Stanford degree — they need the right curriculum, the right mentors, and relentless hands-on practice.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Mission */}
      <section className="px-6 py-20 bg-beige-subtle">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <motion.div {...fadeUp} className="glass-card rounded-3xl p-10">
              <div className="w-12 h-12 rounded-2xl bg-keen-black/5 flex items-center justify-center mb-6">
                <Lightbulb size={22} className="text-keen-black" />
              </div>
              <h2 className="font-heading font-bold text-2xl text-keen-black tracking-tight mb-4">Our Mission</h2>
              <p className="text-sm text-keen-secondary leading-relaxed">
                To create 100,000 production-ready AI engineers by 2027 through industry-led, project-based learning programs
                that bridge the gap between academic theory and real-world AI systems.
              </p>
            </motion.div>
            <motion.div {...fadeUp} className="glass-card rounded-3xl p-10">
              <div className="w-12 h-12 rounded-2xl bg-keen-black/5 flex items-center justify-center mb-6">
                <Eye size={22} className="text-keen-black" />
              </div>
              <h2 className="font-heading font-bold text-2xl text-keen-black tracking-tight mb-4">Our Vision</h2>
              <p className="text-sm text-keen-secondary leading-relaxed">
                A world where anyone with curiosity and determination can learn, build, and deploy AI systems
                that solve real problems — regardless of their background, location, or credentials.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="px-6 py-20">
        <div className="max-w-5xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-14">
            <h2 className="font-heading font-extrabold text-3xl md:text-4xl text-keen-black tracking-tight">Our Values</h2>
          </motion.div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {VALUES.map((v, i) => (
              <motion.div key={v.title} {...fadeUp} transition={{ delay: i * 0.1 }}
                className="glass-card rounded-3xl p-8 hover:bg-white/60 transition-all duration-300"
              >
                <v.icon size={24} className="text-keen-black mb-4" />
                <h3 className="font-heading font-bold text-lg text-keen-black tracking-tight mb-2">{v.title}</h3>
                <p className="text-sm text-keen-secondary leading-relaxed">{v.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="px-6 py-20 bg-beige-subtle">
        <div className="max-w-5xl mx-auto">
          <motion.div {...fadeUp} className="text-center mb-14">
            <h2 className="font-heading font-extrabold text-3xl md:text-4xl text-keen-black tracking-tight">Meet Our Faculty</h2>
            <p className="text-base text-keen-secondary mt-4">Engineers and researchers from the world's top AI teams.</p>
          </motion.div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
            {TEAM.map((t, i) => (
              <motion.div key={t.name} {...fadeUp} transition={{ delay: i * 0.1 }}
                className="glass-card rounded-3xl p-6 text-center hover:bg-white/60 transition-all duration-300"
              >
                <img src={t.image} alt={t.name} className="w-20 h-20 rounded-2xl object-cover mx-auto mb-4" />
                <h3 className="font-heading font-bold text-sm text-keen-black">{t.name}</h3>
                <p className="text-xs text-keen-tertiary mt-1">{t.role}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Numbers */}
      <section className="px-6 py-20">
        <div className="max-w-4xl mx-auto">
          <motion.div {...fadeUp} className="glass-card rounded-3xl p-12 text-center">
            <h2 className="font-heading font-extrabold text-3xl text-keen-black tracking-tight mb-10">KEEN in Numbers</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {[
                { value: "10,000+", label: "Learners" },
                { value: "10", label: "AI Programs" },
                { value: "95%", label: "Satisfaction Rate" },
                { value: "50+", label: "Industry Mentors" },
              ].map(n => (
                <div key={n.label}>
                  <div className="font-heading font-extrabold text-3xl text-keen-black">{n.value}</div>
                  <div className="text-xs text-keen-tertiary mt-1">{n.label}</div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
