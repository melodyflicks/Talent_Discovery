import os
import sys
from pathlib import Path

# Add backend directory to sys.path if run directly
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.domain import (
    Course,
    CourseRecommendation,
    EmployeeProfile,
    EmployeeSkill,
    ExternalProfile,
    LearningRoadmap,
    Role,
    RoleMatch,
    RoleSkill,
    Skill,
    SkillEvidence,
    SkillGap,
    User,
)
from app.services.employee_service import employee_service
from app.services.matching_service import matching_service
from app.services.gap_service import gap_service


def seed_database(db: Session = None):
    close_session = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        close_session = True

    try:
        print("[*] Starting Talent Discovery database seeding...")

        # 1. Seed 4 HR / Admin Accounts
        admin_pw = settings.default_admin_password or "CHANGE_ADMIN_PASSWORD"
        hr_pw = settings.default_hr_password or "CHANGE_HR_PASSWORD"

        admin_accounts = [
            ("admin1@talent.local", "System Administrator 1", "admin", admin_pw),
            ("admin2@talent.local", "System Administrator 2", "admin", admin_pw),
        ]
        hr_accounts = [
            ("hr1@talent.local", "Sarah Connor (HR Lead)", "hr", hr_pw),
            ("hr2@talent.local", "David Miller (HR Specialist)", "hr", hr_pw),
        ]

        for email, name, role, pw in admin_accounts + hr_accounts:
            existing = db.query(User).filter(User.email == email).first()
            if not existing:
                u = User(
                    email=email,
                    password_hash=hash_password(pw),
                    full_name=name,
                    role=role,
                    is_active=True,
                )
                db.add(u)
                print(f"  + Created {role.upper()} account: {email}")
            else:
                existing.password_hash = hash_password(pw)
                existing.full_name = name
                existing.role = role

        db.commit()

        # 2. Seed Skills Catalog
        skills_data = [
            # Engineering / Backend
            ("Python", "Backend Engineering", "Core Python programming, data structures, and async frameworks."),
            ("FastAPI", "Backend Engineering", "High-performance API framework for Python."),
            ("PostgreSQL", "Database & Storage", "Relational database modeling, query optimization, and indexing."),
            ("SQLAlchemy", "Backend Engineering", "Python SQL toolkit and Object Relational Mapper."),
            ("Docker", "Cloud & DevOps", "Containerization and local development orchestration."),
            ("Kubernetes", "Cloud & DevOps", "Container orchestration, scaling, and deployment management."),
            ("AWS", "Cloud & DevOps", "Amazon Web Services cloud architecture and services."),
            ("Go (Golang)", "Backend Engineering", "Concurrent backend systems and microservices."),
            # Frontend
            ("TypeScript", "Frontend Engineering", "Typed superset of JavaScript for scalable UI architecture."),
            ("React", "Frontend Engineering", "Component-based UI development and state management."),
            ("Next.js", "Frontend Engineering", "Full-stack React framework with SSR and API routes."),
            ("Tailwind CSS", "Frontend Engineering", "Utility-first CSS framework for rapid UI styling."),
            # Data & AI
            ("Machine Learning", "Data & AI", "Supervised and unsupervised learning, model evaluation."),
            ("PyTorch", "Data & AI", "Deep learning framework for computer vision and NLP."),
            ("Pandas & NumPy", "Data & AI", "Data manipulation, vectorized operations, and feature engineering."),
            ("Data Warehousing", "Data & AI", "Snowflake, BigQuery, dimensional data modeling."),
            ("Large Language Models", "Data & AI", "Prompt engineering, RAG architectures, and fine-tuning."),
            ("NLP", "Data & AI", "Natural Language Processing and text analytics."),
            # Product & Design
            ("Product Strategy", "Product & Management", "Roadmapping, prioritization frameworks, and OKRs."),
            ("UI/UX Design", "Design & UX", "User journeys, wireframing, design systems, and Figma."),
            ("Agile & Scrum", "Product & Management", "Sprint planning, backlog grooming, and team retrospectives."),
            ("User Research", "Design & UX", "Usability testing, customer interviews, and user personas."),
            # Security & Operations
            ("Cybersecurity", "Security & Reliability", "Vulnerability assessment, IAM policies, and threat modeling."),
            ("CI/CD Pipelines", "Cloud & DevOps", "Automated testing, build pipelines, and continuous deployment."),
        ]

        skill_map = {}
        for name, category, desc in skills_data:
            skill = db.query(Skill).filter(Skill.name == name).first()
            if not skill:
                skill = Skill(name=name, category=category, description=desc)
                db.add(skill)
                db.flush()
            skill_map[name] = skill

        print(f"  + Seeded {len(skill_map)} core taxonomy skills")
        db.commit()

        # 3. Seed Roles & Role Requirements
        roles_data = [
            {
                "title": "Senior Software Engineer",
                "department": "Engineering",
                "level": "Senior",
                "description": "Architects resilient microservices, mentors engineers, and drives backend standards.",
                "skills": [
                    ("Python", 4, "critical"),
                    ("FastAPI", 4, "critical"),
                    ("PostgreSQL", 4, "high"),
                    ("Docker", 3, "medium"),
                    ("AWS", 3, "medium"),
                    ("CI/CD Pipelines", 3, "medium"),
                ]
            },
            {
                "title": "Software Engineer",
                "department": "Engineering",
                "level": "Mid-Level",
                "description": "Develops APIs, builds features, and maintains database schemas.",
                "skills": [
                    ("Python", 3, "critical"),
                    ("PostgreSQL", 3, "high"),
                    ("FastAPI", 3, "high"),
                    ("Docker", 2, "medium"),
                ]
            },
            {
                "title": "ML Engineer",
                "department": "Data",
                "level": "Mid-to-Senior",
                "description": "Deploys ML models to production, maintains inference pipelines, and optimizes LLM workflows.",
                "skills": [
                    ("Python", 4, "critical"),
                    ("PyTorch", 4, "critical"),
                    ("Machine Learning", 4, "critical"),
                    ("Large Language Models", 3, "high"),
                    ("Docker", 3, "medium"),
                ]
            },
            {
                "title": "Data Scientist",
                "department": "Data",
                "level": "Mid-Level",
                "description": "Conducts statistical analysis, extracts predictive insights, and builds proof-of-concept models.",
                "skills": [
                    ("Python", 4, "critical"),
                    ("Pandas & NumPy", 4, "critical"),
                    ("Machine Learning", 3, "high"),
                    ("PostgreSQL", 3, "high"),
                ]
            },
            {
                "title": "Product Manager",
                "department": "Product",
                "level": "Senior",
                "description": "Drives product strategy, defines feature requirements, and coordinates cross-functional delivery.",
                "skills": [
                    ("Product Strategy", 4, "critical"),
                    ("Agile & Scrum", 4, "critical"),
                    ("User Research", 3, "high"),
                    ("UI/UX Design", 2, "medium"),
                ]
            },
            {
                "title": "UI/UX Designer",
                "department": "Design",
                "level": "Mid-Level",
                "description": "Designs modern interactive interfaces, prototypes workflows, and maintains design systems.",
                "skills": [
                    ("UI/UX Design", 4, "critical"),
                    ("User Research", 4, "critical"),
                    ("Tailwind CSS", 3, "medium"),
                ]
            },
            {
                "title": "DevOps Engineer",
                "department": "Engineering",
                "level": "Senior",
                "description": "Maintains cloud infrastructure, guarantees 99.9% uptime, and manages CI/CD pipelines.",
                "skills": [
                    ("Kubernetes", 4, "critical"),
                    ("AWS", 4, "critical"),
                    ("Docker", 4, "critical"),
                    ("CI/CD Pipelines", 4, "critical"),
                    ("Cybersecurity", 3, "high"),
                ]
            },
        ]

        role_map = {}
        for r_spec in roles_data:
            role = db.query(Role).filter(Role.title == r_spec["title"]).first()
            if not role:
                role = Role(
                    title=r_spec["title"],
                    department=r_spec["department"],
                    level=r_spec["level"],
                    description=r_spec["description"],
                    is_active=True,
                )
                db.add(role)
                db.flush()

                for s_name, req_prof, imp in r_spec["skills"]:
                    sk = skill_map.get(s_name)
                    if sk:
                        rs = RoleSkill(
                            role_id=role.id,
                            skill_id=sk.id,
                            required_proficiency=req_prof,
                            importance=imp,
                        )
                        db.add(rs)
            role_map[r_spec["title"]] = role

        print(f"  + Seeded {len(role_map)} organizational roles with skill requirements")
        db.commit()

        # 4. Seed Courses
        courses_data = [
            ("Advanced FastAPI & Microservices", "Coursera", "Master asynchronous Python, dependency injection, and scalable API architecture.", "FastAPI", "Advanced", "6 weeks", "https://coursera.org/learn/fastapi"),
            ("Production PostgreSQL Optimization", "Pluralsight", "Deep dive into query planning, explain analyze, and index tuning.", "PostgreSQL", "Intermediate", "4 weeks", "https://pluralsight.com/courses/postgresql-opt"),
            ("Deep Learning with PyTorch", "edX", "Build, train, and deploy neural networks for vision and NLP.", "PyTorch", "Intermediate", "8 weeks", "https://edx.org/learn/pytorch"),
            ("Production LLM Engineering & RAG", "Coursera", "Design retrieval-augmented generation systems and fine-tune open models.", "Large Language Models", "Advanced", "5 weeks", "https://coursera.org/learn/llm-rag"),
            ("Cloud Architecture with AWS & Terraform", "Udemy", "Implement high-availability cloud infrastructure with IAC.", "AWS", "Intermediate", "6 weeks", "https://udemy.com/course/aws-architect"),
            ("Kubernetes in Production", "Pluralsight", "Deploy, manage, and scale containerized clusters seamlessly.", "Kubernetes", "Advanced", "5 weeks", "https://pluralsight.com/courses/kubernetes-prod"),
            ("Product Strategy & OKR Mastery", "Coursera", "Develop high-growth product roadmaps and customer-centric value propositions.", "Product Strategy", "Intermediate", "4 weeks", "https://coursera.org/learn/product-strategy"),
            ("Modern UI/UX Design & Systems", "Udemy", "Design systems, auto-layout in Figma, and usability heuristics.", "UI/UX Design", "Beginner", "3 weeks", "https://udemy.com/course/modern-uiux"),
        ]

        course_map = {}
        for title, provider, desc, s_name, diff, dur, url in courses_data:
            course = db.query(Course).filter(Course.title == title).first()
            if not course:
                sk = skill_map.get(s_name)
                course = Course(
                    title=title,
                    provider=provider,
                    description=desc,
                    skill_id=sk.id if sk else None,
                    difficulty=diff,
                    duration=dur,
                    url=url,
                    is_active=True,
                )
                db.add(course)
                db.flush()
            course_map[title] = course

        print(f"  + Seeded {len(course_map)} learning courses")
        db.commit()

        # 5. Seed 12 Realistic Demo Employees
        demo_employees = [
            {
                "email": "alex.chen@talent.local",
                "full_name": "Alex Chen",
                "code": "EMP001",
                "department": "Engineering",
                "designation": "Software Engineer",
                "yoe": 3.5,
                "education": "B.S. in Computer Science, UC Berkeley",
                "location": "San Francisco, CA",
                "bio": "Backend software engineer passionate about clean architectures, distributed systems, and Python.",
                "skills": [
                    ("Python", 4, 0.95, "explicit", "GitHub PR reviews and production codebase commits"),
                    ("FastAPI", 3, 0.90, "explicit", "Built core internal microservice endpoints"),
                    ("PostgreSQL", 3, 0.85, "explicit", "Designed relational schemas for order tracking"),
                    ("Docker", 3, 0.80, "inferred", "Configured multi-stage container builds"),
                    ("AWS", 2, 0.70, "inferred", "Deployed ECS services via Terraform"),
                ]
            },
            {
                "email": "elena.rostova@talent.local",
                "full_name": "Elena Rostova",
                "code": "EMP002",
                "department": "Data",
                "designation": "Data Scientist",
                "yoe": 4.0,
                "education": "M.S. in Statistics, Stanford University",
                "location": "New York, NY",
                "bio": "Specializes in predictive modeling, statistical inference, and customer lifetime value algorithms.",
                "skills": [
                    ("Python", 4, 0.95, "explicit", "Authored data processing pipelines"),
                    ("Pandas & NumPy", 5, 0.98, "explicit", "5+ years of production data manipulation"),
                    ("Machine Learning", 4, 0.90, "explicit", "Deployed churn prediction models"),
                    ("PostgreSQL", 3, 0.85, "explicit", "Wrote complex analytical SQL queries"),
                    ("PyTorch", 2, 0.70, "inferred", "Completed experimental transformer notebooks"),
                ]
            },
            {
                "email": "marcus.vance@talent.local",
                "full_name": "Marcus Vance",
                "code": "EMP003",
                "department": "Engineering",
                "designation": "Senior Software Engineer",
                "yoe": 6.5,
                "education": "B.S. in Software Engineering, UT Austin",
                "location": "Austin, TX",
                "bio": "Lead backend developer experienced in high-throughput APIs, database tuning, and microservices.",
                "skills": [
                    ("Python", 5, 0.98, "explicit", "Core architect for core payment and user services"),
                    ("FastAPI", 4, 0.95, "explicit", "Built event-driven microservices handling 2M req/day"),
                    ("PostgreSQL", 4, 0.92, "explicit", "Managed database sharding and index strategy"),
                    ("Docker", 4, 0.90, "explicit", "Standardized developer container setups"),
                    ("AWS", 3, 0.85, "explicit", "Configured IAM, S3, RDS, and API Gateway"),
                    ("CI/CD Pipelines", 4, 0.90, "explicit", "Built GitHub Actions automated pipelines"),
                ]
            },
            {
                "email": "priya.sharma@talent.local",
                "full_name": "Priya Sharma",
                "code": "EMP004",
                "department": "Data",
                "designation": "ML Engineer",
                "yoe": 5.0,
                "education": "M.Tech in Artificial Intelligence, IIT Bombay",
                "location": "Seattle, WA",
                "bio": "Machine learning practitioner focused on LLMs, RAG applications, and production model serving.",
                "skills": [
                    ("Python", 5, 0.98, "explicit", "Primary development language for AI systems"),
                    ("PyTorch", 4, 0.92, "explicit", "Trained custom embeddings and semantic search models"),
                    ("Machine Learning", 4, 0.95, "explicit", "Deployed production recommendation systems"),
                    ("Large Language Models", 4, 0.90, "explicit", "Built RAG indexing pipeline with vector store"),
                    ("Docker", 3, 0.85, "explicit", "Containerized GPU inference workloads"),
                ]
            },
            {
                "email": "jordan.lee@talent.local",
                "full_name": "Jordan Lee",
                "code": "EMP005",
                "department": "Product",
                "designation": "Product Manager",
                "yoe": 4.5,
                "education": "MBA, Northwestern Kellogg",
                "location": "Chicago, IL",
                "bio": "Customer-obsessed product manager guiding B2B SaaS solutions from discovery to launch.",
                "skills": [
                    ("Product Strategy", 4, 0.95, "explicit", "Led roadmap execution for enterprise tiers"),
                    ("Agile & Scrum", 4, 0.92, "explicit", "Certified Scrum Product Owner (CSPO)"),
                    ("User Research", 3, 0.88, "explicit", "Conducted 50+ customer discovery interviews"),
                    ("UI/UX Design", 2, 0.70, "transferable", "Created wireframes for MVP feature releases"),
                ]
            },
            {
                "email": "hannah.kim@talent.local",
                "full_name": "Hannah Kim",
                "code": "EMP006",
                "department": "Design",
                "designation": "UI/UX Designer",
                "yoe": 3.0,
                "education": "B.A. in Interaction Design, RISD",
                "location": "New York, NY",
                "bio": "Visual and interaction designer dedicated to accessible, intuitive digital experiences.",
                "skills": [
                    ("UI/UX Design", 4, 0.95, "explicit", "Created and maintained company design system in Figma"),
                    ("User Research", 4, 0.90, "explicit", "Ran usability testing sessions and card sorts"),
                    ("Tailwind CSS", 2, 0.75, "inferred", "Collaborated with frontend developers on UI styling"),
                ]
            },
            {
                "email": "carlos.mendoza@talent.local",
                "full_name": "Carlos Mendoza",
                "code": "EMP007",
                "department": "Engineering",
                "designation": "DevOps Engineer",
                "yoe": 5.5,
                "education": "B.S. in Computer Systems, Georgia Tech",
                "location": "Atlanta, GA",
                "bio": "Cloud infrastructure automation specialist focused on Kubernetes, security, and developer velocity.",
                "skills": [
                    ("Kubernetes", 4, 0.95, "explicit", "Managed EKS clusters with ArgoCD"),
                    ("AWS", 4, 0.92, "explicit", "Certified AWS Solutions Architect"),
                    ("Docker", 5, 0.98, "explicit", "Optimized container build cache and base images"),
                    ("CI/CD Pipelines", 4, 0.95, "explicit", "Architected zero-downtime deployment pipelines"),
                    ("Cybersecurity", 3, 0.85, "explicit", "Implemented SOC2 compliance monitoring"),
                ]
            },
            {
                "email": "rachel.green@talent.local",
                "full_name": "Rachel Green",
                "code": "EMP008",
                "department": "Marketing",
                "designation": "Marketing Lead",
                "yoe": 4.0,
                "education": "B.A. in Communications, NYU",
                "location": "New York, NY",
                "bio": "Growth marketing lead driving brand positioning, content campaigns, and talent branding.",
                "skills": [
                    ("Product Strategy", 3, 0.80, "transferable", "Coordinated product go-to-market launches"),
                    ("User Research", 3, 0.85, "explicit", "Analyzed customer segments and demographics"),
                ]
            },
            {
                "email": "tariq.almansoor@talent.local",
                "full_name": "Tariq Al-Mansoor",
                "code": "EMP009",
                "department": "Engineering",
                "designation": "Frontend Engineer",
                "yoe": 3.0,
                "education": "B.S. in Computer Science, University of Michigan",
                "location": "Ann Arbor, MI",
                "bio": "Frontend developer building reactive, fluid dashboards using React and TypeScript.",
                "skills": [
                    ("React", 4, 0.95, "explicit", "Built main SPA dashboard"),
                    ("TypeScript", 4, 0.92, "explicit", "Migrated JavaScript codebase to strict TypeScript"),
                    ("Tailwind CSS", 4, 0.90, "explicit", "Styled responsive components"),
                    ("FastAPI", 2, 0.65, "inferred", "Contributed minor bug fixes to backend routers"),
                ]
            },
            {
                "email": "sophia.loring@talent.local",
                "full_name": "Sophia Loring",
                "code": "EMP010",
                "department": "Operations",
                "designation": "Operations Specialist",
                "yoe": 3.5,
                "education": "B.S. in Business Administration, Boston University",
                "location": "Boston, MA",
                "bio": "Process optimization specialist focused on internal workflows, tooling, and analytics.",
                "skills": [
                    ("Agile & Scrum", 3, 0.85, "explicit", "Managed operational sprints and vendor deliverables"),
                    ("PostgreSQL", 2, 0.70, "inferred", "Queried operational performance metrics"),
                ]
            },
            {
                "email": "liam.oconnor@talent.local",
                "full_name": "Liam O'Connor",
                "code": "EMP011",
                "department": "HR",
                "designation": "Talent Development Specialist",
                "yoe": 3.0,
                "education": "M.S. in Human Resources Management, Cornell University",
                "location": "Ithaca, NY",
                "bio": "Internal employee coaching and skill development coordinator.",
                "skills": [
                    ("User Research", 3, 0.80, "transferable", "Surveyed employee satisfaction and career goals"),
                    ("Agile & Scrum", 3, 0.75, "explicit", "Organized agile training workshops"),
                ]
            },
            {
                "email": "maya.patel@talent.local",
                "full_name": "Maya Patel",
                "code": "EMP012",
                "department": "Engineering",
                "designation": "Junior Software Engineer",
                "yoe": 1.5,
                "education": "B.S. in Information Systems, Purdue University",
                "location": "Indianapolis, IN",
                "bio": "Enthusiastic junior developer eager to master Python, databases, and backend APIs.",
                "skills": [
                    ("Python", 2, 0.85, "explicit", "Built utility scripts and unit test suites"),
                    ("FastAPI", 2, 0.80, "explicit", "Implemented CRUD endpoints under mentor guidance"),
                    ("PostgreSQL", 2, 0.75, "explicit", "Wrote basic SELECT and JOIN queries"),
                ]
            },
        ]

        default_emp_pw = "EmployeePassword123!"

        for emp_spec in demo_employees:
            user = db.query(User).filter(User.email == emp_spec["email"]).first()
            if not user:
                user = User(
                    email=emp_spec["email"],
                    password_hash=hash_password(default_emp_pw),
                    full_name=emp_spec["full_name"],
                    role="employee",
                    is_active=True,
                )
                db.add(user)
                db.flush()

            profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user.id).first()
            if not profile:
                profile = EmployeeProfile(
                    user_id=user.id,
                    employee_code=emp_spec["code"],
                    department=emp_spec["department"],
                    designation=emp_spec["designation"],
                    years_of_experience=emp_spec["yoe"],
                    education=emp_spec["education"],
                    location=emp_spec["location"],
                    bio=emp_spec["bio"],
                    resume_url=f"/resumes/{emp_spec['code'].lower()}_{emp_spec['full_name'].lower().replace(' ', '_')}.pdf",
                )
                db.add(profile)
                db.flush()

            # Ensure External Profile
            ext = db.query(ExternalProfile).filter(ExternalProfile.employee_id == profile.id).first()
            if not ext:
                gh_username = emp_spec["full_name"].lower().replace(" ", "").replace("'", "")
                ext = ExternalProfile(
                    employee_id=profile.id,
                    platform="github",
                    profile_url=f"https://github.com/{gh_username}",
                    username=gh_username,
                    raw_data={"public_repos": 14, "followers": 28}
                )
                db.add(ext)

            # Ensure Skills & Evidence
            for s_name, prof, conf, stype, ev_text in emp_spec["skills"]:
                sk = skill_map.get(s_name)
                if sk:
                    es = db.query(EmployeeSkill).filter(
                        EmployeeSkill.employee_id == profile.id,
                        EmployeeSkill.skill_id == sk.id
                    ).first()
                    if not es:
                        es = EmployeeSkill(
                            employee_id=profile.id,
                            skill_id=sk.id,
                            proficiency=prof,
                            confidence=conf,
                            skill_type=stype,
                            source="self-reported",
                        )
                        db.add(es)
                        db.flush()

                        evidence = SkillEvidence(
                            employee_skill_id=es.id,
                            source_type="project-contribution",
                            source_reference="enterprise-repo",
                            evidence_text=ev_text,
                            confidence=conf,
                        )
                        db.add(evidence)
                    else:
                        es.proficiency = prof
                        es.confidence = conf
                        es.skill_type = stype

            profile.profile_completion = employee_service.calculate_profile_completion(profile)

        db.commit()
        print(f"  + Seeded {len(demo_employees)} demo employee accounts and profiles")

        # 6. Generate Initial Matches, Gaps, Recommendations, and Roadmaps for each employee
        all_profiles = db.query(EmployeeProfile).all()
        for p in all_profiles:
            try:
                matching_service.generate_matches_for_employee(db, p.id)
                # Calculate gaps for top matched roles
                matches = db.query(RoleMatch).filter(RoleMatch.employee_id == p.id).all()
                for m in matches[:2]:
                    gap_service.calculate_and_sync_gaps(db, p.id, m.role_id)
                # Recommendations & Roadmap
                from app.services.recommendation_service import recommendation_service
                from app.services.roadmap_service import roadmap_service
                recommendation_service.get_recommendations_for_employee(db, p.id)
                roadmap_service.get_roadmap_for_employee(db, p.id)
            except Exception as e:
                print(f"  [WARN] Initializing metrics for employee {p.id}: {e}")

        db.commit()
        print("[OK] Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Database seeding failed: {e}")
        raise e
    finally:
        if close_session:
            db.close()


if __name__ == "__main__":
    seed_database()
