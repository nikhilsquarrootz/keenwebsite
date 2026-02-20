import { Link } from "react-router-dom";

const FOOTER_LINKS = [
  { title: "Courses", links: [
    { href: "/courses", label: "All Courses" },
    { href: "/courses/agentic-ai-cloud-agnostic", label: "Agentic AI - cloud agnostic" },
    { href: "/courses/machine-learning", label: "Machine Learning" },
    { href: "/courses/deep-learning", label: "Deep Learning" },
    { href: "/courses/generative-ai", label: "Generative AI" },
  ]},
  { title: "Company", links: [
    { href: "/about", label: "About Us" },
    { href: "/contact", label: "Contact" },
    { href: "/pricing", label: "Pricing" },
  ]},
  { title: "Resources", links: [
    { href: "#", label: "Blog" },
    { href: "#", label: "Community" },
    { href: "#", label: "Careers" },
  ]},
];

export default function Footer() {
  return (
    <footer className="bg-Squarerootz-black text-white mt-24" data-testid="footer">
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-12">
          <div className="col-span-2 md:col-span-1">
            <h3 className="font-heading font-extrabold text-2xl tracking-tight mb-4">Squarerootz</h3>
            <p className="text-white/60 text-sm leading-relaxed max-w-xs">
              The future of AI education. Learn from industry experts and build the skills that matter.
            </p>
          </div>
          {FOOTER_LINKS.map(section => (
            <div key={section.title}>
              <h4 className="font-heading font-semibold text-sm uppercase tracking-wider text-white/40 mb-4">{section.title}</h4>
              <ul className="space-y-3">
                {section.links.map(link => (
                  <li key={link.label}>
                    <Link to={link.href} className="text-white/60 hover:text-white text-sm transition-colors duration-300">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="border-t border-white/10 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-white/40 text-sm">&copy; 2025 Squarerootz. All rights reserved.</p>
          <div className="flex gap-6">
            <a href="#" className="text-white/40 hover:text-white text-sm transition-colors">Privacy</a>
            <a href="#" className="text-white/40 hover:text-white text-sm transition-colors">Terms</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
