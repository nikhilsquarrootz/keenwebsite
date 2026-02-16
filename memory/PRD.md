# KEEN - AI EdTech Platform PRD

## Original Problem Statement
Build an AI EdTech startup called KEEN that teaches AI-related courses with Apple design + Liquid Glass principles. Features include course catalog, course details, payment portal (Razorpay), Google auth, user dashboard with enrolled courses.

## Architecture
- **Frontend**: React + Tailwind CSS + shadcn/ui + Framer Motion
- **Backend**: FastAPI + MongoDB (Motor async driver)
- **Auth**: Emergent Google OAuth
- **Payments**: Razorpay (demo mode - keys needed)
- **Design**: Apple Liquid Glass + warm beige palette + Plus Jakarta Sans

## User Personas
1. **AI Learner**: Beginners wanting to learn AI/ML fundamentals
2. **Tech Professional**: Upskilling in GenAI, Agentic AI, cloud AI
3. **Enterprise Team Lead**: Looking for team training programs

## Core Requirements
- [x] 10 AI courses with full syllabus, pricing, why-select
- [x] Course catalog with category filtering and search
- [x] Individual course detail pages with accordion syllabus
- [x] Google OAuth authentication (Emergent)
- [x] Payment flow (demo mode, Razorpay-ready)
- [x] User dashboard showing enrolled courses
- [x] Contact form
- [x] Pricing page with 3 tiers + individual course pricing
- [x] About page with mission, values, team
- [x] Apple Liquid Glass design throughout

## What's Been Implemented (Feb 16, 2026)
- Full-stack app with 7 pages: Home, Courses, Course Detail, Dashboard, About, Contact, Pricing
- 10 AI courses seeded (ML, DL, NLP, CV, GenAI, Prompt Engineering, Agentic AI x3, AIOps)
- Emergent Google OAuth with session management
- Demo payment flow (enroll → order → verify → enrollment)
- Floating glass navbar, liquid orb hero, glass cards throughout
- Category filters, search, accordion syllabus
- Protected dashboard route

## Prioritized Backlog
### P0 (Critical)
- Add Razorpay live keys for real payments

### P1 (Important)
- Course progress tracking within enrolled courses
- Email OTP authentication option
- Mobile number authentication option

### P2 (Nice to Have)
- Blog/resource section
- Certificate generation
- Video content integration
- Community forum
