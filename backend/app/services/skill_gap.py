from typing import List, Dict, Any

ROADMAPS = {
    "Docker": {
        "steps": [
            "Container Concepts & Architecture",
            "Writing Dockerfile & Image Optimization",
            "Docker Compose & Multi-Container Apps",
            "Container Networking & Volume Persistence",
            "Docker in CI/CD Pipelines"
        ],
        "est_hours": 15,
        "difficulty": "Intermediate",
        "recommended_resource": "Docker Official Get Started Docs & Play with Docker"
    },
    "Kubernetes": {
        "steps": [
            "Pods, Services & Deployments Fundamentals",
            "ConfigMaps, Secrets & Ingress Controllers",
            "Helm Charts Package Management",
            "Cluster Observability & Scaling",
            "CKA Prep & Production Best Practices"
        ],
        "est_hours": 30,
        "difficulty": "Advanced",
        "recommended_resource": "Kubernetes.io Interactive Tutorials & Minikube"
    },
    "AWS": {
        "steps": [
            "Core Compute & Storage (EC2, S3, EBS)",
            "Networking & VPC Fundamentals",
            "IAM Roles, Policies & CloudTrail Security",
            "Databases: RDS, DynamoDB & ElastiCache",
            "Serverless Architecture (Lambda, API Gateway)"
        ],
        "est_hours": 25,
        "difficulty": "Intermediate",
        "recommended_resource": "AWS Skill Builder & Free Tier Hands-on Labs"
    },
    "Azure": {
        "steps": [
            "Azure Resource Manager & Portal Basics",
            "Virtual Machines & Azure App Services",
            "Azure Virtual Networks & Entra ID Security",
            "Azure SQL & Cosmos DB",
            "Azure DevOps & Pipelines Integration"
        ],
        "est_hours": 25,
        "difficulty": "Intermediate",
        "recommended_resource": "Microsoft Learn Azure Fundamentals Path (AZ-900)"
    },
    "GCP": {
        "steps": [
            "Compute Engine & Cloud Storage",
            "VPC Networks & Cloud IAM",
            "Cloud Run & Google Kubernetes Engine (GKE)",
            "BigQuery & Cloud Spanner",
            "Google Cloud Associate Engineer Track"
        ],
        "est_hours": 25,
        "difficulty": "Intermediate",
        "recommended_resource": "Google Cloud Skills Boost & Codelabs"
    },
    "PostgreSQL": {
        "steps": [
            "Relational Schema Design & Constraints",
            "Complex SQL Joins, Aggregations & CTEs",
            "Indexing Strategies (B-Tree, GIN) & Query EXPLAIN",
            "Transactions, ACID, & Locking mechanisms",
            "Connection Pooling & Performance Tuning"
        ],
        "est_hours": 18,
        "difficulty": "Intermediate",
        "recommended_resource": "PostgreSQL Exercises (pgexercises.com) & Official Docs"
    },
    "MongoDB": {
        "steps": [
            "Document Model vs Relational Databases",
            "CRUD Operations & Schema Validation",
            "Aggregation Pipeline Masterclass",
            "Indexes & Sharding Architecture",
            "Mongoose / Motor ODM Integration"
        ],
        "est_hours": 15,
        "difficulty": "Beginner-Intermediate",
        "recommended_resource": "MongoDB University Free Certification Courses"
    },
    "Redis": {
        "steps": [
            "In-Memory Data Structures (Strings, Hashes, Sets)",
            "Caching Patterns (Cache-Aside, Write-Through)",
            "Pub/Sub Messaging & Streams",
            "TTL, Eviction Policies & Persistence (RDB/AOF)",
            "Distributed Locks & Rate Limiting Implementation"
        ],
        "est_hours": 10,
        "difficulty": "Intermediate",
        "recommended_resource": "Redis University & Redis Docs"
    },
    "CI/CD": {
        "steps": [
            "Continuous Integration Principles",
            "GitHub Actions / GitLab CI Pipeline Syntax",
            "Automated Testing & Linting Gates",
            "Build Artifacts & Container Registry Publishing",
            "Blue-Green & Canary Deployment Strategies"
        ],
        "est_hours": 16,
        "difficulty": "Intermediate",
        "recommended_resource": "GitHub Actions Documentation & Quickstart"
    },
    "FastAPI": {
        "steps": [
            "Pydantic V2 Models & Type Annotations",
            "Dependency Injection System",
            "Asynchronous Endpoints & Database Sessions (Asyncpg)",
            "OAuth2 & JWT Authentication Flow",
            "Automated Swagger Docs & Production Deployment"
        ],
        "est_hours": 14,
        "difficulty": "Beginner-Intermediate",
        "recommended_resource": "FastAPI Official Tutorial by Tiangolo"
    },
    "React": {
        "steps": [
            "Component Lifecycle & JSX Fundamentals",
            "Hooks Mastery (useState, useEffect, useMemo, useCallback)",
            "State Management (Zustand / Redux Toolkit)",
            "Routing with React Router 6",
            "Performance Optimization & Tailwind CSS Styling"
        ],
        "est_hours": 22,
        "difficulty": "Intermediate",
        "recommended_resource": "react.dev (New Interactive React Documentation)"
    },
    "TypeScript": {
        "steps": [
            "Primitive & Object Types, Interfaces vs Types",
            "Generics & Utility Types (Partial, Record, Pick)",
            "Discriminated Unions & Type Narrowing",
            "TSConfig & Build Pipeline Integration",
            "Typing Full-Stack REST & GraphQL Contracts"
        ],
        "est_hours": 16,
        "difficulty": "Intermediate",
        "recommended_resource": "TypeScript Handbook & ExecuteProgram Courses"
    },
    "Machine Learning": {
        "steps": [
            "Data Preprocessing & Feature Engineering with Pandas/NumPy",
            "Supervised Learning: Regressors & Classifiers (Scikit-Learn)",
            "Unsupervised Learning: Clustering & Dimensionality Reduction",
            "Model Evaluation Metrics (ROC-AUC, Precision-Recall, F1)",
            "Hyperparameter Tuning & Cross-Validation"
        ],
        "est_hours": 35,
        "difficulty": "Intermediate-Advanced",
        "recommended_resource": "Coursera Andrew Ng Machine Learning Specialization"
    },
    "PyTorch": {
        "steps": [
            "Tensors, Autograd & Computational Graphs",
            "Building Neural Networks with nn.Module",
            "Custom Datasets & DataLoader Pipelines",
            "Training Loops, Loss Functions & Optimizers",
            "Transfer Learning & Fine-Tuning Vision/NLP Models"
        ],
        "est_hours": 28,
        "difficulty": "Advanced",
        "recommended_resource": "PyTorch Official 60-Minute Blitz Tutorials"
    },
    "GraphQL": {
        "steps": [
            "Schema Definition Language (SDL) & Types",
            "Queries, Mutations & Resolvers",
            "DataLoader for N+1 Query Problem Solution",
            "Subscriptions & Real-Time Updates",
            "Apollo Client / Server Integration"
        ],
        "est_hours": 14,
        "difficulty": "Intermediate",
        "recommended_resource": "HowToGraphQL.com Fullstack Tutorials"
    }
}


def analyze_skill_gaps(missing_skills: List[str]) -> List[Dict[str, Any]]:
    """Generate detailed actionable skill gap roadmaps."""
    gaps = []
    
    for skill in missing_skills:
        info = ROADMAPS.get(skill)
        if info:
            gaps.append({
                "skill": skill,
                "priority": "High" if skill in ["Docker", "Kubernetes", "AWS", "Python", "SQL", "React", "TypeScript"] else "Medium",
                "steps": info["steps"],
                "est_hours": info["est_hours"],
                "difficulty": info["difficulty"],
                "recommended_resource": info["recommended_resource"]
            })
        else:
            # Generic sensible roadmap for any other tech skill
            gaps.append({
                "skill": skill,
                "priority": "Medium",
                "steps": [
                    f"Core syntax and fundamentals of {skill}",
                    f"Building small practical hands-on projects with {skill}",
                    f"Best practices, error handling & testing in {skill}",
                    f"Integration into full-stack ecosystem"
                ],
                "est_hours": 12,
                "difficulty": "Intermediate",
                "recommended_resource": f"Official documentation and GitHub community guides for {skill}"
            })
            
    # Sort High priority first
    gaps.sort(key=lambda x: (0 if x["priority"] == "High" else 1, x["est_hours"]))
    return gaps


# Alias for backward compatibility / alternative naming
diagnose_skill_gaps = analyze_skill_gaps
