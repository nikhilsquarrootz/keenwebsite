# Squarerootz - AI EdTech Platform PRD

## Original Problem Statement
Build an AI EdTech startup called Squarerootz that teaches AI-related courses with Apple design + Liquid Glass principles.

## Architecture
- **Frontend**: React + Tailwind CSS + shadcn/ui + Framer Motion
- **Backend**: FastAPI + MongoDB (Motor async driver)
- **Auth**: Emergent Google OAuth ("Sign in with Google")
- **Enrollment**: Formspree form submission (https://formspree.io/f/mpqjrrrn)
- **Design**: Apple Liquid Glass + warm beige palette + Plus Jakarta Sans

## What's Been Implemented
### Phase 1 (Feb 16, 2026)
- 10 AI courses with full syllabus, pricing (₹1-3L range), why-select
- Course catalog with category filtering and search
- Individual course detail pages with accordion syllabus
- Google OAuth authentication (Emergent)
- Demo payment flow
- 7 pages: Home, Courses, Course Detail, Dashboard, About, Contact, Pricing
- Apple Liquid Glass design throughout

### Phase 2 (Feb 16, 2026)
- Fixed content loading speed (animate instead of whileInView)
- Hidden "Made with Emergent" badge
- Updated pricing to 2 plans: Individual + Enterprise (removed Pro Bundle)
- Increased prices to ₹1-3 lakh range
- Added IIT & AWS founder story to Home + About pages
- Simplified faculty section to Head Faculty + "+30 others"

### Phase 3 (Feb 16, 2026)
- Updated course images (AIOps, AWS, Azure, Agentic AI, Deep Learning)
- Changed login to "Sign in with Google" with Google icon
- Created enrollment form page (/enroll/:slug) with Formspree integration
- Enrollment collects: Name, Email, Phone, Message + Course details
- Removed Razorpay payment flow in favor of enrollment form

## Prioritized Backlog
### P0 - Email/phone OTP auth, Razorpay payment when ready
### P1 - Course progress tracking, Video content integration
### P2 - Blog, Certificate generation, Community forum
