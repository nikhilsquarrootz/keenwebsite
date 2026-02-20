import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Clock, BarChart3, Check, Send, User, Mail, Phone, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import axios from "axios";
import { API, useAuth } from "@/App";

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { type: "spring", stiffness: 100, damping: 20 }
};

export default function EnrollForm() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    message: "",
  });

  useEffect(() => {
    axios.get(`${API}/courses/${slug}`)
      .then(r => {
        setCourse(r.data);
        setLoading(false);
        if (user) {
          setForm(f => ({ ...f, full_name: user.name || "", email: user.email || "" }));
        }
      })
      .catch(() => { setLoading(false); navigate('/courses'); });
  }, [slug, navigate, user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.full_name || !form.email || !form.phone) {
      toast.error("Please fill in all required fields.");
      return;
    }
    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append("full_name", form.full_name);
      formData.append("email", form.email);
      formData.append("phone", form.phone);
      formData.append("message", form.message);
      formData.append("course_title", course?.title || "");
      formData.append("course_id", course?.course_id || "");
      formData.append("course_price", `INR ${course?.price?.toLocaleString('en-IN')}` || "");
      formData.append("course_duration", course?.duration || "");
      formData.append("course_level", course?.level || "");

      await fetch("https://formspree.io/f/mpqjrrrn", {
        method: "POST",
        body: formData,
        headers: { "Accept": "application/json" },
      });

      // Also create enrollment in our backend if user is logged in
      if (user) {
        try {
          const orderRes = await axios.post(`${API}/orders/create`, { course_id: course.course_id }, { withCredentials: true });
          const order = orderRes.data;
          await axios.post(`${API}/orders/verify`, {
            order_id: order.order_id,
            payment_id: `enroll_${Date.now()}`,
            signature: ""
          }, { withCredentials: true });
        } catch (err) {
          // Enrollment might fail if already enrolled - that's ok
        }
      }

      setSubmitted(true);
      toast.success("Enrollment request submitted successfully!");
    } catch (err) {
      toast.error("Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-beige flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-Squarerootz-black border-t-transparent rounded-full animate-spin" />
    </div>
  );
  if (!course) return null;

  if (submitted) {
    return (
      <div className="min-h-screen bg-beige pt-28 pb-16 px-6" data-testid="enroll-success">
        <div className="max-w-xl mx-auto text-center">
          <motion.div {...fadeUp} className="glass-card rounded-3xl p-12">
            <div className="w-16 h-16 rounded-full bg-Squarerootz-success/10 flex items-center justify-center mx-auto mb-6">
              <Check size={32} className="text-Squarerootz-success" />
            </div>
            <h1 className="font-heading font-extrabold text-2xl text-Squarerootz-black tracking-tight mb-3">
              Enrollment Request Submitted!
            </h1>
            <p className="text-sm text-Squarerootz-secondary mb-2">
              Thank you for your interest in <strong>{course.title}</strong>.
            </p>
            <p className="text-sm text-Squarerootz-tertiary mb-8">
              Our team will reach out to you shortly with next steps and payment details.
            </p>
            <div className="flex gap-3 justify-center">
              <Link to="/courses">
                <Button variant="ghost" className="rounded-full border border-Squarerootz-black/10 px-6" data-testid="back-to-courses">
                  Browse More Courses
                </Button>
              </Link>
              {user && (
                <Link to="/dashboard">
                  <Button className="rounded-full bg-Squarerootz-black text-white px-6" data-testid="go-to-dashboard">
                    Go to Dashboard
                  </Button>
                </Link>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  const discount = Math.round(((course.original_price - course.price) / course.original_price) * 100);

  return (
    <div className="min-h-screen bg-beige pt-24 pb-16" data-testid="enroll-form-page">
      <div className="max-w-5xl mx-auto px-6 mb-6">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-Squarerootz-secondary hover:text-Squarerootz-black transition-colors text-sm" data-testid="enroll-back-button">
          <ArrowLeft size={16} /> Back to Course
        </button>
      </div>

      <div className="max-w-5xl mx-auto px-6">
        <motion.div {...fadeUp} className="text-center mb-10">
          <h1 className="font-heading font-extrabold text-3xl sm:text-4xl text-Squarerootz-black tracking-tight mb-2">
            Enroll in {course.title}
          </h1>
          <p className="text-base text-Squarerootz-secondary">
            Fill in your details and our team will get you started.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Course Summary Card */}
          <motion.div {...fadeUp} className="lg:col-span-2">
            <div className="glass-card rounded-3xl overflow-hidden sticky top-28" data-testid="enroll-course-summary">
              <div className="aspect-[16/9] overflow-hidden">
                <img src={course.image_url} alt={course.title} className="w-full h-full object-cover" />
              </div>
              <div className="p-6 space-y-4">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="rounded-full text-[10px] border-Squarerootz-black/10 font-mono">{course.category}</Badge>
                  <Badge variant="outline" className="rounded-full text-[10px] border-Squarerootz-black/10">{course.level}</Badge>
                </div>
                <h3 className="font-heading font-bold text-lg text-Squarerootz-black tracking-tight">{course.title}</h3>
                <p className="text-sm text-Squarerootz-tertiary line-clamp-2">{course.subtitle}</p>
                <div className="border-t border-Squarerootz-black/5 pt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-Squarerootz-tertiary">Duration</span>
                    <span className="text-Squarerootz-black font-medium flex items-center gap-1"><Clock size={14} /> {course.duration}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-Squarerootz-tertiary">Level</span>
                    <span className="text-Squarerootz-black font-medium flex items-center gap-1"><BarChart3 size={14} /> {course.level}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-Squarerootz-tertiary">Price</span>
                    <div className="text-right">
                      <span className="font-mono font-bold text-Squarerootz-black">&#8377;{course.price?.toLocaleString('en-IN')}</span>
                      <span className="font-mono text-xs text-Squarerootz-tertiary line-through ml-2">&#8377;{course.original_price?.toLocaleString('en-IN')}</span>
                    </div>
                  </div>
                </div>
                <Badge className="bg-Squarerootz-success/10 text-Squarerootz-success border-0 font-mono text-xs">{discount}% OFF</Badge>
              </div>
            </div>
          </motion.div>

          {/* Enrollment Form */}
          <motion.div {...fadeUp} className="lg:col-span-3">
            <form onSubmit={handleSubmit} className="glass-card rounded-3xl p-8 space-y-5" data-testid="enrollment-form">
              <h2 className="font-heading font-bold text-xl text-Squarerootz-black tracking-tight mb-2">Your Details</h2>
              <p className="text-sm text-Squarerootz-tertiary mb-4">All fields marked with * are required.</p>

              <div className="space-y-2">
                <Label htmlFor="full_name" className="text-sm font-medium text-Squarerootz-black flex items-center gap-1.5">
                  <User size={14} /> Full Name *
                </Label>
                <Input
                  id="full_name"
                  value={form.full_name}
                  onChange={e => setForm({ ...form, full_name: e.target.value })}
                  placeholder="Enter your full name"
                  required
                  className="h-12 rounded-xl bg-white/50 border-Squarerootz-black/10 focus:border-Squarerootz-black/30 focus:ring-0 backdrop-blur-sm"
                  data-testid="enroll-name"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-medium text-Squarerootz-black flex items-center gap-1.5">
                    <Mail size={14} /> Email *
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    value={form.email}
                    onChange={e => setForm({ ...form, email: e.target.value })}
                    placeholder="you@example.com"
                    required
                    className="h-12 rounded-xl bg-white/50 border-Squarerootz-black/10 focus:border-Squarerootz-black/30 focus:ring-0 backdrop-blur-sm"
                    data-testid="enroll-email"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone" className="text-sm font-medium text-Squarerootz-black flex items-center gap-1.5">
                    <Phone size={14} /> Phone *
                  </Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={form.phone}
                    onChange={e => setForm({ ...form, phone: e.target.value })}
                    placeholder="+91 9876543210"
                    required
                    className="h-12 rounded-xl bg-white/50 border-Squarerootz-black/10 focus:border-Squarerootz-black/30 focus:ring-0 backdrop-blur-sm"
                    data-testid="enroll-phone"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="message" className="text-sm font-medium text-Squarerootz-black flex items-center gap-1.5">
                  <MessageSquare size={14} /> Why are you interested in this course?
                </Label>
                <Textarea
                  id="message"
                  value={form.message}
                  onChange={e => setForm({ ...form, message: e.target.value })}
                  placeholder="Tell us about your background and what you hope to achieve..."
                  rows={4}
                  className="rounded-xl bg-white/50 border-Squarerootz-black/10 focus:border-Squarerootz-black/30 focus:ring-0 backdrop-blur-sm resize-none"
                  data-testid="enroll-message"
                />
              </div>

              {/* Hidden course fields for Formspree */}
              <input type="hidden" name="course_title" value={course.title} />
              <input type="hidden" name="course_id" value={course.course_id} />

              <Button
                type="submit"
                disabled={submitting}
                className="w-full rounded-full bg-Squarerootz-black text-white hover:bg-Squarerootz-black/90 hover:scale-[1.01] transition-all duration-300 shadow-lg hover:shadow-xl h-13 text-base font-medium"
                data-testid="enroll-submit-button"
              >
                {submitting ? "Submitting..." : "Submit Enrollment Request"} <Send size={16} className="ml-2" />
              </Button>

              <p className="text-xs text-Squarerootz-tertiary text-center">
                By submitting, you agree to our Terms of Service. Our team will contact you within 24 hours.
              </p>
            </form>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
