import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Check, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import axios from "axios";
import { API } from "@/App";

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { type: "spring", stiffness: 100, damping: 20 }
};

const PLANS = [
  {
    name: "Individual Course",
    desc: "Perfect for focused, deep learning on a single AI domain",
    price: null,
    period: "per course",
    features: ["Full course access", "Hands-on projects", "Community access", "Certificate of completion", "Industry mentor sessions"],
    highlighted: false,
  },
  {
    name: "Enterprise",
    desc: "Train your entire team with custom AI programs",
    price: "Custom",
    period: "per team",
    features: ["Unlimited team seats", "Custom curriculum", "Dedicated account manager", "Progress dashboards", "API access", "On-site workshops"],
    highlighted: true,
  },
];

export default function Pricing() {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    axios.get(`${API}/courses`).then(r => setCourses(r.data)).catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-beige pt-28 pb-16 px-6" data-testid="pricing-page">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div {...fadeUp} className="text-center mb-16">
          <h1 className="font-heading font-extrabold text-4xl sm:text-5xl lg:text-6xl text-keen-black tracking-tight text-balance mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-base md:text-lg text-keen-secondary max-w-xl mx-auto">
            Invest in your AI career. Pay once, learn forever.
          </p>
        </motion.div>

        {/* Plans */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-24" data-testid="pricing-plans">
          {PLANS.map((plan, i) => (
            <motion.div
              key={plan.name}
              {...fadeUp}
              transition={{ delay: i * 0.1 }}
              className={`rounded-[2rem] p-8 transition-all duration-500 hover:-translate-y-2 ${
                plan.highlighted
                  ? 'bg-keen-black text-white shadow-2xl shadow-black/20'
                  : 'glass-card border border-black/5'
              }`}
              data-testid={`plan-${plan.name.toLowerCase().replace(/\s/g, '-')}`}
            >
              {plan.highlighted && (
                <Badge className="mb-4 bg-white/20 text-white border-0 rounded-full font-mono text-[10px]">Recommended</Badge>
              )}
              <h3 className={`font-heading font-bold text-xl tracking-tight mb-2 ${plan.highlighted ? 'text-white' : 'text-keen-black'}`}>
                {plan.name}
              </h3>
              <p className={`text-sm mb-6 ${plan.highlighted ? 'text-white/60' : 'text-keen-tertiary'}`}>{plan.desc}</p>
              {plan.price && (
                <div className="mb-6">
                  <span className={`font-heading font-extrabold text-3xl ${plan.highlighted ? 'text-white' : 'text-keen-black'}`}>
                    {plan.price}
                  </span>
                  <span className={`text-sm ml-2 ${plan.highlighted ? 'text-white/40' : 'text-keen-tertiary'}`}>/{plan.period}</span>
                </div>
              )}
              {!plan.price && (
                <div className="mb-6">
                  <span className={`font-heading font-bold text-lg ${plan.highlighted ? 'text-white' : 'text-keen-black'}`}>
                    See course pricing below
                  </span>
                </div>
              )}
              <ul className="space-y-3 mb-8">
                {plan.features.map(f => (
                  <li key={f} className="flex items-center gap-2">
                    <Check size={14} className={plan.highlighted ? 'text-white/60' : 'text-keen-success'} />
                    <span className={`text-sm ${plan.highlighted ? 'text-white/80' : 'text-keen-secondary'}`}>{f}</span>
                  </li>
                ))}
              </ul>
              <Link to={plan.price === "Custom" ? "/contact" : "/courses"}>
                <Button
                  className={`w-full rounded-full h-11 font-medium transition-all duration-300 ${
                    plan.highlighted
                      ? 'bg-white text-keen-black hover:bg-white/90 hover:scale-[1.02]'
                      : 'bg-keen-black text-white hover:bg-keen-black/90 hover:scale-[1.02]'
                  }`}
                  data-testid={`plan-cta-${plan.name.toLowerCase().replace(/\s/g, '-')}`}
                >
                  {plan.price === "Custom" ? "Contact Us" : "Browse Courses"} <ArrowRight size={14} className="ml-2" />
                </Button>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Individual Course Pricing */}
        <motion.div {...fadeUp}>
          <h2 className="font-heading font-extrabold text-2xl md:text-3xl text-keen-black tracking-tight text-center mb-10">
            Individual Course Pricing
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full" data-testid="course-pricing-table">
              <thead>
                <tr className="border-b border-keen-black/10">
                  <th className="text-left py-4 px-4 font-heading font-semibold text-sm text-keen-black">Course</th>
                  <th className="text-left py-4 px-4 font-heading font-semibold text-sm text-keen-black hidden md:table-cell">Duration</th>
                  <th className="text-left py-4 px-4 font-heading font-semibold text-sm text-keen-black hidden md:table-cell">Level</th>
                  <th className="text-right py-4 px-4 font-heading font-semibold text-sm text-keen-black">Price</th>
                  <th className="text-right py-4 px-4"></th>
                </tr>
              </thead>
              <tbody>
                {courses.map(course => (
                  <tr key={course.course_id} className="border-b border-keen-black/5 hover:bg-white/30 transition-colors">
                    <td className="py-4 px-4">
                      <div className="font-heading font-semibold text-sm text-keen-black">{course.title}</div>
                      <div className="text-xs text-keen-tertiary mt-0.5 md:hidden">{course.duration} · {course.level}</div>
                    </td>
                    <td className="py-4 px-4 text-sm text-keen-secondary hidden md:table-cell">{course.duration}</td>
                    <td className="py-4 px-4 hidden md:table-cell">
                      <Badge variant="outline" className="rounded-full text-[10px] border-keen-black/10">{course.level}</Badge>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <span className="font-mono font-bold text-sm text-keen-black">₹{course.price?.toLocaleString('en-IN')}</span>
                      <span className="font-mono text-xs text-keen-tertiary line-through ml-2">₹{course.original_price?.toLocaleString('en-IN')}</span>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <Link to={`/courses/${course.slug}`}>
                        <Button variant="ghost" size="sm" className="rounded-full text-xs text-keen-secondary hover:text-keen-black">
                          View <ArrowRight size={12} className="ml-1" />
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
