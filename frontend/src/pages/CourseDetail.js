import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Clock, BarChart3, Check, ChevronDown, ChevronUp, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { toast } from "sonner";
import axios from "axios";
import { API, useAuth } from "@/App";

const fadeUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { type: "spring", stiffness: 100, damping: 20 }
};

export default function CourseDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);

  useEffect(() => {
    axios.get(`${API}/courses/${slug}`)
      .then(r => { setCourse(r.data); setLoading(false); })
      .catch(() => { setLoading(false); navigate('/courses'); });
  }, [slug, navigate]);

  const handleEnroll = async () => {
    if (!user) {
      // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
      const redirectUrl = window.location.origin + '/dashboard';
      window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
      return;
    }

    setEnrolling(true);
    try {
      const orderRes = await axios.post(`${API}/orders/create`, { course_id: course.course_id }, { withCredentials: true });
      const order = orderRes.data;

      if (order.demo_mode) {
        // Demo mode - simulate payment
        const paymentId = `demo_pay_${Date.now()}`;
        await axios.post(`${API}/orders/verify`, {
          order_id: order.order_id,
          payment_id: paymentId,
          signature: ""
        }, { withCredentials: true });
        toast.success("Enrolled successfully!");
        navigate('/dashboard');
      } else {
        // Razorpay mode
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.onload = () => {
          const options = {
            key: order.razorpay_key,
            amount: order.amount * 100,
            currency: order.currency,
            name: "KEEN",
            description: order.course?.title || "Course Purchase",
            order_id: order.razorpay_order_id,
            handler: async function (response) {
              try {
                await axios.post(`${API}/orders/verify`, {
                  order_id: order.order_id,
                  payment_id: response.razorpay_payment_id,
                  signature: response.razorpay_signature
                }, { withCredentials: true });
                toast.success("Payment successful! You're enrolled.");
                navigate('/dashboard');
              } catch {
                toast.error("Payment verification failed.");
              }
            },
            prefill: { name: user.name, email: user.email },
            theme: { color: "#050505" }
          };
          const rzp = new window.Razorpay(options);
          rzp.open();
        };
        document.body.appendChild(script);
      }
    } catch (err) {
      const msg = err.response?.data?.detail || "Something went wrong";
      toast.error(msg);
    } finally {
      setEnrolling(false);
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-beige flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-keen-black border-t-transparent rounded-full animate-spin" />
    </div>
  );
  if (!course) return null;

  const discount = Math.round(((course.original_price - course.price) / course.original_price) * 100);

  return (
    <div className="min-h-screen bg-beige pt-24 pb-16" data-testid="course-detail-page">
      {/* Back */}
      <div className="max-w-6xl mx-auto px-6 mb-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-keen-secondary hover:text-keen-black transition-colors text-sm" data-testid="back-button">
          <ArrowLeft size={16} /> Back to Courses
        </button>
      </div>

      <div className="max-w-6xl mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Hero */}
            <motion.div {...fadeUp}>
              <div className="aspect-[16/8] rounded-3xl overflow-hidden mb-8">
                <img src={course.image_url} alt={course.title} className="w-full h-full object-cover" />
              </div>
              <div className="flex flex-wrap items-center gap-2 mb-4">
                <Badge variant="outline" className="rounded-full font-mono text-xs border-keen-black/10">{course.category}</Badge>
                <Badge variant="outline" className="rounded-full text-xs border-keen-black/10">{course.level}</Badge>
                <div className="flex items-center gap-1 text-xs text-keen-secondary"><Clock size={14} /> {course.duration}</div>
              </div>
              <h1 className="font-heading font-extrabold text-3xl sm:text-4xl lg:text-5xl text-keen-black tracking-tight text-balance mb-3">
                {course.title}
              </h1>
              <p className="text-base md:text-lg text-keen-secondary leading-relaxed">{course.description}</p>
            </motion.div>

            {/* Why Select */}
            <motion.div {...fadeUp} className="glass-card rounded-3xl p-8" data-testid="why-select-section">
              <h2 className="font-heading font-bold text-xl text-keen-black tracking-tight mb-6">Why Choose This Course</h2>
              <div className="space-y-4">
                {course.why_select?.map((reason, i) => (
                  <div key={i} className="flex gap-3">
                    <div className="w-6 h-6 rounded-full bg-keen-success/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check size={14} className="text-keen-success" />
                    </div>
                    <p className="text-sm text-keen-secondary leading-relaxed">{reason}</p>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Syllabus */}
            <motion.div {...fadeUp} data-testid="syllabus-section">
              <h2 className="font-heading font-bold text-xl text-keen-black tracking-tight mb-6">Curriculum</h2>
              <Accordion type="multiple" className="space-y-3">
                {course.syllabus?.map((mod, i) => (
                  <AccordionItem key={i} value={`module-${i}`} className="glass-card rounded-2xl border-0 px-6 overflow-hidden">
                    <AccordionTrigger className="py-5 hover:no-underline">
                      <div className="flex items-center gap-3 text-left">
                        <span className="font-mono text-xs text-keen-tertiary bg-keen-black/5 px-2 py-1 rounded-lg">W{mod.weeks}</span>
                        <span className="font-heading font-semibold text-sm text-keen-black">{mod.module}</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pb-5">
                      <div className="flex flex-wrap gap-2 pl-14">
                        {mod.topics?.map(topic => (
                          <span key={topic} className="text-xs bg-beige/80 border border-keen-black/5 text-keen-secondary px-3 py-1.5 rounded-full">{topic}</span>
                        ))}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </motion.div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2" data-testid="course-tags">
              {course.tags?.map(tag => (
                <span key={tag} className="text-xs font-mono text-keen-secondary bg-keen-black/5 px-3 py-1.5 rounded-full">{tag}</span>
              ))}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-28 space-y-6">
              {/* Pricing Card */}
              <motion.div {...fadeUp} className="glass-card rounded-3xl p-8" data-testid="pricing-card">
                <div className="mb-6">
                  <div className="flex items-baseline gap-3 mb-1">
                    <span className="font-heading font-extrabold text-3xl text-keen-black">&#8377;{course.price?.toLocaleString('en-IN')}</span>
                    <span className="font-mono text-sm text-keen-tertiary line-through">&#8377;{course.original_price?.toLocaleString('en-IN')}</span>
                  </div>
                  <Badge className="bg-keen-success/10 text-keen-success border-0 font-mono text-xs">{discount}% OFF</Badge>
                </div>

                <Button
                  onClick={handleEnroll}
                  disabled={enrolling}
                  className="w-full rounded-full bg-keen-black text-white hover:bg-keen-black/90 hover:scale-[1.02] transition-all duration-300 shadow-lg hover:shadow-xl h-12 text-base font-medium mb-4"
                  data-testid="enroll-button"
                >
                  {enrolling ? "Processing..." : user ? "Enroll Now" : "Sign In to Enroll"}
                </Button>

                <div className="space-y-3 text-sm text-keen-secondary">
                  {course.highlights?.map((h, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <ShieldCheck size={14} className="text-keen-success" />
                      <span>{h}</span>
                    </div>
                  ))}
                </div>
              </motion.div>

              {/* Instructor */}
              <motion.div {...fadeUp} className="glass-card rounded-3xl p-6" data-testid="instructor-card">
                <h3 className="font-heading font-bold text-sm text-keen-black mb-4">Your Instructor</h3>
                <div className="flex items-center gap-3">
                  <img src={course.instructor?.image} alt={course.instructor?.name} className="w-12 h-12 rounded-full object-cover" />
                  <div>
                    <div className="font-heading font-semibold text-sm text-keen-black">{course.instructor?.name}</div>
                    <div className="text-xs text-keen-tertiary">{course.instructor?.role}</div>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
