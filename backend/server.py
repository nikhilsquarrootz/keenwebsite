from fastapi import FastAPI, APIRouter, HTTPException, Request, Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import uuid
import httpx
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ---- Models ----
class CourseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    course_id: str
    slug: str
    title: str
    subtitle: str
    description: str
    why_select: List[str]
    syllabus: List[dict]
    duration: str
    level: str
    price: int
    original_price: int
    image_url: str
    category: str
    tags: List[str]
    instructor: dict
    highlights: List[str]

class UserModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: str = ""
    created_at: str

class EnrollmentModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enrollment_id: str
    user_id: str
    course_id: str
    course_title: str
    course_image: str = ""
    enrolled_at: str
    status: str = "active"
    payment_id: str = ""

class ContactInput(BaseModel):
    name: str
    email: str
    subject: str
    message: str

class OrderInput(BaseModel):
    course_id: str

class PaymentVerifyInput(BaseModel):
    order_id: str
    payment_id: str
    signature: str = ""

class SessionInput(BaseModel):
    session_id: str

# ---- Course Data ----
COURSES = [
    {
        "course_id": "ml-101", "slug": "machine-learning",
        "title": "Machine Learning",
        "subtitle": "Master the fundamentals of ML algorithms and techniques",
        "description": "Dive deep into machine learning with hands-on projects. Learn regression, classification, clustering, and ensemble methods with real-world datasets.",
        "why_select": ["Industry-standard curriculum aligned with top tech companies", "20+ real-world projects with enterprise datasets", "Learn scikit-learn, XGBoost, and production ML pipelines", "Capstone project with mentorship from ML engineers"],
        "syllabus": [
            {"module": "Introduction to ML", "topics": ["ML landscape", "Types of learning", "End-to-end ML project"], "weeks": "1-2"},
            {"module": "Regression & Classification", "topics": ["Linear/Logistic regression", "SVMs", "Decision Trees", "Random Forests"], "weeks": "3-5"},
            {"module": "Unsupervised Learning", "topics": ["K-Means", "DBSCAN", "PCA", "Anomaly Detection"], "weeks": "6-7"},
            {"module": "Ensemble Methods", "topics": ["Bagging", "Boosting", "XGBoost", "Hyperparameter Optimization"], "weeks": "8-9"},
            {"module": "Production ML", "topics": ["Model deployment", "MLflow", "Monitoring", "A/B Testing"], "weeks": "10-12"}
        ],
        "duration": "12 weeks", "level": "Intermediate", "price": 149999, "original_price": 249999,
        "image_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=800&auto=format&fit=crop",
        "category": "Core AI", "tags": ["Python", "scikit-learn", "XGBoost", "MLflow"],
        "instructor": {"name": "Dr. Priya Sharma", "role": "Principal ML Engineer", "image": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["95% placement rate", "Industry mentors", "Lifetime access"]
    },
    {
        "course_id": "dl-201", "slug": "deep-learning",
        "title": "Deep Learning",
        "subtitle": "Neural networks from scratch to production",
        "description": "Build neural networks from the ground up. Master CNNs, RNNs, Transformers, and modern architectures with PyTorch.",
        "why_select": ["Build 15+ deep learning models from scratch", "Master PyTorch — the industry's preferred framework", "Understand transformer architecture in depth", "GPU-powered lab environments included"],
        "syllabus": [
            {"module": "Neural Network Foundations", "topics": ["Perceptrons", "Backpropagation", "Activation functions", "Optimizers"], "weeks": "1-2"},
            {"module": "CNNs & Computer Vision", "topics": ["Conv layers", "ResNet", "Object detection", "Image segmentation"], "weeks": "3-5"},
            {"module": "RNNs & Sequence Models", "topics": ["LSTM", "GRU", "Seq2Seq", "Attention mechanisms"], "weeks": "6-7"},
            {"module": "Transformers", "topics": ["Self-attention", "BERT", "GPT architecture", "Vision Transformers"], "weeks": "8-10"},
            {"module": "Advanced Topics", "topics": ["GANs", "Diffusion models", "Neural Architecture Search", "Distillation"], "weeks": "11-14"}
        ],
        "duration": "14 weeks", "level": "Advanced", "price": 199999, "original_price": 349999,
        "image_url": "https://images.unsplash.com/photo-1684394944551-6c55a647337b?q=80&w=800&auto=format&fit=crop",
        "category": "Core AI", "tags": ["PyTorch", "CNNs", "Transformers", "GANs"],
        "instructor": {"name": "Arjun Mehta", "role": "Research Scientist", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["Research-grade curriculum", "GPU labs included", "Paper reading group"]
    },
    {
        "course_id": "nlp-301", "slug": "natural-language-processing",
        "title": "Natural Language Processing",
        "subtitle": "From text processing to large language models",
        "description": "Master NLP from classical techniques to modern LLMs. Build chatbots, search engines, and text analytics systems.",
        "why_select": ["Complete NLP pipeline — from tokenization to fine-tuning LLMs", "Build production chatbots and semantic search systems", "Hands-on with HuggingFace Transformers library", "Exclusive access to NLP research papers club"],
        "syllabus": [
            {"module": "Text Processing", "topics": ["Tokenization", "Stemming/Lemmatization", "TF-IDF", "Word Embeddings"], "weeks": "1-2"},
            {"module": "Classical NLP", "topics": ["NER", "POS Tagging", "Sentiment Analysis", "Topic Modeling"], "weeks": "3-4"},
            {"module": "Deep NLP", "topics": ["Seq2Seq", "Attention", "BERT fine-tuning", "Text generation"], "weeks": "5-7"},
            {"module": "LLMs & Applications", "topics": ["GPT architecture", "Prompt engineering", "RAG systems", "Fine-tuning LLMs"], "weeks": "8-10"}
        ],
        "duration": "10 weeks", "level": "Intermediate", "price": 169999, "original_price": 299999,
        "image_url": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?q=80&w=800&auto=format&fit=crop",
        "category": "Core AI", "tags": ["HuggingFace", "BERT", "GPT", "LLMs"],
        "instructor": {"name": "Dr. Priya Sharma", "role": "Principal ML Engineer", "image": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["LLM-focused", "Industry projects", "Research club access"]
    },
    {
        "course_id": "cv-401", "slug": "computer-vision",
        "title": "Computer Vision",
        "subtitle": "See the world through AI eyes",
        "description": "Master computer vision with cutting-edge techniques. Build object detection, image segmentation, and 3D vision systems.",
        "why_select": ["Comprehensive coverage from classical CV to modern deep learning", "Build 12 vision projects including autonomous driving simulation", "Master OpenCV, YOLO, and Segment Anything Model", "Industry-relevant with real deployment scenarios"],
        "syllabus": [
            {"module": "Image Processing", "topics": ["Filters", "Edge detection", "Feature extraction", "OpenCV"], "weeks": "1-2"},
            {"module": "Object Detection", "topics": ["R-CNN family", "YOLO", "SSD", "Anchor-free detectors"], "weeks": "3-5"},
            {"module": "Image Segmentation", "topics": ["Semantic segmentation", "Instance segmentation", "SAM", "Panoptic"], "weeks": "6-7"},
            {"module": "Advanced Vision", "topics": ["3D Vision", "Video analysis", "Multimodal models", "Deployment"], "weeks": "8-10"}
        ],
        "duration": "10 weeks", "level": "Advanced", "price": 179999, "original_price": 299999,
        "image_url": "https://images.unsplash.com/photo-1561736778-92e52a7769ef?q=80&w=800&auto=format&fit=crop",
        "category": "Core AI", "tags": ["OpenCV", "YOLO", "PyTorch", "3D Vision"],
        "instructor": {"name": "Arjun Mehta", "role": "Research Scientist", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["Autonomous driving project", "SAM & YOLO mastery", "Edge deployment"]
    },
    {
        "course_id": "gai-501", "slug": "generative-ai",
        "title": "Generative AI",
        "subtitle": "Create the future with generative models",
        "description": "Master generative AI from fundamentals to production. Build with OpenAI, Stable Diffusion, and custom models.",
        "why_select": ["Most comprehensive GenAI curriculum in the market", "Build production-grade AI applications with real APIs", "Master both text generation (GPT) and image generation (Diffusion)", "Startup-focused — learn to build AI products"],
        "syllabus": [
            {"module": "GenAI Foundations", "topics": ["Generative vs Discriminative", "VAEs", "GANs", "Diffusion Models"], "weeks": "1-3"},
            {"module": "Large Language Models", "topics": ["GPT architecture", "Fine-tuning", "RLHF", "Constitutional AI"], "weeks": "4-6"},
            {"module": "Image & Multimodal", "topics": ["Stable Diffusion", "DALL-E", "ControlNet", "Multimodal models"], "weeks": "7-9"},
            {"module": "Building AI Products", "topics": ["RAG systems", "AI Agents", "API design", "Scaling & Monitoring"], "weeks": "10-12"}
        ],
        "duration": "12 weeks", "level": "Intermediate", "price": 219999, "original_price": 399999,
        "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?q=80&w=800&auto=format&fit=crop",
        "category": "Generative AI", "tags": ["GPT", "Stable Diffusion", "RAG", "AI Agents"],
        "instructor": {"name": "Kavya Nair", "role": "GenAI Lead", "image": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["Build 8 AI products", "API integration mastery", "Startup mentorship"]
    },
    {
        "course_id": "pe-601", "slug": "prompt-engineering",
        "title": "Prompt Engineering",
        "subtitle": "Master the art of communicating with AI",
        "description": "Learn systematic prompt engineering techniques for production AI systems. From basic prompting to advanced chain-of-thought and agent architectures.",
        "why_select": ["The highest-ROI AI skill in 2025", "Covers all major LLM providers (OpenAI, Anthropic, Google)", "Build production prompt pipelines with evaluation frameworks", "Certificate recognized by 100+ companies"],
        "syllabus": [
            {"module": "Prompt Foundations", "topics": ["Zero-shot", "Few-shot", "System prompts", "Temperature & parameters"], "weeks": "1-2"},
            {"module": "Advanced Techniques", "topics": ["Chain-of-thought", "Tree-of-thought", "ReAct", "Self-consistency"], "weeks": "3-4"},
            {"module": "Production Prompting", "topics": ["Prompt templates", "Output parsing", "Guardrails", "Evaluation"], "weeks": "5-6"},
            {"module": "Prompt Ops", "topics": ["A/B testing prompts", "Version control", "Cost optimization", "Multi-model strategies"], "weeks": "7-8"}
        ],
        "duration": "8 weeks", "level": "Beginner", "price": 109999, "original_price": 179999,
        "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=800&auto=format&fit=crop",
        "category": "Generative AI", "tags": ["GPT-5", "Claude", "Gemini", "LangChain"],
        "instructor": {"name": "Kavya Nair", "role": "GenAI Lead", "image": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["Fastest growing skill", "Multi-LLM coverage", "Industry certificate"]
    },
    {
        "course_id": "aai-701", "slug": "agentic-ai-cloud-agnostic",
        "title": "Agentic AI — Cloud Agnostic",
        "subtitle": "Build autonomous AI agents that work anywhere",
        "description": "Design and build autonomous AI agents that operate across any cloud. Master LangGraph, CrewAI, and custom agent frameworks.",
        "why_select": ["Cloud-agnostic design — deploy agents on AWS, Azure, GCP, or on-premise", "Master 3 major agent frameworks (LangGraph, CrewAI, AutoGen)", "Build multi-agent systems with tool use and memory", "Real enterprise use cases with production patterns"],
        "syllabus": [
            {"module": "Agent Fundamentals", "topics": ["ReAct pattern", "Tool use", "Memory systems", "Planning algorithms"], "weeks": "1-3"},
            {"module": "Framework Deep Dives", "topics": ["LangGraph", "CrewAI", "AutoGen", "Custom frameworks"], "weeks": "4-6"},
            {"module": "Multi-Agent Systems", "topics": ["Agent orchestration", "Communication protocols", "Shared memory", "Conflict resolution"], "weeks": "7-9"},
            {"module": "Production Deployment", "topics": ["Containerization", "Monitoring", "Safety guardrails", "Cost management"], "weeks": "10-12"}
        ],
        "duration": "12 weeks", "level": "Advanced", "price": 249999, "original_price": 449999,
        "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=800&auto=format&fit=crop",
        "category": "Agentic AI", "tags": ["LangGraph", "CrewAI", "AutoGen", "Docker"],
        "instructor": {"name": "Rohan Gupta", "role": "AI Architect", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["Multi-cloud ready", "3 agent frameworks", "Enterprise patterns"]
    },
    {
        "course_id": "aws-801", "slug": "aws-agentic-ai",
        "title": "AWS Agentic AI",
        "subtitle": "Build AI agents on Amazon's cloud ecosystem",
        "description": "Master building and deploying AI agents on AWS. Learn Bedrock, SageMaker, Lambda, and AWS-native agent patterns.",
        "why_select": ["Official AWS-aligned curriculum", "Master Amazon Bedrock agents and knowledge bases", "Build serverless AI pipelines with Lambda & Step Functions", "AWS certification preparation included"],
        "syllabus": [
            {"module": "AWS AI Foundations", "topics": ["Bedrock overview", "SageMaker basics", "IAM for AI", "Cost optimization"], "weeks": "1-2"},
            {"module": "Bedrock Agents", "topics": ["Agent creation", "Knowledge bases", "Action groups", "Guardrails"], "weeks": "3-5"},
            {"module": "Serverless AI Pipelines", "topics": ["Lambda functions", "Step Functions", "EventBridge", "API Gateway"], "weeks": "6-8"},
            {"module": "Production & Scaling", "topics": ["ECS/EKS deployment", "CloudWatch monitoring", "A/B testing", "Multi-region"], "weeks": "9-10"}
        ],
        "duration": "10 weeks", "level": "Intermediate", "price": 229999, "original_price": 399999,
        "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=800&auto=format&fit=crop",
        "category": "Agentic AI", "tags": ["AWS Bedrock", "SageMaker", "Lambda", "CloudFormation"],
        "instructor": {"name": "Rohan Gupta", "role": "AI Architect", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["AWS certified path", "Bedrock mastery", "Serverless focus"]
    },
    {
        "course_id": "az-901", "slug": "azure-agentic-ai",
        "title": "Azure Agentic AI",
        "subtitle": "Enterprise AI agents with Microsoft Azure",
        "description": "Build enterprise-grade AI agents on Azure. Master Azure OpenAI, AI Studio, and enterprise integration patterns.",
        "why_select": ["Enterprise-focused — Azure is #1 in enterprise AI adoption", "Master Azure OpenAI Service and AI Studio", "Learn Copilot Studio for no-code agent building", "Azure AI certification preparation included"],
        "syllabus": [
            {"module": "Azure AI Platform", "topics": ["Azure OpenAI", "AI Studio", "Cognitive Services", "Resource management"], "weeks": "1-2"},
            {"module": "Building Agents", "topics": ["Copilot Studio", "Semantic Kernel", "Function calling", "Plugins"], "weeks": "3-5"},
            {"module": "Enterprise Integration", "topics": ["Power Platform", "Teams integration", "SharePoint", "Dynamics 365"], "weeks": "6-8"},
            {"module": "Security & Governance", "topics": ["Content safety", "RBAC", "Compliance", "Audit logging"], "weeks": "9-10"}
        ],
        "duration": "10 weeks", "level": "Intermediate", "price": 229999, "original_price": 399999,
        "image_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=800&auto=format&fit=crop",
        "category": "Agentic AI", "tags": ["Azure OpenAI", "Copilot Studio", "Semantic Kernel", "Power Platform"],
        "instructor": {"name": "Rohan Gupta", "role": "AI Architect", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["Enterprise #1 choice", "Copilot Studio", "Azure certified"]
    },
    {
        "course_id": "ops-1001", "slug": "aiops",
        "title": "AIOps",
        "subtitle": "Automate IT operations with AI intelligence",
        "description": "Transform IT operations with AI. Build anomaly detection, automated remediation, and intelligent monitoring systems.",
        "why_select": ["Bridge the gap between AI and DevOps — the most in-demand hybrid skill", "Build real anomaly detection and auto-remediation systems", "Master observability tools with AI integration", "Prepare for the future of autonomous IT"],
        "syllabus": [
            {"module": "AIOps Fundamentals", "topics": ["IT operations landscape", "Observability basics", "Data pipeline design", "Metrics/Logs/Traces"], "weeks": "1-2"},
            {"module": "Anomaly Detection", "topics": ["Statistical methods", "ML-based detection", "Time series analysis", "Alert correlation"], "weeks": "3-5"},
            {"module": "Automated Remediation", "topics": ["Runbook automation", "Self-healing systems", "Change intelligence", "Capacity planning"], "weeks": "6-8"},
            {"module": "Enterprise AIOps", "topics": ["Tool integration", "Custom dashboards", "ROI measurement", "Organizational adoption"], "weeks": "9-10"}
        ],
        "duration": "10 weeks", "level": "Intermediate", "price": 199999, "original_price": 349999,
        "image_url": "https://images.unsplash.com/photo-1518432031352-d6fc5c10da5a?q=80&w=800&auto=format&fit=crop",
        "category": "Operations", "tags": ["Prometheus", "Grafana", "Python", "Kubernetes"],
        "instructor": {"name": "Vikram Singh", "role": "SRE Lead", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["DevOps + AI hybrid", "Real monitoring systems", "Auto-remediation"]
    }
]

# ---- Auth Helper ----
async def get_current_user(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    session = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    expires_at = session.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ---- Seed Courses ----
@app.on_event("startup")
async def seed_courses():
    count = await db.courses.count_documents({})
    if count == 0:
        await db.courses.insert_many(COURSES)
        logger.info("Seeded %d courses", len(COURSES))
    else:
        for course in COURSES:
            await db.courses.update_one(
                {"course_id": course["course_id"]},
                {"$set": course},
                upsert=True
            )

# ---- Course Routes ----
@api_router.get("/courses")
async def get_courses(category: str = None):
    query = {}
    if category and category != "all":
        query["category"] = category
    courses = await db.courses.find(query, {"_id": 0}).to_list(100)
    return courses

@api_router.get("/courses/{slug}")
async def get_course(slug: str):
    course = await db.courses.find_one({"slug": slug}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@api_router.get("/categories")
async def get_categories():
    categories = await db.courses.distinct("category")
    return categories

# ---- Auth Routes ----
@api_router.post("/auth/session")
async def exchange_session(body: SessionInput, response: Response):
    # REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    async with httpx.AsyncClient() as http_client:
        resp = await http_client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": body.session_id}
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session")
    data = resp.json()
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    existing = await db.users.find_one({"email": data["email"]}, {"_id": 0})
    if existing:
        user_id = existing["user_id"]
        await db.users.update_one({"email": data["email"]}, {"$set": {"name": data["name"], "picture": data.get("picture", "")}})
    else:
        await db.users.insert_one({
            "user_id": user_id,
            "email": data["email"],
            "name": data["name"],
            "picture": data.get("picture", ""),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    session_token = data.get("session_token", f"st_{uuid.uuid4().hex}")
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    response.set_cookie(
        key="session_token", value=session_token,
        httponly=True, secure=True, samesite="none",
        path="/", max_age=7*24*3600
    )
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return user

@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    return user

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    response.delete_cookie("session_token", path="/", secure=True, samesite="none")
    return {"message": "Logged out"}

# ---- Order / Payment Routes ----
@api_router.post("/orders/create")
async def create_order(body: OrderInput, request: Request):
    user = await get_current_user(request)
    course = await db.courses.find_one({"course_id": body.course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    existing = await db.enrollments.find_one({"user_id": user["user_id"], "course_id": body.course_id}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    order_id = f"order_{uuid.uuid4().hex[:12]}"
    razorpay_key = os.environ.get("RAZORPAY_KEY_ID")
    razorpay_order = None
    if razorpay_key:
        import razorpay
        rz_client = razorpay.Client(auth=(razorpay_key, os.environ.get("RAZORPAY_KEY_SECRET", "")))
        razorpay_order = rz_client.order.create({
            "amount": course["price"] * 100,
            "currency": "INR",
            "payment_capture": 1,
            "notes": {"order_id": order_id, "course_id": body.course_id, "user_id": user["user_id"]}
        })
    await db.orders.insert_one({
        "order_id": order_id,
        "user_id": user["user_id"],
        "course_id": body.course_id,
        "amount": course["price"],
        "status": "created",
        "razorpay_order_id": razorpay_order["id"] if razorpay_order else None,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    return {
        "order_id": order_id,
        "amount": course["price"],
        "currency": "INR",
        "razorpay_order_id": razorpay_order["id"] if razorpay_order else None,
        "razorpay_key": razorpay_key,
        "course": {"title": course["title"], "image_url": course["image_url"]},
        "demo_mode": razorpay_key is None
    }

@api_router.post("/orders/verify")
async def verify_payment(body: PaymentVerifyInput, request: Request):
    user = await get_current_user(request)
    order = await db.orders.find_one({"order_id": body.order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    razorpay_key = os.environ.get("RAZORPAY_KEY_ID")
    if razorpay_key and body.signature:
        import razorpay
        rz_client = razorpay.Client(auth=(razorpay_key, os.environ.get("RAZORPAY_KEY_SECRET", "")))
        try:
            rz_client.utility.verify_payment_signature({
                "razorpay_order_id": order.get("razorpay_order_id", ""),
                "razorpay_payment_id": body.payment_id,
                "razorpay_signature": body.signature
            })
        except Exception:
            raise HTTPException(status_code=400, detail="Payment verification failed")
    await db.orders.update_one({"order_id": body.order_id}, {"$set": {"status": "paid", "payment_id": body.payment_id}})
    course = await db.courses.find_one({"course_id": order["course_id"]}, {"_id": 0})
    enrollment_id = f"enr_{uuid.uuid4().hex[:12]}"
    await db.enrollments.insert_one({
        "enrollment_id": enrollment_id,
        "user_id": user["user_id"],
        "course_id": order["course_id"],
        "course_title": course["title"] if course else "",
        "course_image": course["image_url"] if course else "",
        "enrolled_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "payment_id": body.payment_id
    })
    return {"message": "Payment verified, enrollment created", "enrollment_id": enrollment_id}

# ---- Enrollment Routes ----
@api_router.get("/enrollments")
async def get_enrollments(request: Request):
    user = await get_current_user(request)
    enrollments = await db.enrollments.find({"user_id": user["user_id"]}, {"_id": 0}).to_list(100)
    return enrollments

# ---- Contact Route ----
@api_router.post("/contact")
async def submit_contact(body: ContactInput):
    doc = {
        "contact_id": f"contact_{uuid.uuid4().hex[:12]}",
        "name": body.name,
        "email": body.email,
        "subject": body.subject,
        "message": body.message,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.contacts.insert_one(doc)
    return {"message": "Message sent successfully"}

@api_router.get("/")
async def root():
    return {"message": "KEEN API is running"}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
