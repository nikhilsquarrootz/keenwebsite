import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Search, Filter } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import axios from "axios";
import { API } from "@/App";

const stagger = {
  initial: { opacity: 0, y: 15 },
  animate: { opacity: 1, y: 0 },
};

export default function Courses() {
  const [courses, setCourses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    axios.get(`${API}/courses`).then(r => setCourses(r.data)).catch(() => {});
    axios.get(`${API}/categories`).then(r => setCategories(r.data)).catch(() => {});
  }, []);

  const filtered = courses.filter(c => {
    const matchCategory = activeCategory === "all" || c.category === activeCategory;
    const matchSearch = !searchQuery || c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.tags?.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchCategory && matchSearch;
  });

  return (
    <div className="min-h-screen bg-beige pt-28 pb-16 px-6" data-testid="courses-page">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div {...stagger} transition={{ type: "spring", stiffness: 100, damping: 20 }} className="mb-12">
          <h1 className="font-heading font-extrabold text-4xl sm:text-5xl lg:text-6xl text-keen-black tracking-tight text-balance mb-4">
            All Courses
          </h1>
          <p className="text-base md:text-lg text-keen-secondary max-w-xl">
            10 comprehensive programs to take your AI career to the next level.
          </p>
        </motion.div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-10" data-testid="course-filters">
          <div className="relative flex-1 max-w-md">
            <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-keen-tertiary" />
            <Input
              placeholder="Search courses or technologies..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-11 h-12 rounded-2xl bg-white/50 border-keen-black/10 focus:border-keen-black/30 focus:ring-0 backdrop-blur-sm"
              data-testid="course-search-input"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setActiveCategory("all")}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                activeCategory === "all" ? "bg-keen-black text-white" : "bg-white/50 border border-keen-black/10 text-keen-secondary hover:bg-white"
              }`}
              data-testid="filter-all"
            >
              All
            </button>
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                  activeCategory === cat ? "bg-keen-black text-white" : "bg-white/50 border border-keen-black/10 text-keen-secondary hover:bg-white"
                }`}
                data-testid={`filter-${cat.toLowerCase().replace(/\s/g, '-')}`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Course Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="course-grid">
          {filtered.map((course, i) => (
            <motion.div
              key={course.course_id}
              {...stagger}
              transition={{ type: "spring", stiffness: 100, damping: 20, delay: i * 0.06 }}
            >
              <Link to={`/courses/${course.slug}`} data-testid={`course-card-${course.slug}`}>
                <div className="group glass-card rounded-3xl overflow-hidden hover:bg-white/60 hover:shadow-2xl hover:shadow-black/5 hover:-translate-y-1 transition-all duration-500 h-full flex flex-col">
                  <div className="aspect-[16/9] overflow-hidden bg-beige-subtle">
                    <img
                      src={course.image_url}
                      alt={course.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                      loading="lazy"
                    />
                  </div>
                  <div className="p-6 flex-1 flex flex-col">
                    <div className="flex items-center gap-2 mb-3">
                      <Badge variant="outline" className="rounded-full text-[10px] border-keen-black/10 bg-beige/80 font-mono">
                        {course.category}
                      </Badge>
                      <Badge variant="outline" className="rounded-full text-[10px] border-keen-black/10 bg-beige/80">
                        {course.level}
                      </Badge>
                    </div>
                    <h3 className="font-heading font-bold text-lg text-keen-black tracking-tight mb-1">{course.title}</h3>
                    <p className="text-sm text-keen-tertiary mb-4 line-clamp-2 flex-1">{course.subtitle}</p>
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {course.tags?.slice(0, 3).map(tag => (
                        <span key={tag} className="text-[10px] font-mono text-keen-secondary bg-keen-black/5 px-2 py-0.5 rounded-full">{tag}</span>
                      ))}
                    </div>
                    <div className="flex items-center justify-between pt-4 border-t border-keen-black/5">
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

        {filtered.length === 0 && (
          <div className="text-center py-20">
            <p className="text-keen-tertiary text-lg">No courses found matching your search.</p>
          </div>
        )}
      </div>
    </div>
  );
}
