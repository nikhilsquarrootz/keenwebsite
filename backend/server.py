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
COURSES = [    {
        "course_id": "aws-101", "slug": "aws-agentic-ai",
        "title": "AWS Agentic AI",
        "subtitle": "Build production-grade AI agents on Amazon's cloud — from Bedrock basics to multi-agent orchestration",
        "description": "The complete 10-week program to master AI agent development on AWS. Learn to build, deploy, and scale autonomous agents using Amazon Bedrock's fully managed agent framework — including the new multi-agent collaboration (GA), inline agents, knowledge bases with guardrails, and serverless orchestration with Step Functions. This course prepares you for the AWS Certified Generative AI Developer certification while giving you hands-on experience with real enterprise patterns. Graduate with production-ready agents deployed on AWS infrastructure.",
        "why_select": [
            "AWS Certified Generative AI Developer aligned — covers the exam domains with hands-on depth",
            "Multi-agent collaboration mastery — supervisor agents, inline agents, and the new routing modes (GA 2025)",
            "Serverless-first architecture — Lambda, Step Functions, EventBridge for cost-efficient, scalable agents",
            "Enterprise security patterns — IAM least privilege, KMS encryption, VPC networking, Bedrock Guardrails",
            "Production observability — Lambda Powertools, X-Ray tracing, CloudWatch dashboards for agent debugging",
            "Real AWS costs, real optimization — learn to manage Bedrock pricing, token budgets, and caching strategies"
        ],
        "syllabus": [
            {
                "module": "AWS AI Platform Foundations",
                "weeks": "1-2",
                "topics": [
                    "AWS AI/ML service landscape — Bedrock vs SageMaker, when to use what",
                    "Amazon Bedrock deep dive — model selection (Claude, Llama, Mistral, Titan), pricing models",
                    "IAM for AI workloads — least privilege policies, service roles, cross-account access",
                    "Setting up your development environment — AWS CLI, Boto3, CDK for infrastructure",
                    "First Bedrock API calls — text generation, embeddings, model parameters",
                    "Cost fundamentals — on-demand vs provisioned throughput, token counting",
                    "Hands-on: Build a CLI chatbot using Bedrock with multiple model options"
                ]
            },
            {
                "module": "Bedrock Agents — Core Architecture",
                "weeks": "3-4",
                "topics": [
                    "Bedrock Agents architecture — how agents reason, plan, and execute",
                    "Creating your first agent — instructions, model selection, agent aliases",
                    "Action Groups — connecting agents to Lambda functions for real-world actions",
                    "Lambda function design for agents — request/response schemas, error handling",
                    "Agent session management — maintaining context across turns",
                    "Testing and debugging agents — trace analysis, understanding agent reasoning",
                    "Powertools for AWS Lambda — structured logging, tracing for agent actions",
                    "Hands-on: Customer service agent that checks orders, processes returns, and updates records"
                ]
            },
            {
                "module": "Knowledge Bases & RAG on AWS",
                "weeks": "5-6",
                "topics": [
                    "Knowledge Bases for Amazon Bedrock — architecture and data flow",
                    "Data source configuration — S3, web crawlers, Confluence, SharePoint connectors",
                    "Chunking strategies — fixed size, semantic, hierarchical chunking",
                    "Embedding models — Titan Embeddings, Cohere, choosing the right model",
                    "Vector stores — OpenSearch Serverless, Aurora PostgreSQL with pgvector, Pinecone",
                    "Retrieval configuration — number of results, search types, metadata filtering",
                    "Integrating Knowledge Bases with Agents — grounding responses with enterprise data",
                    "Hands-on: Enterprise documentation agent with S3-based knowledge base"
                ]
            },
            {
                "module": "Guardrails & Enterprise Safety",
                "weeks": "7",
                "topics": [
                    "Amazon Bedrock Guardrails — content filters, denied topics, word filters",
                    "PII detection and redaction — protecting sensitive data automatically",
                    "Custom sensitive information types — regex-based detection for your domain",
                    "Contextual grounding checks — reducing hallucinations with retrieval validation",
                    "Guardrails with Knowledge Bases — integrated safety for RAG pipelines",
                    "Guardrails with Agents — input/output filtering in agent workflows",
                    "Compliance considerations — HIPAA, GDPR, SOC2 patterns on AWS",
                    "Hands-on: Add comprehensive guardrails to your customer service agent"
                ]
            },
            {
                "module": "Multi-Agent Collaboration",
                "weeks": "8",
                "topics": [
                    "Multi-agent architecture on Bedrock — when single agents aren't enough",
                    "Supervisor agent pattern — breaking down requests, delegating, consolidating",
                    "Collaboration modes — supervisor mode vs supervisor with routing mode",
                    "Inline agents — dynamically creating agents at runtime for flexibility",
                    "Associating collaborator agents — up to 10 specialized sub-agents",
                    "Trace and debug console — visualizing multi-agent interactions",
                    "Cost optimization for multi-agent — minimizing token usage across agents",
                    "Hands-on: Travel planning system with flight, hotel, and activity specialist agents"
                ]
            },
            {
                "module": "Serverless AI Orchestration",
                "weeks": "9",
                "topics": [
                    "AWS Step Functions for AI workflows — visual orchestration of complex pipelines",
                    "Step Functions + Bedrock integration — direct API calls, parallelization",
                    "Long-running agent workflows — human approval steps, wait states",
                    "EventBridge for event-driven agents — triggers, schedules, cross-service events",
                    "API Gateway integration — exposing agents as REST/WebSocket APIs",
                    "SQS and SNS patterns — async agent invocation, fan-out architectures",
                    "Error handling and retries — building resilient agent pipelines",
                    "Hands-on: Document processing pipeline with parallel extraction and human review"
                ]
            },
            {
                "module": "Production Deployment & Operations",
                "weeks": "10",
                "topics": [
                    "Infrastructure as Code — CDK and Terraform for Bedrock agents",
                    "CI/CD for agents — testing, versioning, and deploying agent updates",
                    "Observability stack — CloudWatch dashboards, X-Ray traces, custom metrics",
                    "Cost monitoring and optimization — Bedrock pricing, reserved capacity, caching",
                    "Security hardening — VPC endpoints, private networking, encryption at rest",
                    "Multi-region deployment — disaster recovery patterns for agents",
                    "AWS Certified Generative AI Developer exam preparation",
                    "Capstone: Production-ready multi-agent system with full observability and guardrails"
                ]
            }
        ],
        "duration": "10 weeks", "level": "Intermediate", "price": 229999, "original_price": 399999,
        "image_url": "https://images.unsplash.com/photo-1770169272345-9636d5ef2681?q=80&w=800&auto=format&fit=crop",
        "category": "Agentic AI",
        "tags": ["AWS Bedrock", "Bedrock Agents", "Multi-Agent", "Step Functions", "Lambda Powertools", "Knowledge Bases", "Guardrails"],
        "instructor": {"name": "Rohan Gupta", "role": "AI Architect", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop"},
        "highlights": [
            "AWS Generative AI certification aligned",
            "Multi-agent collaboration (GA) — supervisor & inline agents",
            "Enterprise guardrails & security",
            "Serverless-first with Step Functions",
            "Production observability with Lambda Powertools",
            "Real cost optimization strategies"
        ],
        "popular": 1
    },
    {
        "course_id": "ml-801", "slug": "machine-learning",
        "title": "Machine Learning",
        "subtitle": "From algorithms to production — master the complete ML engineering lifecycle for tabular data",
        "description": "The comprehensive 12-week program to become a production-ready Machine Learning Engineer. In 2026, 85% of ML models never make it to production — this course ensures you're in the 15% that do. Master the algorithms that dominate real-world tabular data (XGBoost, LightGBM, CatBoost), build reproducible ML pipelines with MLflow, and deploy models that scale. From mathematical foundations to MLOps best practices, learn what top companies actually need: not just model building, but the entire lifecycle of data preparation, feature engineering, training, deployment, and monitoring.",
        "why_select": [
            "Production-first curriculum — 85% of ML models fail in production; learn the patterns that prevent this",
            "Tabular data mastery — gradient boosting (XGBoost, LightGBM, CatBoost) still beats deep learning on business data",
            "Complete MLOps pipeline — MLflow, feature stores (Feast), CI/CD for ML, and monitoring with Evidently",
            "Explainability built-in — SHAP, LIME, and interpretability techniques now required for enterprise ML",
            "AutoML demystified — understand when to use AutoGluon, Auto-sklearn, and when manual tuning wins",
            "Job-market aligned — covers the exact skills from 2026 ML Engineer job postings ($157K+ median salary)"
        ],
        "syllabus": [
            {
                "module": "ML Foundations & The Production Mindset",
                "weeks": "1-2",
                "topics": [
                    "The 2026 ML landscape — why 85% of models fail in production and how to be in the 15%",
                    "Types of learning — supervised, unsupervised, semi-supervised, self-supervised",
                    "The ML project lifecycle — from problem framing to deployment and monitoring",
                    "Python ML stack — NumPy, Pandas, Matplotlib, Seaborn for data exploration",
                    "Scikit-learn fundamentals — estimators, transformers, pipelines, cross-validation",
                    "Experimental rigor — train/validation/test splits, avoiding data leakage",
                    "Version control for ML — Git, DVC for data versioning",
                    "Hands-on: End-to-end ML project from data exploration to baseline model"
                ]
            },
            {
                "module": "Supervised Learning — Regression & Classification",
                "weeks": "3-4",
                "topics": [
                    "Linear regression — from simple to regularized (Ridge, Lasso, ElasticNet)",
                    "Logistic regression — binary and multiclass, decision boundaries",
                    "The bias-variance tradeoff — understanding underfitting and overfitting",
                    "Decision trees — CART algorithm, pruning, interpretability advantages",
                    "Random forests — bagging, feature importance, out-of-bag error",
                    "Support vector machines — kernels, margin maximization, when to use SVMs",
                    "Model evaluation — accuracy, precision, recall, F1, ROC-AUC, PR curves",
                    "Handling imbalanced data — SMOTE, class weights, threshold tuning",
                    "Hands-on: Credit risk classification with class imbalance handling"
                ]
            },
            {
                "module": "Gradient Boosting — The Production Workhorses",
                "weeks": "5-6",
                "topics": [
                    "Boosting fundamentals — AdaBoost, gradient boosting intuition",
                    "XGBoost deep dive — regularization, tree pruning, handling missing values",
                    "LightGBM — histogram-based learning, GOSS, EFB, memory efficiency",
                    "CatBoost — native categorical handling, ordered boosting, symmetric trees",
                    "When to use which — XGBoost vs LightGBM vs CatBoost decision framework",
                    "Hyperparameter tuning — grid search, random search, Bayesian optimization (Optuna)",
                    "Early stopping and regularization — preventing overfitting in boosting",
                    "GPU acceleration — training large models efficiently",
                    "Hands-on: Kaggle-style competition with XGBoost and LightGBM ensemble"
                ]
            },
            {
                "module": "Feature Engineering & Feature Stores",
                "weeks": "7",
                "topics": [
                    "Why feature engineering matters — often more impactful than model selection",
                    "Numerical features — scaling, binning, polynomial features, log transforms",
                    "Categorical features — encoding strategies (one-hot, target, frequency, embeddings)",
                    "Temporal features — date/time extraction, lag features, rolling statistics",
                    "Text features for tabular — TF-IDF, embeddings as features",
                    "Feature selection — filter, wrapper, embedded methods, SHAP-based selection",
                    "Feature stores with Feast — centralized feature management, training-serving consistency",
                    "Avoiding training-serving skew — why feature stores matter in production",
                    "Hands-on: Build a feature store pipeline with Feast for a real dataset"
                ]
            },
            {
                "module": "Unsupervised Learning & Anomaly Detection",
                "weeks": "8",
                "topics": [
                    "Clustering fundamentals — K-Means, initialization strategies, elbow method",
                    "Density-based clustering — DBSCAN, HDBSCAN for arbitrary cluster shapes",
                    "Hierarchical clustering — agglomerative, dendrograms, linkage methods",
                    "Dimensionality reduction — PCA, t-SNE, UMAP for visualization and preprocessing",
                    "Anomaly detection — Isolation Forest, One-Class SVM, Local Outlier Factor",
                    "Clustering evaluation — silhouette score, Davies-Bouldin, business metrics",
                    "Customer segmentation — real-world application of clustering",
                    "Hands-on: Customer segmentation and anomaly detection for fraud"
                ]
            },
            {
                "module": "Model Explainability & Responsible ML",
                "weeks": "9",
                "topics": [
                    "Why explainability matters — regulatory requirements, trust, debugging",
                    "Feature importance — permutation importance, impurity-based, limitations",
                    "SHAP deep dive — Shapley values, TreeSHAP, force plots, summary plots",
                    "LIME — local surrogate models, when LIME beats SHAP",
                    "Partial dependence plots — understanding feature effects",
                    "Fairness in ML — bias detection, disparate impact, fairness metrics",
                    "Model cards and documentation — responsible ML practices",
                    "Regulatory considerations — GDPR right to explanation, EU AI Act",
                    "Hands-on: Create explainability reports for stakeholder communication"
                ]
            },
            {
                "module": "AutoML & Hyperparameter Optimization",
                "weeks": "10",
                "topics": [
                    "AutoML landscape — AutoGluon, Auto-sklearn, PyCaret, H2O comparison",
                    "AutoGluon deep dive — stacking, ensembling, presets for different use cases",
                    "When AutoML helps vs when manual tuning wins — decision framework",
                    "Bayesian optimization — surrogate models, acquisition functions, Optuna",
                    "Neural architecture search concepts — understanding modern AutoML",
                    "Ensemble methods — stacking, blending, voting for production models",
                    "Model selection strategies — nested cross-validation, holdout sets",
                    "Hands-on: AutoGluon vs manual XGBoost tuning — compare and analyze"
                ]
            },
            {
                "module": "MLOps — From Notebook to Production",
                "weeks": "11",
                "topics": [
                    "MLOps fundamentals — why 72% of enterprises now prioritize automation",
                    "MLflow deep dive — experiment tracking, model registry, model serving",
                    "Reproducibility — environment management, Docker, dependency locking",
                    "CI/CD for ML — testing models, automated retraining pipelines",
                    "Model serving — REST APIs, batch inference, real-time vs batch tradeoffs",
                    "Monitoring and drift detection — data drift, concept drift, Evidently AI",
                    "A/B testing for models — statistical rigor in production experiments",
                    "Cost management — compute optimization, model compression",
                    "Hands-on: Deploy an ML pipeline with MLflow, Docker, and monitoring"
                ]
            },
            {
                "module": "Capstone — Production ML System",
                "weeks": "12",
                "topics": [
                    "Capstone project — end-to-end ML system solving a real business problem",
                    "Data pipeline design — ingestion, validation, feature engineering",
                    "Model development — experimentation, hyperparameter tuning, ensembling",
                    "Explainability implementation — SHAP reports for business stakeholders",
                    "MLOps pipeline — MLflow tracking, model registry, automated deployment",
                    "Monitoring setup — drift detection, alerting, retraining triggers",
                    "Documentation — model cards, API documentation, runbooks",
                    "Portfolio presentation — communicating ML results to technical and non-technical audiences",
                    "Career preparation — ML Engineer interview patterns, system design for ML"
                ]
            }
        ],
        "duration": "12 weeks", "level": "Intermediate", "price": 149999, "original_price": 249999,
        "image_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=800&auto=format&fit=crop",
        "category": "Core AI",
        "tags": ["XGBoost", "LightGBM", "scikit-learn", "MLflow", "Feast", "SHAP", "AutoML", "MLOps"],
        "instructor": {"name": "Mo. Wajahat", "role": "HOD Squarerootz", "image": "/images/wajahat.jpeg"},
        "highlights": [
            "Production-first — learn why 85% of models fail and how to succeed",
            "Gradient boosting mastery — XGBoost, LightGBM, CatBoost",
            "Complete MLOps pipeline with MLflow",
            "Feature stores with Feast",
            "Explainability with SHAP & LIME",
            "AutoML + manual tuning strategies"
        ],
        "popular": 0
    },
    {
        "course_id": "dl-201", "slug": "deep-learning",
        "title": "Deep Learning",
        "subtitle": "From mathematical foundations to production systems — master modern neural architectures with PyTorch",
        "description": "The comprehensive 14-week program to become a production-ready Deep Learning Engineer. Master PyTorch 2.x with torch.compile for optimized training, build CNNs and Vision Transformers (ViT, DINO, CLIP) for computer vision, understand the transformer architecture that powers modern AI, and explore cutting-edge alternatives like Mamba and State Space Models. Learn efficient fine-tuning with LoRA/QLoRA, train diffusion models, and deploy neural networks at scale. This course bridges the gap between understanding algorithms mathematically and shipping them in production.",
        "why_select": [
            "PyTorch 2.x mastery — torch.compile, regional compilation, and production optimization techniques",
            "Modern architectures beyond transformers — Mamba, State Space Models, and hybrid architectures (Jamba)",
            "Vision foundation models — ViT, CLIP, DINO/DINOv2, and their practical applications",
            "Efficient training techniques — LoRA, QLoRA, PEFT for fine-tuning billion-parameter models on consumer GPUs",
            "Diffusion models deep dive — DDPM theory, Stable Diffusion architecture, fine-tuning (DreamBooth, LoRA)",
            "Math-to-code approach — understand the theory, implement from scratch, then use frameworks"
        ],
        "syllabus": [
            {
                "module": "Deep Learning Foundations & PyTorch Mastery",
                "weeks": "1-2",
                "topics": [
                    "The deep learning landscape 2026 — what's changed and what matters",
                    "Neural network fundamentals — perceptrons, activation functions, universal approximation",
                    "Backpropagation — chain rule, computational graphs, gradient flow",
                    "PyTorch fundamentals — tensors, autograd, datasets, dataloaders",
                    "Building neural networks — nn.Module, forward pass, custom layers",
                    "Optimization deep dive — SGD, momentum, Adam, AdamW, learning rate schedules",
                    "Regularization techniques — dropout, batch norm, layer norm, weight decay",
                    "PyTorch 2.x features — torch.compile basics, TorchInductor backend",
                    "Hands-on: Build and train a multi-layer perceptron from scratch, then with PyTorch"
                ]
            },
            {
                "module": "Convolutional Neural Networks",
                "weeks": "3-4",
                "topics": [
                    "Convolution operation — kernels, feature maps, receptive fields",
                    "CNN building blocks — conv layers, pooling, stride, padding",
                    "Classic architectures — LeNet, AlexNet, VGG (understanding the evolution)",
                    "Modern architectures — ResNet (skip connections), DenseNet, EfficientNet",
                    "Transfer learning — pretrained models, feature extraction, fine-tuning strategies",
                    "Data augmentation — transforms, mixup, cutout, AutoAugment",
                    "CNN interpretability — Grad-CAM, feature visualization, saliency maps",
                    "Hands-on: Image classification with transfer learning and Grad-CAM visualization"
                ]
            },
            {
                "module": "Sequence Models — RNNs to Attention",
                "weeks": "5-6",
                "topics": [
                    "Sequential data challenges — variable length, long-range dependencies",
                    "Recurrent Neural Networks — vanilla RNN, hidden states, BPTT",
                    "The vanishing gradient problem — why RNNs struggle with long sequences",
                    "LSTM deep dive — gates, cell state, gradient highways",
                    "GRU — simplified gating, when to use LSTM vs GRU",
                    "Sequence-to-sequence models — encoder-decoder architecture",
                    "Attention mechanism — the breakthrough that changed everything",
                    "Bahdanau vs Luong attention — additive vs multiplicative",
                    "Hands-on: Machine translation with attention-based seq2seq"
                ]
            },
            {
                "module": "Transformers — Architecture Deep Dive",
                "weeks": "7-8",
                "topics": [
                    "Self-attention — queries, keys, values from first principles",
                    "Multi-head attention — why multiple heads help",
                    "Positional encoding — sinusoidal, learned, rotary (RoPE)",
                    "The full transformer — encoder, decoder, cross-attention",
                    "Layer normalization variants — pre-norm vs post-norm, RMSNorm",
                    "Transformer training dynamics — warmup, gradient clipping, mixed precision",
                    "BERT architecture — bidirectional encoding, MLM, NSP objectives",
                    "GPT architecture — causal attention, autoregressive generation",
                    "Efficient attention — Flash Attention, sparse attention, linear attention",
                    "Hands-on: Implement transformer from scratch, then train with HuggingFace"
                ]
            },
            {
                "module": "Vision Transformers & Foundation Models",
                "weeks": "9",
                "topics": [
                    "Vision Transformer (ViT) — patch embeddings, position embeddings, CLS token",
                    "ViT variants — DeiT, Swin Transformer, hybrid architectures",
                    "CLIP — contrastive learning, image-text alignment, zero-shot classification",
                    "DINO and DINOv2 — self-supervised learning, emergent segmentation",
                    "DINOv3 (2025) — Gram anchoring, axial RoPE, 7B parameter models",
                    "Foundation models for vision — when to use ViT vs CNN vs foundation models",
                    "Efficient ViTs — MobileViT, EfficientViT for edge deployment",
                    "Hands-on: Zero-shot classification with CLIP, feature extraction with DINOv2"
                ]
            },
            {
                "module": "Beyond Transformers — Mamba & State Space Models",
                "weeks": "10",
                "topics": [
                    "The quadratic attention problem — why transformers struggle with long sequences",
                    "State Space Models (SSM) — continuous-time systems, discretization",
                    "S4 architecture — structured state spaces, efficient computation",
                    "Mamba — selective state spaces, content-aware filtering",
                    "Mamba-2 — faster implementation, hardware-aware algorithms",
                    "Hybrid architectures — Jamba (Transformer + Mamba + MoE), Griffin",
                    "When to use what — transformers vs SSMs decision framework",
                    "The future of sequence modeling — linear complexity, infinite context",
                    "Hands-on: Implement a simple SSM, compare Mamba vs Transformer on long sequences"
                ]
            },
            {
                "module": "Generative Models — GANs & VAEs",
                "weeks": "11",
                "topics": [
                    "Generative modeling landscape — GANs, VAEs, flows, diffusion",
                    "Variational Autoencoders — ELBO, reparameterization trick, latent spaces",
                    "GAN fundamentals — generator, discriminator, minimax game",
                    "GAN training challenges — mode collapse, training instability",
                    "Modern GANs — DCGAN, StyleGAN, Progressive GAN",
                    "Conditional generation — cGAN, pix2pix, CycleGAN",
                    "GAN evaluation — FID, IS, precision/recall for generative models",
                    "Hands-on: Train a GAN for image generation, explore latent space"
                ]
            },
            {
                "module": "Diffusion Models — Theory to Practice",
                "weeks": "12",
                "topics": [
                    "Diffusion fundamentals — forward process, reverse process, score matching",
                    "DDPM — denoising diffusion probabilistic models, noise schedules",
                    "Score-based models — score matching, Langevin dynamics",
                    "Latent diffusion — why work in latent space, the autoencoder component",
                    "Stable Diffusion architecture — U-Net, cross-attention, CLIP text encoder",
                    "Sampling algorithms — DDIM, DPM-Solver, consistency models",
                    "Guidance — classifier guidance, classifier-free guidance, CFG scale",
                    "Fine-tuning diffusion models — DreamBooth, textual inversion, LoRA for SD",
                    "Hands-on: Train a diffusion model, fine-tune Stable Diffusion with DreamBooth"
                ]
            },
            {
                "module": "Efficient Training & Fine-Tuning",
                "weeks": "13",
                "topics": [
                    "The memory bottleneck — why large models are hard to train",
                    "Mixed precision training — FP16, BF16, loss scaling",
                    "Gradient checkpointing — trading compute for memory",
                    "LoRA deep dive — low-rank adaptation, rank selection, target modules",
                    "QLoRA — 4-bit quantization, NF4, double quantization, paged optimizers",
                    "PEFT landscape — adapters, prefix tuning, prompt tuning comparison",
                    "Distributed training basics — DataParallel, DistributedDataParallel, FSDP",
                    "torch.compile advanced — regional compilation, fullgraph mode, avoiding recompilations",
                    "Hands-on: Fine-tune a 7B LLM with QLoRA on consumer GPU (16GB)"
                ]
            },
            {
                "module": "Production Deep Learning & Capstone",
                "weeks": "14",
                "topics": [
                    "Model optimization for deployment — quantization (INT8, INT4), pruning, distillation",
                    "ONNX export — framework-agnostic model format, runtime optimization",
                    "TensorRT and inference optimization — NVIDIA ecosystem for production",
                    "Serving deep learning models — TorchServe, Triton Inference Server",
                    "Edge deployment — mobile (CoreML, TFLite), embedded (Jetson)",
                    "Monitoring and observability — latency tracking, accuracy monitoring",
                    "Capstone project — end-to-end deep learning system with training and deployment",
                    "Paper reading skills — how to read and implement ML papers",
                    "Career preparation — DL Engineer interview patterns, portfolio presentation"
                ]
            }
        ],
        "duration": "14 weeks", "level": "Advanced", "price": 199999, "original_price": 349999,
        "image_url": "https://images.unsplash.com/photo-1549925245-f20a1bac6454?q=80&w=800&auto=format&fit=crop",
        "category": "Core AI",
        "tags": ["PyTorch", "Transformers", "Vision Transformers", "Mamba", "Diffusion Models", "LoRA", "CLIP", "DINO"],
        "instructor": {"name": "Mo. Wajahat", "role": "HOD Squarerootz", "image": "/images/wajahat.jpeg"},
        "highlights": [
            "PyTorch 2.x with torch.compile optimization",
            "Beyond transformers — Mamba & State Space Models",
            "Vision foundation models — ViT, CLIP, DINO",
            "Diffusion models & Stable Diffusion fine-tuning",
            "Efficient fine-tuning — LoRA, QLoRA, PEFT",
            "Math-to-code — implement from scratch, then scale"
        ],
        "popular": 0
    },
    {
        "course_id": "nlp-301", "slug": "natural-language-processing",
        "title": "Natural Language Processing",
        "subtitle": "From embeddings to production LLM systems with RAG & fine-tuning",
        "description": "Master NLP for the 2026 job market — from classical text processing to LLM fine-tuning, semantic search, and RAG pipelines. Build production-grade NLP systems that employers are actively hiring for: chatbots, document intelligence, entity extraction, and retrieval-augmented generation.",
        "why_select": [
            "Job-market aligned — covers skills commanding $170K+ salaries in 2026",
            "Production focus — semantic search, RAG pipelines, vector databases",
            "Complete fine-tuning mastery — LoRA, QLoRA, DPO, instruction tuning",
            "Open-source stack — HuggingFace, spaCy, ChromaDB, no paid dependencies"
        ],
        "syllabus": [
            {
                "module": "Text Processing & Embeddings Foundations",
                "weeks": "1-2",
                "topics": [
                    "Modern tokenization — BPE, WordPiece, SentencePiece, tiktoken",
                    "Text preprocessing pipelines — cleaning, normalization, language detection",
                    "Classical embeddings — Word2Vec, GloVe, FastText, and their limitations",
                    "Neural embeddings — sentence-transformers, BGE, E5, Nomic embeddings",
                    "Embedding evaluation — similarity metrics, benchmark datasets",
                    "Hands-on: Build semantic similarity engine with sentence-transformers"
                ]
            },
            {
                "module": "Named Entity Recognition & Information Extraction",
                "weeks": "3-4",
                "topics": [
                    "NER architectures — CRF, BiLSTM-CRF, transformer-based NER",
                    "spaCy pipelines — custom NER training, entity rulers, pattern matching",
                    "Zero-shot & few-shot NER with GLiNER and SetFit",
                    "Relation extraction — entity linking, knowledge graph construction",
                    "Document understanding — layout analysis, table extraction, PDF parsing",
                    "Hands-on: Build custom NER for domain-specific entity extraction (legal/medical)"
                ]
            },
            {
                "module": "Text Classification & Sentiment Analysis",
                "weeks": "5-6",
                "topics": [
                    "Classification architectures — BERT, RoBERTa, DeBERTa for classification",
                    "Multi-label and hierarchical classification strategies",
                    "Sentiment analysis — aspect-based sentiment, emotion detection",
                    "Efficient fine-tuning with SetFit for low-data scenarios",
                    "Text classification at scale — distillation, quantization, ONNX export",
                    "Evaluation frameworks — precision/recall tradeoffs, handling imbalanced data",
                    "Hands-on: Build production sentiment analysis API with FastAPI"
                ]
            },
            {
                "module": "Transformer Architectures Deep Dive",
                "weeks": "7-8",
                "topics": [
                    "Attention mechanisms — self-attention, multi-head, flash attention",
                    "Encoder models — BERT, RoBERTa, DeBERTa, ModernBERT",
                    "Decoder models — GPT architecture, causal attention, KV caching",
                    "Encoder-decoder models — T5, BART, mT5 for seq2seq tasks",
                    "Efficient attention — Longformer, BigBird, sparse attention patterns",
                    "Position encoding — absolute, relative, RoPE, ALiBi",
                    "Hands-on: Implement transformer from scratch in PyTorch"
                ]
            },
            {
                "module": "Semantic Search & Vector Databases",
                "weeks": "9-10",
                "topics": [
                    "Vector database landscape — ChromaDB, Qdrant, Milvus, pgvector",
                    "Embedding model selection — accuracy vs latency tradeoffs",
                    "Hybrid search — combining dense vectors with BM25 sparse retrieval",
                    "Re-ranking strategies — cross-encoders, ColBERT, learned sparse",
                    "Graph-enhanced retrieval — knowledge graphs + vector search",
                    "Production architecture — indexing strategies, sharding, caching",
                    "Hands-on: Build production semantic search with ChromaDB + re-ranking"
                ]
            },
            {
                "module": "Retrieval-Augmented Generation (RAG)",
                "weeks": "11-12",
                "topics": [
                    "RAG architectures — naive RAG, advanced RAG, modular RAG",
                    "Chunking strategies — recursive, semantic, sentence-based chunking",
                    "Query transformation — HyDE, query decomposition, step-back prompting",
                    "Context optimization — lost-in-the-middle, compression, relevance filtering",
                    "Multi-hop RAG — iterative retrieval, chain-of-retrieval",
                    "RAG evaluation — RAGAS, faithfulness, answer relevance metrics",
                    "GraphRAG — entity extraction, community detection, graph-based retrieval",
                    "Hands-on: Build production RAG pipeline with evaluation framework"
                ]
            },
            {
                "module": "LLM Fine-Tuning for NLP Tasks",
                "weeks": "13-14",
                "topics": [
                    "Full fine-tuning vs parameter-efficient methods — when to use what",
                    "LoRA & QLoRA — adapter training, rank selection, target modules",
                    "Instruction tuning — dataset creation, formatting, chat templates",
                    "DPO & ORPO — preference optimization without reward models",
                    "Fine-tuning for specific NLP tasks — summarization, QA, translation",
                    "Evaluation frameworks — task-specific metrics, human evaluation",
                    "Model merging — combining adapters, task arithmetic",
                    "Hands-on: Fine-tune open-source LLM for domain-specific NLP task"
                ]
            },
            {
                "module": "Production NLP Systems",
                "weeks": "15-16",
                "topics": [
                    "NLP pipeline orchestration — batch processing, streaming inference",
                    "Model serving — vLLM, TGI, Triton for transformer models",
                    "Quantization for deployment — GPTQ, AWQ, GGUF, bitsandbytes",
                    "Monitoring NLP systems — latency tracking, drift detection, quality metrics",
                    "Cost optimization — caching, batching, model selection strategies",
                    "Safety & guardrails — content filtering, PII detection, output validation",
                    "Capstone: End-to-end NLP application with RAG, fine-tuning, and production deployment"
                ]
            }
        ],
        "duration": "16 weeks", "level": "Intermediate", "price": 189999, "original_price": 329999,
        "image_url": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?q=80&w=800&auto=format&fit=crop",
        "category": "Core AI", "tags": ["HuggingFace", "RAG", "Fine-tuning", "Vector DB", "LLMs", "spaCy"],
        "instructor": {"name": "Mo. Wajahat", "role": "HOD Squarerootz", "image": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["RAG pipeline mastery", "LoRA/QLoRA fine-tuning", "ChromaDB + semantic search", "Production NLP systems"]
    },
    {
        "course_id": "cv-401", "slug": "computer-vision",
        "title": "Computer Vision",
        "subtitle": "From classical image processing to Vision Transformers, SAM, and real-time edge deployment",
        "description": "Master computer vision for the 2026 job market — where CV adoption is increasing 270% and engineers command $150K-$200K salaries. Build production systems with YOLOv8/v10, Segment Anything Model 2, Vision Transformers (ViT, CLIP, DINOv2), and deploy to edge devices. From defect detection in manufacturing to autonomous navigation, learn the full stack from pixel manipulation to real-time inference on Jetson and mobile.",
        "why_select": [
            "2026 job-market aligned — covers YOLO, SAM, ViT, and multimodal skills employers demand",
            "Production-first approach — edge deployment, TensorRT optimization, real-time inference",
            "Vision Transformers mastery — ViT, CLIP, DINOv2, and transformer-based detection (DETR)",
            "Open-source stack — OpenCV, Ultralytics, PyTorch, ONNX — no paid dependencies"
        ],
        "syllabus": [
            {
                "module": "Image Processing & OpenCV Foundations",
                "weeks": "1-2",
                "topics": [
                    "Digital image fundamentals — pixels, color spaces (RGB, HSV, LAB), bit depth",
                    "OpenCV essentials — reading, writing, resizing, cropping, drawing",
                    "Image filtering — blurring, sharpening, morphological operations",
                    "Edge detection — Sobel, Canny, Laplacian operators",
                    "Feature detection — corners (Harris, Shi-Tomasi), SIFT, ORB, BRISK",
                    "Image transformations — perspective, affine, homography estimation",
                    "Camera calibration — intrinsic/extrinsic parameters, distortion correction",
                    "Hands-on: Document scanner with perspective correction and edge enhancement"
                ]
            },
            {
                "module": "Convolutional Neural Networks for Vision",
                "weeks": "3-4",
                "topics": [
                    "CNN fundamentals — convolution, pooling, receptive fields, feature maps",
                    "Classic architectures — LeNet, AlexNet, VGG (understanding the evolution)",
                    "Modern architectures — ResNet skip connections, EfficientNet, ConvNeXt",
                    "Transfer learning — ImageNet pretrained models, feature extraction, fine-tuning",
                    "Data augmentation — geometric transforms, color augmentation, Albumentations",
                    "Advanced augmentation — MixUp, CutMix, AutoAugment, RandAugment",
                    "Training techniques — learning rate schedules, early stopping, gradient clipping",
                    "Hands-on: Custom image classifier with transfer learning and augmentation pipeline"
                ]
            },
            {
                "module": "Object Detection — YOLO & Beyond",
                "weeks": "5-6",
                "topics": [
                    "Object detection fundamentals — localization, bounding boxes, IoU, NMS",
                    "Two-stage detectors — R-CNN family evolution, Faster R-CNN architecture",
                    "Single-stage detectors — SSD, RetinaNet, focal loss for class imbalance",
                    "YOLO deep dive — YOLOv5, YOLOv8, YOLOv10 architectures and tradeoffs",
                    "Ultralytics ecosystem — training, validation, export, tracking integration",
                    "Anchor-free detection — CenterNet, FCOS, anchor-free YOLO variants",
                    "Evaluation metrics — mAP@50, mAP@50:95, precision-recall curves",
                    "Custom dataset preparation — labeling tools, COCO format, data splits",
                    "Hands-on: Train YOLOv8 on custom dataset for real-time object detection"
                ]
            },
            {
                "module": "Transformer-Based Detection",
                "weeks": "7",
                "topics": [
                    "DETR — Detection Transformer, end-to-end object detection without NMS",
                    "DETR improvements — Deformable DETR, DINO-DETR, RT-DETR for real-time",
                    "When transformers beat CNNs — understanding the tradeoffs",
                    "Co-DETR and DINOv3 — state-of-the-art detection benchmarks (mAP 65+)",
                    "Sparse-DETR — efficient transformer detection for production",
                    "Grounding DINO — open-vocabulary detection with text prompts",
                    "Combining detection with language — zero-shot and few-shot detection",
                    "Hands-on: Open-vocabulary object detection with Grounding DINO"
                ]
            },
            {
                "module": "Image Segmentation — From U-Net to SAM",
                "weeks": "8-9",
                "topics": [
                    "Segmentation taxonomy — semantic, instance, panoptic segmentation",
                    "U-Net architecture — encoder-decoder, skip connections, variants",
                    "Semantic segmentation — DeepLab family, PSPNet, SegFormer",
                    "Instance segmentation — Mask R-CNN, YOLACT, mask prediction",
                    "Panoptic segmentation — unifying semantic and instance, Mask2Former",
                    "Segment Anything Model (SAM) — architecture, prompting, zero-shot transfer",
                    "SAM 2 — video segmentation, temporal consistency, memory attention",
                    "Fine-tuning SAM — adapting to domain-specific segmentation tasks",
                    "Medical imaging segmentation — U-Net variants, nnU-Net, specialized architectures",
                    "Hands-on: Interactive segmentation tool with SAM and custom fine-tuning"
                ]
            },
            {
                "module": "Vision Transformers & Foundation Models",
                "weeks": "10",
                "topics": [
                    "Vision Transformer (ViT) — patch embedding, position encoding, attention",
                    "ViT variants — DeiT, Swin Transformer, PVT, hierarchical vision transformers",
                    "CLIP — contrastive learning, image-text alignment, zero-shot classification",
                    "DINO and DINOv2 — self-supervised learning, emergent properties",
                    "Foundation models for vision — when to use pretrained vs fine-tuned",
                    "Multimodal models — LLaVA, InternVL, vision-language integration",
                    "Zero-shot and few-shot classification with foundation models",
                    "Hands-on: Zero-shot image classification and search with CLIP"
                ]
            },
            {
                "module": "Video Analysis & Temporal Understanding",
                "weeks": "11",
                "topics": [
                    "Video fundamentals — frames, codecs, temporal sampling strategies",
                    "Object tracking — SORT, DeepSORT, ByteTrack, BoT-SORT algorithms",
                    "Multi-object tracking (MOT) — track association, re-identification",
                    "YOLO + tracking — integrated detection and tracking pipelines",
                    "Action recognition — Two-Stream, I3D, SlowFast, Video Transformers",
                    "Multiscale Vision Transformers (MViT) — video understanding at scale",
                    "Temporal action detection — localizing actions in untrimmed video",
                    "Video object segmentation — propagating masks through time",
                    "Hands-on: Real-time multi-object tracking system with re-identification"
                ]
            },
            {
                "module": "3D Vision & Spatial Computing",
                "weeks": "12",
                "topics": [
                    "3D vision fundamentals — depth estimation, stereo vision, structure from motion",
                    "Monocular depth estimation — MiDaS, Depth Anything, transformer-based depth",
                    "Point cloud processing — PointNet, PointNet++, 3D object detection",
                    "Neural Radiance Fields (NeRF) — 3D reconstruction from 2D images",
                    "Gaussian Splatting — fast 3D rendering, real-time novel view synthesis",
                    "LiDAR processing — sensor fusion, autonomous vehicle perception",
                    "Spatial computing applications — AR/VR, robotics, autonomous navigation",
                    "Hands-on: Depth estimation and 3D reconstruction from monocular video"
                ]
            },
            {
                "module": "Edge Deployment & Real-Time Optimization",
                "weeks": "13-14",
                "topics": [
                    "Model optimization — quantization (INT8, INT4), pruning, knowledge distillation",
                    "ONNX export — framework-agnostic deployment, runtime optimization",
                    "TensorRT optimization — NVIDIA inference optimization, layer fusion",
                    "Edge deployment targets — Jetson Nano/Xavier/Orin, Raspberry Pi, mobile",
                    "Mobile deployment — CoreML for iOS, TFLite for Android, ONNX Runtime Mobile",
                    "Real-time inference optimization — batching, async processing, memory management",
                    "OpenVINO — Intel optimization toolkit for CPU inference",
                    "Benchmarking and profiling — latency analysis, throughput optimization",
                    "Hands-on: Deploy YOLOv8 to Jetson with TensorRT for real-time inference"
                ]
            },
            {
                "module": "Production CV Systems & Capstone",
                "weeks": "15-16",
                "topics": [
                    "Production architecture — model serving, load balancing, scaling strategies",
                    "Triton Inference Server — multi-model serving, dynamic batching",
                    "Data pipeline design — annotation workflows, active learning loops",
                    "Monitoring CV systems — accuracy degradation, data drift detection",
                    "MLOps for vision — versioning datasets, experiment tracking, CI/CD",
                    "Quality inspection use case — manufacturing defect detection pipeline",
                    "Autonomous systems use case — perception stack for robotics/vehicles",
                    "Capstone: End-to-end CV system with training, optimization, and edge deployment",
                    "Portfolio presentation — showcasing CV projects to employers"
                ]
            }
        ],
        "duration": "16 weeks", "level": "Advanced", "price": 199999, "original_price": 349999,
        "image_url": "https://images.unsplash.com/photo-1561736778-92e52a7769ef?q=80&w=800&auto=format&fit=crop",
        "category": "Core AI", "tags": ["YOLOv8", "SAM", "Vision Transformers", "CLIP", "OpenCV", "TensorRT", "Edge AI"],
        "instructor": {"name": "Mo. Wajahat", "role": "HOD Squarerootz", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["YOLOv8/v10 + SAM mastery", "Vision Transformers (ViT, CLIP, DINOv2)", "Edge deployment with TensorRT", "3D vision & NeRF/Gaussian Splatting"],
        "popular": 0
    },
    {
        "course_id": "gai-501", "slug": "generative-ai",
        "title": "Generative AI",
        "subtitle": "From LLM fundamentals to diffusion models, multimodal AI, and production systems",
        "description": "Master the full spectrum of generative AI for the 2026 job market — where AI Engineer roles grew 143% and global GenAI investment exceeds $30 billion. Build production systems with LLMs (GPT, Claude, LLaMA), diffusion models (Stable Diffusion, FLUX), and multimodal architectures. From fine-tuning with LoRA/DPO to building RAG pipelines and AI agents, graduate with a portfolio spanning text generation, image synthesis, video generation, and agentic workflows.",
        "why_select": [
            "Complete GenAI stack — LLMs, diffusion models, multimodal, video generation, and agents",
            "Production-first curriculum — RAG + fine-tuning hybrid architectures used in enterprise",
            "2026 alignment techniques — DPO, ORPO, and Constitutional AI for safe, helpful outputs",
            "Open-source focused — Hugging Face, Ollama, ComfyUI, with OpenAI API for comparison"
        ],
        "syllabus": [
            {
                "module": "Generative AI Foundations",
                "weeks": "1-2",
                "topics": [
                    "The 2026 GenAI landscape — market trends, job roles, and skill requirements",
                    "Generative vs discriminative models — understanding the paradigm shift",
                    "Autoregressive generation — predicting the next token, sampling strategies",
                    "Language model fundamentals — tokenization, embeddings, context windows",
                    "OpenAI API deep dive — chat completions, function calling, structured outputs",
                    "Local LLMs with Ollama — running Llama, Mistral, Qwen on your machine",
                    "Cost and latency considerations — when to use API vs local models",
                    "Hands-on: Build a multi-model chatbot with OpenAI and Ollama fallback"
                ]
            },
            {
                "module": "Transformer Architectures for Generation",
                "weeks": "3-4",
                "topics": [
                    "Transformer architecture — attention, positional encoding, layer normalization",
                    "Decoder-only models — GPT architecture, causal attention, KV caching",
                    "Open-source LLM landscape — Llama 3.x, Mistral, Qwen, Gemma, Phi",
                    "Model selection criteria — size, context length, capabilities, licensing",
                    "Mixture of Experts (MoE) — Mixtral, DeepSeek, sparse activation",
                    "Long context models — handling 100K+ tokens, retrieval vs context length",
                    "Inference optimization — speculative decoding, continuous batching",
                    "Hands-on: Compare model architectures on benchmark tasks"
                ]
            },
            {
                "module": "Prompt Engineering & Structured Outputs",
                "weeks": "5-6",
                "topics": [
                    "Prompt engineering fundamentals — zero-shot, few-shot, system prompts",
                    "Advanced prompting — chain-of-thought, tree-of-thought, self-consistency",
                    "ReAct pattern — combining reasoning and acting for agentic tasks",
                    "Structured outputs — JSON mode, function calling, Instructor library",
                    "Output parsing and validation — Pydantic models, retry strategies",
                    "Prompt optimization — DSPy for systematic prompt tuning",
                    "Prompt injection defense — understanding and mitigating attacks",
                    "Hands-on: Build a structured data extraction pipeline with validation"
                ]
            },
            {
                "module": "Retrieval-Augmented Generation (RAG)",
                "weeks": "7-8",
                "topics": [
                    "RAG architecture — retrieval as dynamic knowledge for generation",
                    "Document processing — chunking strategies, metadata extraction",
                    "Embedding models — OpenAI, BGE, Nomic, choosing the right model",
                    "Vector databases — ChromaDB, Qdrant, pgvector for different use cases",
                    "Hybrid search — combining dense embeddings with BM25 sparse retrieval",
                    "Re-ranking — cross-encoders, Cohere Rerank, improving precision",
                    "Advanced RAG — HyDE, query decomposition, multi-hop retrieval",
                    "RAG evaluation — RAGAS metrics, faithfulness, answer relevance",
                    "Hands-on: Production RAG system with hybrid search and evaluation"
                ]
            },
            {
                "module": "Fine-Tuning LLMs",
                "weeks": "9-10",
                "topics": [
                    "When to fine-tune vs RAG vs prompting — decision framework",
                    "Full fine-tuning — when you have compute and data, best practices",
                    "LoRA deep dive — low-rank adaptation, rank selection, target modules",
                    "QLoRA — 4-bit quantization enabling fine-tuning on consumer GPUs",
                    "Instruction tuning — dataset creation, chat templates, formatting",
                    "DPO (Direct Preference Optimization) — simpler alternative to RLHF",
                    "ORPO — combining SFT and preference learning in one step",
                    "Model merging — combining adapters, TIES, DARE, task arithmetic",
                    "Evaluation frameworks — benchmarks, human evaluation, LLM-as-judge",
                    "Hands-on: Fine-tune Llama/Mistral with QLoRA for a domain-specific task"
                ]
            },
            {
                "module": "RLHF & AI Alignment",
                "weeks": "11",
                "topics": [
                    "The alignment problem — why helpful, harmless, and honest matter",
                    "RLHF fundamentals — reward modeling, PPO optimization",
                    "Reward model training — preference data collection, ranking formats",
                    "DPO vs RLHF — when simpler is better, implementation tradeoffs",
                    "Constitutional AI — self-improvement through principles",
                    "Red teaming — adversarial testing, finding model weaknesses",
                    "Safety guardrails — content filtering, refusal training",
                    "Responsible AI practices — bias detection, fairness evaluation",
                    "Hands-on: Train a reward model and align an LLM with DPO"
                ]
            },
            {
                "module": "Diffusion Models & Image Generation",
                "weeks": "12-13",
                "topics": [
                    "Diffusion fundamentals — forward process, reverse process, noise schedules",
                    "DDPM and score matching — the math behind diffusion models",
                    "Latent diffusion — working in compressed space, autoencoder component",
                    "Stable Diffusion architecture — U-Net, cross-attention, CLIP encoder",
                    "SDXL and SD3 — modern Stable Diffusion variants and improvements",
                    "FLUX models — next-generation architecture, flow matching",
                    "ControlNet — adding spatial control to image generation",
                    "Fine-tuning diffusion — DreamBooth, textual inversion, LoRA for SD",
                    "ComfyUI workflows — node-based generation for production pipelines",
                    "Hands-on: Build a custom image generation pipeline with ComfyUI"
                ]
            },
            {
                "module": "Multimodal & Video Generation",
                "weeks": "14-15",
                "topics": [
                    "Multimodal AI fundamentals — vision-language alignment, CLIP architecture",
                    "Vision-language models — LLaVA, InternVL, GPT-4V capabilities",
                    "Image understanding — visual QA, image captioning, OCR integration",
                    "Text-to-video fundamentals — temporal consistency, motion modeling",
                    "Video generation models — Runway Gen-3, Pika, open-source alternatives",
                    "Image-to-video — animating static images, video extension",
                    "Audio generation — text-to-speech, music generation, voice cloning ethics",
                    "Multimodal agents — combining vision, language, and action",
                    "Hands-on: Build a multimodal assistant with vision and generation capabilities"
                ]
            },
            {
                "module": "AI Agents & Agentic Systems",
                "weeks": "16-17",
                "topics": [
                    "Agent fundamentals — autonomy, tool use, planning, memory",
                    "Agent architectures — ReAct, function calling, multi-step reasoning",
                    "Tool creation — defining tools, parameter schemas, error handling",
                    "Memory systems — short-term context, long-term vector storage",
                    "Multi-agent systems — orchestration, collaboration, specialization",
                    "LangGraph for agents — graph-based workflows, state management",
                    "OpenAI Agents SDK — handoffs, guardrails, production patterns",
                    "Agent evaluation — task completion, efficiency, safety metrics",
                    "Hands-on: Build a multi-agent system for research and content creation"
                ]
            },
            {
                "module": "Production GenAI & Capstone",
                "weeks": "18",
                "topics": [
                    "Production architecture — API design, load balancing, scaling",
                    "Inference optimization — vLLM, TGI, quantization for deployment",
                    "Cost management — caching, model routing, token budgets",
                    "Monitoring and observability — latency tracking, quality metrics",
                    "Safety in production — content filtering, PII detection, rate limiting",
                    "GenAI product design — user experience, feedback loops, iteration",
                    "Capstone: End-to-end GenAI application with LLM, RAG, fine-tuning, and agents",
                    "Portfolio presentation — showcasing GenAI projects to employers"
                ]
            }
        ],
        "duration": "18 weeks", "level": "Intermediate", "price": 249999, "original_price": 449999,
        "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?q=80&w=800&auto=format&fit=crop",
        "category": "Generative AI", "tags": ["LLMs", "Diffusion Models", "RAG", "Fine-tuning", "DPO", "AI Agents", "Multimodal"],
        "instructor": {"name": "Nikhil Yadav", "role": "Cofounder HypeneuronAi", "image": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["Complete GenAI stack — LLMs to diffusion to video", "Fine-tuning mastery — LoRA, QLoRA, DPO, ORPO", "RAG + agents production patterns", "Multimodal & video generation"],
        "popular": 1
    },
    {
        "course_id": "pe-601", "slug": "prompt-engineering",
        "title": "Prompt Engineering",
        "subtitle": "From casual prompting to production context engineering with DSPy and evaluation frameworks",
        "description": "Master prompt engineering as a genuine engineering discipline for 2026 — where the field has evolved from casual prompting to production context engineering. Learn to treat prompts as code with version control, A/B testing, and automated optimization using DSPy. Cover all major LLMs (GPT-4, Claude, Gemini, Llama), advanced techniques (CoT, ToT, ReAct), structured outputs, prompt injection defense, and evaluation frameworks. Average salary: $127K with top roles commanding significantly more.",
        "why_select": [
            "2026 context engineering — beyond casual prompting to genuine production engineering",
            "DSPy mastery — programmatic prompt optimization replacing manual trial-and-error",
            "Multi-LLM proficiency — GPT-4, Claude, Gemini, Llama with model-specific strategies",
            "Production patterns — evaluation, A/B testing, version control, security"
        ],
        "syllabus": [
            {
                "module": "Prompt Engineering Foundations",
                "weeks": "1-2",
                "topics": [
                    "The 2026 prompting landscape — casual vs production context engineering",
                    "LLM fundamentals for prompt engineers — tokenization, context windows, attention",
                    "Zero-shot prompting — crafting effective single-turn prompts",
                    "Few-shot prompting — example selection, formatting, in-context learning",
                    "System prompts — persona design, instruction formatting, constraint setting",
                    "Model parameters — temperature, top-p, frequency penalty, when to adjust",
                    "Multi-LLM differences — GPT-4 vs Claude vs Gemini vs Llama prompting styles",
                    "Hands-on: Build a prompt testing harness across multiple LLM providers"
                ]
            },
            {
                "module": "Advanced Prompting Techniques",
                "weeks": "3-4",
                "topics": [
                    "Chain-of-thought (CoT) — step-by-step reasoning, 19-point MMLU-Pro boost",
                    "When to skip CoT — reasoning models (o-series, Claude Extended Thinking) do it internally",
                    "Tree-of-thought (ToT) — branching exploration for complex problems",
                    "Self-consistency — sampling multiple reasoning paths, voting for answers",
                    "ReAct pattern — reasoning + acting for agentic task completion",
                    "Decomposition techniques — breaking complex tasks into manageable steps",
                    "Metacognitive prompting — having models evaluate their own reasoning",
                    "Hands-on: Compare prompting strategies on benchmark reasoning tasks"
                ]
            },
            {
                "module": "Structured Outputs & Parsing",
                "weeks": "5-6",
                "topics": [
                    "JSON mode — forcing structured output from LLMs",
                    "Function calling — OpenAI, Anthropic, and open-source implementations",
                    "Schema design — Pydantic models, JSON Schema, type constraints",
                    "Instructor library — structured extraction with validation and retries",
                    "Output parsing strategies — regex, JSON parsing, error recovery",
                    "Nested structures — handling complex, hierarchical outputs",
                    "Multi-step extraction — chaining prompts for complex data extraction",
                    "Hands-on: Build a structured data extraction pipeline with validation"
                ]
            },
            {
                "module": "DSPy — Programming, Not Prompting",
                "weeks": "7-8",
                "topics": [
                    "DSPy fundamentals — the framework for programming language models",
                    "Signatures — declarative specifications for LLM tasks",
                    "Modules — ChainOfThought, ReAct, and custom modules",
                    "Optimizers — MIPROv2, BootstrapFewShot, automatic prompt refinement",
                    "Metrics and evaluation — defining what 'better' means for your task",
                    "DSPy for RAG — optimizing retrieval and generation together",
                    "DSPy for agents — building optimizable agentic workflows",
                    "When DSPy wins vs manual prompting — decision framework",
                    "Hands-on: Optimize a classification pipeline with DSPy, measure improvement"
                ]
            },
            {
                "module": "Prompt Security & Safety",
                "weeks": "9",
                "topics": [
                    "Prompt injection attacks — direct, indirect, and data exfiltration",
                    "Jailbreaking techniques — understanding attack vectors",
                    "Defense strategies — input validation, output filtering, sandboxing",
                    "Guardrails implementation — content filtering, topic boundaries",
                    "PII detection and redaction — protecting sensitive data",
                    "Rate limiting and abuse prevention — protecting production systems",
                    "Red teaming prompts — systematically finding vulnerabilities",
                    "Hands-on: Build a hardened prompt pipeline with multiple defense layers"
                ]
            },
            {
                "module": "Production Prompt Operations",
                "weeks": "10-12",
                "topics": [
                    "Prompts as code — version control, code review for prompts",
                    "A/B testing prompts — statistical rigor, sample sizing, analysis",
                    "Evaluation frameworks — human evaluation, LLM-as-judge, metrics",
                    "Prompt registries — centralized management, access control",
                    "Cost optimization — model routing, caching, token budgets",
                    "Multi-model strategies — fallbacks, routing by task complexity",
                    "Monitoring in production — latency, quality, drift detection",
                    "CI/CD for prompts — automated testing, deployment pipelines",
                    "Capstone: Production prompt system with evaluation, testing, and monitoring"
                ]
            }
        ],
        "duration": "12 weeks", "level": "Beginner", "price": 129999, "original_price": 199999,
        "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=800&auto=format&fit=crop",
        "category": "Generative AI", "tags": ["DSPy", "GPT-4", "Claude", "Gemini", "CoT", "Structured Outputs", "Production"],
        "instructor": {"name": "Nikhil Yadav", "role": "Cofounder HypeneuronAi", "image": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["DSPy for programmatic optimization", "Multi-LLM strategies", "Production prompt ops", "Security & guardrails"],
        "popular": 0
    },
    {
        "course_id": "aai-701", "slug": "agentic-ai-cloud-agnostic",
        "title": "Agentic AI — Cloud Agnostic",
        "subtitle": "Master autonomous AI agents with production-ready skills for the 2026 job market",
        "description": "The definitive 12-week program to become a production-ready Agentic AI engineer. Learn to build autonomous agents that reason, use tools, remember context, and collaborate — all using open-source frameworks and minimal paid services. From ReAct fundamentals to multi-agent orchestration, MCP integration to production deployment, this course reverse-engineers what employers will demand and teaches you to exceed those expectations. Graduate with 4 portfolio-ready capstone projects targeting research, enterprise, developer tools, and customer support domains.",
        "why_select": [
            "Future-proof curriculum — designed for the job market 12 weeks ahead, not yesterday's requirements",
            "Concept-first approach — master the 'why' behind agent architectures, not just tool-specific implementations",
            "Minimal paid services — uses only OpenAI API; everything else is open-source (LangGraph, CrewAI, Ollama, ChromaDB)",
            "4 capstone tracks — build portfolio projects for Research, Enterprise, Developer Tools, or Customer Support roles",
            "Production patterns from day one — observability, guardrails, cost optimization, and safety are core, not afterthoughts",
            "MCP & A2A protocols — master the new industry standards adopted by OpenAI, Google, Microsoft, and Anthropic"
        ],
        "syllabus": [
            {
                "module": "Agent Foundations & First Principles",
                "weeks": "1-2",
                "topics": [
                    "What makes an agent 'agentic' — autonomy, reasoning, and goal-directed behavior",
                    "The ReAct pattern — Reasoning + Acting in iterative loops",
                    "LLM as the reasoning engine — prompt engineering for agent systems",
                    "Tool use fundamentals — function calling, structured outputs, error handling",
                    "Building your first agent from scratch (Python + OpenAI API only)",
                    "Agent loop anatomy — observe, think, act, repeat",
                    "Hands-on: CLI agent that searches the web, reads files, and answers questions"
                ]
            },
            {
                "module": "Memory Systems & Stateful Agents",
                "weeks": "3-4",
                "topics": [
                    "Why memory matters — from stateless chatbots to persistent assistants",
                    "The three-layer memory architecture — episodic, semantic, and procedural",
                    "Short-term memory — conversation context and sliding windows",
                    "Long-term memory with vector databases — ChromaDB, pgvector (open-source)",
                    "Embeddings deep dive — OpenAI embeddings, sentence-transformers, local models",
                    "Memory retrieval strategies — similarity search, MMR, time-decay",
                    "Implementing memory from scratch vs. using frameworks",
                    "Hands-on: Personal assistant that remembers user preferences across sessions"
                ]
            },
            {
                "module": "RAG for Agents — Knowledge-Powered Intelligence",
                "weeks": "5-6",
                "topics": [
                    "RAG architecture — retrieval as an agent's external knowledge system",
                    "Document processing pipeline — chunking strategies, metadata extraction",
                    "Hybrid retrieval — combining keyword search (BM25) with semantic search",
                    "Re-ranking for precision — cross-encoder models, reciprocal rank fusion",
                    "Evaluation metrics that matter — recall@k, precision@k, groundedness",
                    "Common RAG failures and how to debug them — retrieval vs. generation issues",
                    "GraphRAG concepts — when relationships matter more than similarity",
                    "Hands-on: Research agent with document ingestion, retrieval, and citation"
                ]
            },
            {
                "module": "Framework Mastery — LangGraph, CrewAI, OpenAI SDK",
                "weeks": "7-8",
                "topics": [
                    "Framework landscape 2026 — when to use what and why",
                    "LangGraph deep dive — graph-based workflows, state management, checkpointing",
                    "Building complex workflows — branching, cycles, conditional edges",
                    "CrewAI for rapid prototyping — role-based agents, delegation, collaboration",
                    "OpenAI Agents SDK — handoffs, guardrails, and the fastest path to production",
                    "Framework migration patterns — CrewAI to LangGraph (the common path)",
                    "Human-in-the-loop patterns — approval workflows, feedback collection",
                    "Hands-on: Build the same agent in all 3 frameworks — compare trade-offs"
                ]
            },
            {
                "module": "MCP & A2A — The New Integration Standards",
                "weeks": "9",
                "topics": [
                    "Model Context Protocol (MCP) — the 'USB for AI agents'",
                    "MCP architecture — clients, servers, tools, resources, prompts",
                    "Building MCP servers — expose your own tools to any MCP-compatible agent",
                    "Connecting to the MCP ecosystem — 10,000+ public servers",
                    "Agent-to-Agent (A2A) protocol — Google's standard for multi-agent communication",
                    "A2A concepts — agent cards, task delegation, secure communication",
                    "MCP vs A2A — complementary protocols for tools and agent collaboration",
                    "Hands-on: Agent with MCP connections to filesystem, database, and web APIs"
                ]
            },
            {
                "module": "Multi-Agent Systems & Orchestration",
                "weeks": "10",
                "topics": [
                    "When single agents aren't enough — the case for multi-agent architectures",
                    "Orchestration patterns — sequential, parallel, hierarchical, collaborative",
                    "Agent communication — message passing, shared memory, blackboard systems",
                    "Role specialization — researcher, planner, executor, critic patterns",
                    "Conflict resolution — handling disagreements between agents",
                    "Supervisor vs. peer architectures — control patterns for agent teams",
                    "State synchronization across agents — consistency challenges",
                    "Hands-on: Multi-agent research team with planner, researcher, writer, and reviewer"
                ]
            },
            {
                "module": "Production, Safety & Cost Optimization",
                "weeks": "11",
                "topics": [
                    "Production readiness checklist — what separates demos from deployable systems",
                    "Observability & debugging — tracing agent decisions, LangSmith alternatives",
                    "Safety guardrails — prompt injection defense, tool permission boundaries",
                    "Output validation — ensuring agents don't hallucinate or go off-rails",
                    "Cost optimization strategies — caching, model routing, token budgets",
                    "Local LLM deployment — Ollama, llama.cpp for cost-free development and privacy",
                    "Containerization with Docker — packaging agents for deployment",
                    "Error handling and graceful degradation — building resilient systems",
                    "Hands-on: Add observability, guardrails, and cost tracking to your capstone"
                ]
            },
            {
                "module": "Capstone Projects — Portfolio-Ready Systems",
                "weeks": "12",
                "topics": [
                    "Capstone Track 1: AI Research Assistant — paper search, summarization, knowledge graphs",
                    "Capstone Track 2: Enterprise Workflow Agent — document processing, approvals, email handling",
                    "Capstone Track 3: Developer Productivity Agent — code review, documentation, test generation",
                    "Capstone Track 4: Customer Support System — multi-tier support, escalation, human handoff",
                    "End-to-end deployment — from local development to cloud/on-premise production",
                    "Portfolio documentation — presenting your work to employers",
                    "Live project review and feedback sessions",
                    "Career preparation — resume optimization, interview prep for agentic AI roles"
                ]
            }
        ],
        "duration": "12 weeks", "level": "Advanced", "price": 249999, "original_price": 449999,
        "image_url": "https://images.unsplash.com/photo-1535378917042-10a22c95931a?q=80&w=800&auto=format&fit=crop",
        "category": "Agentic AI",
        "tags": ["LangGraph", "CrewAI", "OpenAI Agents SDK", "MCP", "A2A Protocol", "RAG", "Multi-Agent", "Ollama"],
        "instructor": {"name": "Rohan Gupta", "role": "AI Architect", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop"},
        "highlights": [
            "4 portfolio-ready capstone projects",
            "MCP & A2A protocol mastery — the 2026 standards",
            "Open-source first — minimal paid dependencies",
            "Production patterns from week 1",
            "Multi-framework proficiency (LangGraph + CrewAI + OpenAI SDK)",
            "Local LLM deployment with Ollama"
        ],
        "popular": 1
    },

    {
        "course_id": "az-901", "slug": "azure-agentic-ai",
        "title": "Azure Agentic AI",
        "subtitle": "Build enterprise-grade AI agents with Microsoft's unified AI platform — from Foundry to Copilot Studio",
        "description": "The complete 10-week program to master AI agent development on Microsoft Azure. Learn to build, deploy, and govern autonomous agents using Azure AI Foundry Agent Service (GA), Semantic Kernel, and Copilot Studio. This course covers the new Microsoft Agent Framework that converges AutoGen and Semantic Kernel, enterprise RAG with Azure AI Search, and seamless deployment to Microsoft 365 and Teams. Prepare for the Azure AI Engineer Associate (AI-102) certification while building production agents used by 10,000+ organizations including Heineken, Carvana, and Fujitsu.",
        "why_select": [
            "Azure AI Engineer Associate (AI-102) aligned — updated for 2026 with generative AI and agentic solutions focus",
            "Microsoft Agent Framework mastery — the production-ready convergence of AutoGen + Semantic Kernel",
            "Azure AI Foundry Agent Service (GA) — enterprise-grade agent runtime with built-in safety, memory, and observability",
            "Copilot Studio autonomous agents — no-code to pro-code spectrum for rapid enterprise deployment",
            "Enterprise integration — one-click deployment to Teams, Microsoft 365, Power Platform, and Dynamics 365",
            "Security-first architecture — Entra identity, content safety, network isolation, and compliance controls"
        ],
        "syllabus": [
            {
                "module": "Azure AI Platform Foundations",
                "weeks": "1-2",
                "topics": [
                    "Azure AI services landscape — Foundry vs OpenAI Service vs Cognitive Services",
                    "Azure OpenAI Service deep dive — GPT-4o, o1 reasoning models, model deployment options",
                    "Azure AI Foundry portal — unified workspace for models, agents, and evaluation",
                    "Resource management — subscriptions, resource groups, quotas, and cost management",
                    "Identity and access — Entra ID, managed identities, RBAC for AI workloads",
                    "Development environment setup — Azure CLI, SDKs, VS Code extensions",
                    "Hands-on: Deploy your first Azure OpenAI model and build a chat application"
                ]
            },
            {
                "module": "Azure AI Foundry Agent Service",
                "weeks": "3-4",
                "topics": [
                    "Foundry Agent Service architecture — the production-ready agent runtime",
                    "Creating agents with code — Python SDK, conversation management, tool orchestration",
                    "Function calling — connecting agents to Azure Functions and external APIs",
                    "Built-in tools — code interpreter, file search, Bing grounding, Azure AI Search",
                    "Agent memory (preview) — long-term memory across sessions and devices",
                    "Content safety integration — filters, prompt injection protection (XPIA)",
                    "Debugging and tracing — understanding agent reasoning and tool calls",
                    "Hands-on: Build a customer support agent with function calling and memory"
                ]
            },
            {
                "module": "Semantic Kernel & Microsoft Agent Framework",
                "weeks": "5-6",
                "topics": [
                    "Semantic Kernel fundamentals — plugins, planners, and memory",
                    "Microsoft Agent Framework — the AutoGen + Semantic Kernel convergence",
                    "AzureAIAgent in Semantic Kernel — seamless Foundry integration",
                    "Building multi-agent systems — orchestrating specialist agents",
                    "MCP and A2A protocol support — connecting to the broader agent ecosystem",
                    "Magentic One patterns — advanced multi-agent orchestration",
                    "Local development to Azure deployment — seamless production path",
                    "Hands-on: Multi-agent research system with Search, Report, and Validation agents"
                ]
            },
            {
                "module": "Enterprise RAG with Azure AI Search",
                "weeks": "7",
                "topics": [
                    "Azure AI Search architecture — indexes, indexers, skillsets",
                    "Vector search — embeddings, HNSW indexing, similarity search",
                    "Hybrid search — combining keyword and vector retrieval with RRF",
                    "Semantic ranking — transformer-based re-ranking for precision",
                    "Integrated vectorization — automatic chunking and embedding",
                    "Knowledge bases in Foundry IQ — unified context layer for agents",
                    "Data source connectors — Blob Storage, SharePoint, SQL, Cosmos DB",
                    "Hands-on: Build a knowledge-grounded agent with hybrid search and semantic ranking"
                ]
            },
            {
                "module": "Copilot Studio — No-Code to Pro-Code Agents",
                "weeks": "8",
                "topics": [
                    "Copilot Studio fundamentals — visual agent builder, topics, and triggers",
                    "Autonomous agents — event-driven automation without manual triggers",
                    "Deep reasoning with o1 — complex decision-making in enterprise scenarios",
                    "Generative AI features — generative answers, generative actions",
                    "Custom connectors and Power Automate integration",
                    "Pro-code extensibility — extending Copilot Studio with custom code",
                    "Declarative vs autonomous agents — choosing the right approach",
                    "Hands-on: Build an autonomous IT helpdesk agent with ticket routing and escalation"
                ]
            },
            {
                "module": "Enterprise Integration & Deployment",
                "weeks": "9",
                "topics": [
                    "Microsoft 365 Copilot integration — extending with custom agents",
                    "Teams deployment — one-click agent publishing to Teams channels",
                    "Power Platform integration — Power Automate, Power Apps, Dataverse",
                    "Dynamics 365 scenarios — sales, service, and operations agents",
                    "SharePoint and OneDrive — document-grounded agents",
                    "Work IQ layer — long-term organizational memory and context",
                    "Multi-channel deployment — web, mobile, voice assistants",
                    "Hands-on: Deploy your agent to Teams with Power Automate workflow triggers"
                ]
            },
            {
                "module": "Security, Governance & Production Operations",
                "weeks": "10",
                "topics": [
                    "Enterprise security — Entra identity for agents, network isolation, VNets",
                    "Content safety — Azure AI Content Safety, custom blocklists, XPIA protection",
                    "Data loss prevention — DLP policies for agent communications",
                    "Compliance and governance — audit logging, data residency, responsible AI",
                    "Bring your own resources — storage, search, Cosmos DB for compliance",
                    "Monitoring and observability — Azure Monitor, Application Insights",
                    "Cost management — token tracking, quota management, optimization strategies",
                    "Azure AI Engineer Associate (AI-102) exam preparation",
                    "Capstone: Production-ready enterprise agent with full governance and M365 integration"
                ]
            }
        ],
        "duration": "10 weeks", "level": "Intermediate", "price": 229999, "original_price": 399999,
        "image_url": "https://images.unsplash.com/photo-1584381296550-99dfc0837d42?q=80&w=800&auto=format&fit=crop",
        "category": "Agentic AI",
        "tags": ["Azure AI Foundry", "Semantic Kernel", "Copilot Studio", "Azure AI Search", "Microsoft Agent Framework", "Teams", "M365"],
        "instructor": {"name": "Rohan Gupta", "role": "AI Architect", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop"},
        "highlights": [
            "Azure AI Engineer (AI-102) certification aligned",
            "Microsoft Agent Framework — AutoGen + Semantic Kernel",
            "Foundry Agent Service (GA) — enterprise runtime",
            "Copilot Studio autonomous agents",
            "One-click Teams & M365 deployment",
            "Enterprise security & governance"
        ],
        "popular": 0
    },
    {
        "course_id": "ops-1001", "slug": "aiops",
        "title": "AIOps",
        "subtitle": "Autonomous IT operations with ML-driven monitoring, self-healing systems, and LLM-powered incident management",
        "description": "Master AIOps for 2026 — where 60% of large enterprises will implement self-healing systems powered by AI. Build production-grade anomaly detection, automated remediation, and LLM-powered incident management for Kubernetes and cloud infrastructure. From Prometheus and Grafana to OpenTelemetry and RAG-based log analysis, learn to reduce MTTR by 90% and automate the operations lifecycle. Bridge the gap between DevOps, SRE, and AI — the most in-demand hybrid skill set commanding $81K-$360K salaries.",
        "why_select": [
            "2026 autonomous IT — self-healing systems, predictive alerting, automated root cause analysis",
            "LLM-powered operations — natural language querying, RAG for log analysis, AI agents for remediation",
            "Kubernetes-native — self-healing clusters, K8sGPT, GitOps with Argo CD",
            "Production observability stack — Prometheus, Grafana, OpenTelemetry, ELK, Datadog patterns"
        ],
        "syllabus": [
            {
                "module": "AIOps Foundations & Observability",
                "weeks": "1-2",
                "topics": [
                    "The 2026 AIOps landscape — from monitoring to autonomous operations",
                    "Observability fundamentals — metrics, logs, traces, and their relationships",
                    "The three pillars — why observability is non-negotiable in 2026",
                    "Prometheus deep dive — metrics collection, PromQL, alerting rules",
                    "Grafana fundamentals — dashboards, panels, variables, alerting",
                    "OpenTelemetry — vendor-neutral instrumentation, collectors, exporters",
                    "Distributed tracing — understanding request flows across microservices",
                    "Hands-on: Build observability stack with Prometheus, Grafana, and Jaeger"
                ]
            },
            {
                "module": "Log Management & Analysis",
                "weeks": "3-4",
                "topics": [
                    "Log architecture — collection, aggregation, indexing, retention",
                    "ELK Stack — Elasticsearch, Logstash, Kibana for log analytics",
                    "Loki — Grafana's log aggregation system, LogQL queries",
                    "Log parsing — structured vs unstructured, parsing patterns",
                    "Log-based alerting — pattern matching, threshold detection",
                    "Log correlation — connecting logs across services",
                    "Cost optimization — log sampling, retention policies, tiered storage",
                    "Hands-on: Build centralized logging with Loki and Grafana"
                ]
            },
            {
                "module": "Anomaly Detection with ML",
                "weeks": "5-6",
                "topics": [
                    "Anomaly detection fundamentals — statistical vs ML-based approaches",
                    "Time series analysis — trends, seasonality, forecasting for ops data",
                    "Statistical methods — z-score, IQR, moving averages, ARIMA",
                    "ML-based detection — Isolation Forest, Autoencoders, LSTM for sequences",
                    "Prophet for capacity planning — forecasting resource utilization",
                    "Multivariate anomaly detection — correlating across metrics",
                    "Alert correlation — reducing noise, grouping related alerts",
                    "False positive reduction — tuning models for operational accuracy",
                    "Hands-on: Build anomaly detection pipeline for infrastructure metrics"
                ]
            },
            {
                "module": "LLM-Powered Operations",
                "weeks": "7-8",
                "topics": [
                    "LLMs in AIOps — natural language interfaces for infrastructure",
                    "RAG for log analysis — semantic search over operational data",
                    "LLM-based root cause analysis — connecting symptoms to causes",
                    "Natural language querying — translating questions to PromQL/LogQL",
                    "K8sGPT — AI-powered Kubernetes troubleshooting",
                    "ChatOps with LLMs — conversational incident management",
                    "Building operational knowledge bases — documentation as context",
                    "Tool-augmented generation — LLMs executing diagnostic scripts",
                    "Hands-on: Build RAG-powered log analysis and incident investigation tool"
                ]
            },
            {
                "module": "Kubernetes Operations & Self-Healing",
                "weeks": "9-10",
                "topics": [
                    "Kubernetes observability — metrics-server, kube-state-metrics, cAdvisor",
                    "Kubernetes monitoring with Prometheus — ServiceMonitors, PodMonitors",
                    "Kubernetes troubleshooting — common issues, diagnostic patterns",
                    "Self-healing fundamentals — liveness, readiness, startup probes",
                    "Auto-scaling — HPA, VPA, KEDA for event-driven scaling",
                    "GitOps with Argo CD — declarative operations, drift detection",
                    "Kubernetes operators — extending K8s for operational automation",
                    "K8sGPT Operator — AI-powered cluster insights and suggestions",
                    "Hands-on: Build self-healing Kubernetes application with auto-remediation"
                ]
            },
            {
                "module": "Automated Remediation",
                "weeks": "11-12",
                "topics": [
                    "Remediation fundamentals — runbooks, playbooks, automation patterns",
                    "Event-driven remediation — connecting alerts to actions",
                    "Ansible for IT automation — playbooks, roles, dynamic inventory",
                    "Terraform for infrastructure healing — drift correction, auto-provisioning",
                    "Rundeck and StackStorm — runbook automation platforms",
                    "ServiceNow integration — ITSM-connected remediation workflows",
                    "Change intelligence — risk assessment for automated changes",
                    "Guardrails for automation — preventing automation-caused incidents",
                    "Hands-on: Build automated remediation pipeline with Ansible and event triggers"
                ]
            },
            {
                "module": "Incident Management & AI Agents",
                "weeks": "13-14",
                "topics": [
                    "Modern incident management — MTTA, MTTR, incident lifecycle",
                    "PagerDuty/Opsgenie patterns — on-call management, escalation",
                    "AI-powered triage — automatic severity assessment, routing",
                    "Root cause analysis automation — correlation, dependency mapping",
                    "AI agents for incidents — autonomous investigation and remediation",
                    "Multi-agent operations — orchestrating responses across systems",
                    "Post-incident review automation — generating incident reports with LLMs",
                    "SRE practices — error budgets, SLOs, SLIs for AI systems",
                    "Hands-on: Build AI agent for incident triage and initial remediation"
                ]
            },
            {
                "module": "Production AIOps & Capstone",
                "weeks": "15-16",
                "topics": [
                    "Enterprise AIOps architecture — multi-cloud, hybrid environments",
                    "FinOps integration — cost optimization through intelligent operations",
                    "Cloud provider tools — AWS CloudWatch, Azure Monitor, GCP Cloud Operations",
                    "AIOps platform evaluation — build vs buy, integration considerations",
                    "ROI measurement — quantifying AIOps impact, business metrics",
                    "Organizational adoption — skills development, change management",
                    "AI observability — monitoring AI/ML systems themselves",
                    "Capstone: End-to-end AIOps platform with anomaly detection, LLM interface, and auto-remediation",
                    "Portfolio presentation — demonstrating AIOps capabilities to employers"
                ]
            }
        ],
        "duration": "16 weeks", "level": "Intermediate", "price": 219999, "original_price": 379999,
        "image_url": "https://images.unsplash.com/photo-1715079166921-af80e700d646?q=80&w=800&auto=format&fit=crop",
        "category": "Operations", "tags": ["Prometheus", "Grafana", "OpenTelemetry", "Kubernetes", "LLMs", "Ansible", "SRE"],
        "instructor": {"name": "Vikram Singh", "role": "SRE Lead", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=200&auto=format&fit=crop"},
        "highlights": ["LLM-powered incident management", "Self-healing Kubernetes", "ML anomaly detection", "Automated remediation with Ansible"]
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
    return {"message": "Squarerootz API is running"}

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
