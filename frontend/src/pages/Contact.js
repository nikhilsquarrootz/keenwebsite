import { useState } from "react";
import { motion } from "framer-motion";
import { Send, Mail, MapPin, Phone } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import axios from "axios";
import { API } from "@/App";

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { type: "spring", stiffness: 100, damping: 20 }
};

export default function Contact() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [sending, setSending] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.email || !form.message) {
      toast.error("Please fill in all required fields.");
      return;
    }
    setSending(true);
    try {
      await axios.post(`${API}/contact`, form);
      toast.success("Message sent! We'll get back to you soon.");
      setForm({ name: "", email: "", subject: "", message: "" });
    } catch {
      toast.error("Failed to send message. Please try again.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-beige pt-28 pb-16 px-6" data-testid="contact-page">
      <div className="max-w-5xl mx-auto">
        <motion.div {...fadeUp} className="text-center mb-14">
          <h1 className="font-heading font-extrabold text-4xl sm:text-5xl lg:text-6xl text-keen-black tracking-tight text-balance mb-4">
            Get in Touch
          </h1>
          <p className="text-base md:text-lg text-keen-secondary max-w-xl mx-auto">
            Have a question about our courses? Want to partner with KEEN? We'd love to hear from you.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Contact Info */}
          <motion.div {...fadeUp} className="space-y-5">
            {[
              { icon: Mail, label: "Email", value: "hello@keen.ai" },
              { icon: MapPin, label: "Office", value: "Bengaluru, India" },
              { icon: Phone, label: "Phone", value: "+91 80 1234 5678" },
            ].map(item => (
              <div key={item.label} className="glass-card rounded-2xl p-5 flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-keen-black/5 flex items-center justify-center flex-shrink-0">
                  <item.icon size={18} className="text-keen-black" />
                </div>
                <div>
                  <div className="text-xs text-keen-tertiary">{item.label}</div>
                  <div className="text-sm font-medium text-keen-black">{item.value}</div>
                </div>
              </div>
            ))}
          </motion.div>

          {/* Contact Form */}
          <motion.div {...fadeUp} className="md:col-span-2">
            <form onSubmit={handleSubmit} className="glass-card rounded-3xl p-8 space-y-5" data-testid="contact-form">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-sm font-medium text-keen-black">Name *</Label>
                  <Input
                    id="name"
                    value={form.name}
                    onChange={e => setForm({ ...form, name: e.target.value })}
                    placeholder="Your name"
                    className="h-12 rounded-xl bg-white/50 border-keen-black/10 focus:border-keen-black/30 focus:ring-0 backdrop-blur-sm"
                    data-testid="contact-name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-medium text-keen-black">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={form.email}
                    onChange={e => setForm({ ...form, email: e.target.value })}
                    placeholder="you@example.com"
                    className="h-12 rounded-xl bg-white/50 border-keen-black/10 focus:border-keen-black/30 focus:ring-0 backdrop-blur-sm"
                    data-testid="contact-email"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="subject" className="text-sm font-medium text-keen-black">Subject</Label>
                <Input
                  id="subject"
                  value={form.subject}
                  onChange={e => setForm({ ...form, subject: e.target.value })}
                  placeholder="What's this about?"
                  className="h-12 rounded-xl bg-white/50 border-keen-black/10 focus:border-keen-black/30 focus:ring-0 backdrop-blur-sm"
                  data-testid="contact-subject"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="message" className="text-sm font-medium text-keen-black">Message *</Label>
                <Textarea
                  id="message"
                  value={form.message}
                  onChange={e => setForm({ ...form, message: e.target.value })}
                  placeholder="Tell us more..."
                  rows={5}
                  className="rounded-xl bg-white/50 border-keen-black/10 focus:border-keen-black/30 focus:ring-0 backdrop-blur-sm resize-none"
                  data-testid="contact-message"
                />
              </div>
              <Button
                type="submit"
                disabled={sending}
                className="rounded-full bg-keen-black text-white hover:bg-keen-black/90 hover:scale-[1.02] transition-all duration-300 shadow-lg hover:shadow-xl px-8 h-12 font-medium"
                data-testid="contact-submit"
              >
                {sending ? "Sending..." : "Send Message"} <Send size={16} className="ml-2" />
              </Button>
            </form>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
