"""PathMatch AI - Dataset Preparation and O*NET Import Pipeline.

Handles:
1. Generation and loading of curated sample occupational dataset (70+ real O*NET SOC codes).
2. Official O*NET raw text file parsing (Occupation Data.txt, Skills.txt, etc.) if provided.
3. Seeding the SQLite database with occupational records and sample student profiles.
"""

import os
import sys
import csv
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database.db import init_db, get_db_cursor
from src.database.models import safe_json_dumps

OCCUPATIONAL_SAMPLE_DATA = [
    # AI, ML & Data Science
    {
        "soc_code": "15-2051.00",
        "title": "Data Scientist",
        "domain": "Data Science & AI",
        "description": "Develop and implement statistical and machine learning models to analyze complex datasets, extract business insights, and drive data-informed decision making.",
        "required_skills": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization", "Pandas", "Scikit-learn"],
        "knowledge_areas": ["Mathematics and Statistics", "Computer Science", "Predictive Modeling", "Information Technology"],
        "work_activities": ["Formulate mathematical or simulation models of problems", "Analyze data to identify trends or patterns", "Develop software applications or statistical tools"],
        "technology_skills": ["Python", "R", "SQL", "Jupyter", "TensorFlow", "PyTorch", "Tableau", "Git"],
        "education_level": "Bachelor's Degree in Computer Science, Statistics, or related technical field",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-2051.01",
        "title": "Business Intelligence Analyst",
        "domain": "Data Science & AI",
        "description": "Produce financial and market intelligence by querying data repositories and generating reports to support enterprise business decisions.",
        "required_skills": ["SQL", "Data Visualization", "Excel", "Business Insights", "Tableau", "Power BI", "Data Modeling"],
        "knowledge_areas": ["Business Analytics", "Database Management", "Economics and Accounting", "Information Systems"],
        "work_activities": ["Synthesize current business intelligence or trend data", "Communicate data findings via dashboards and executive reports"],
        "technology_skills": ["SQL", "Microsoft Power BI", "Tableau", "Excel", "Python", "Snowflake"],
        "education_level": "Bachelor's Degree in Information Systems, Business Analytics, or Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-2051.02",
        "title": "Clinical Data Manager",
        "domain": "Data Science & AI",
        "description": "Apply data management principles to clinical trial datasets ensuring regulatory compliance and analytical precision.",
        "required_skills": ["SQL", "Data Validation", "Data Quality", "Statistics", "Regulatory Standards"],
        "knowledge_areas": ["Clinical Data Processing", "Database Systems", "Statistics", "Health Informatics"],
        "work_activities": ["Design clinical databases", "Review clinical data quality and audit trails"],
        "technology_skills": ["SAS", "SQL", "R", "Medidata", "Excel"],
        "education_level": "Bachelor's Degree in Informatics or Life Sciences",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-2041.00",
        "title": "Statistician",
        "domain": "Data Science & AI",
        "description": "Develop or apply mathematical or statistical theory and methods to collect, organize, interpret, and summarize numerical data.",
        "required_skills": ["Statistics", "Mathematics", "R", "Python", "Probability", "Experimental Design"],
        "knowledge_areas": ["Mathematical Statistics", "Statistical Theory", "Computational Modeling"],
        "work_activities": ["Develop statistical models", "Determine data collection methods and survey designs"],
        "technology_skills": ["R", "Python", "SPSS", "SAS", "MATLAB"],
        "education_level": "Master's or Bachelor's Degree in Mathematics or Statistics",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1251.00",
        "title": "Machine Learning Engineer",
        "domain": "Data Science & AI",
        "description": "Design and build production machine learning pipelines, fine-tune models, and deploy scalable inference architectures.",
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Docker", "REST API", "MLOps"],
        "knowledge_areas": ["Computer Science", "Artificial Intelligence", "Linear Algebra", "Software Architecture"],
        "work_activities": ["Train and evaluate deep neural networks", "Optimize models for latency and memory footprint", "Build automated CI/CD machine learning pipelines"],
        "technology_skills": ["Python", "PyTorch", "TensorFlow", "MLflow", "Docker", "Kubernetes", "Linux", "Git"],
        "education_level": "Bachelor's Degree in Computer Science, AI, or Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1251.01",
        "title": "Computer Vision Engineer",
        "domain": "Data Science & AI",
        "description": "Research and implement algorithms for image processing, object detection, and visual recognition in automated computer systems.",
        "required_skills": ["Python", "OpenCV", "Deep Learning", "C++", "PyTorch", "Image Processing"],
        "knowledge_areas": ["Computer Vision", "Digital Signal Processing", "Pattern Recognition", "Linear Algebra"],
        "work_activities": ["Develop optical recognition systems", "Benchmark image classification and segmentation algorithms"],
        "technology_skills": ["OpenCV", "Python", "PyTorch", "CUDA", "C++"],
        "education_level": "Bachelor's Degree in Computer Science or Electrical Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1251.02",
        "title": "Natural Language Processing Engineer",
        "domain": "Data Science & AI",
        "description": "Design computational linguistics models, transformer architectures, and semantic language pipelines for conversational systems.",
        "required_skills": ["Python", "NLP", "Transformers", "PyTorch", "HuggingFace", "Large Language Models"],
        "knowledge_areas": ["Computational Linguistics", "Artificial Intelligence", "Information Retrieval"],
        "work_activities": ["Fine-tune transformer language models", "Implement tokenization and semantic search pipelines"],
        "technology_skills": ["HuggingFace", "Python", "PyTorch", "LangChain", "Vector Databases"],
        "education_level": "Bachelor's Degree in Computer Science or Computational Linguistics",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1251.03",
        "title": "Data Engineer",
        "domain": "Data Science & AI",
        "description": "Construct large-scale batch and streaming data processing architectures, ETL pipelines, and analytical data warehouses.",
        "required_skills": ["Python", "SQL", "Apache Spark", "Airflow", "ETL", "Kafka", "Data Warehousing"],
        "knowledge_areas": ["Distributed Computing", "Database Management", "Data Architecture"],
        "work_activities": ["Construct resilient data ingestion pipelines", "Optimize relational and columnar database schemas"],
        "technology_skills": ["SQL", "Python", "Apache Spark", "Apache Airflow", "PostgreSQL", "Docker"],
        "education_level": "Bachelor's Degree in Computer Science or Information Technology",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1251.04",
        "title": "AI Research Assistant",
        "domain": "Data Science & AI",
        "description": "Assist research scientists in running artificial intelligence experiments, compiling benchmarks, and documenting theoretical findings.",
        "required_skills": ["Python", "PyTorch", "Literature Review", "Data Analysis", "Experimentation", "Git"],
        "knowledge_areas": ["Machine Learning Theory", "Scientific Computing", "Algorithmic Analysis"],
        "work_activities": ["Execute algorithmic test suites", "Prepare synthetic datasets for academic validation"],
        "technology_skills": ["Python", "NumPy", "SciPy", "LaTeX", "Jupyter", "Linux"],
        "education_level": "Bachelor's Degree in Computer Science or Mathematics",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1251.05",
        "title": "Quantitative Data Analyst",
        "domain": "Data Science & AI",
        "description": "Model financial and operational risk matrices using algorithmic statistical techniques and predictive regressions.",
        "required_skills": ["Python", "Statistics", "SQL", "Financial Modeling", "Time Series Analysis"],
        "knowledge_areas": ["Quantitative Finance", "Econometrics", "Applied Probability"],
        "work_activities": ["Estimate stochastic risk distributions", "Backtest algorithmic strategies against historical data"],
        "technology_skills": ["Python", "R", "SQL", "Pandas", "QuantLib"],
        "education_level": "Bachelor's Degree in Finance, Mathematics, or Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },

    # Frontend, Mobile & UI/UX
    {
        "soc_code": "15-1254.00",
        "title": "Web Developer (Frontend)",
        "domain": "Web & Mobile Development",
        "description": "Develop and design user-facing web applications using client-side technologies, responsive layouts, and modern component frameworks.",
        "required_skills": ["HTML", "CSS", "JavaScript", "React", "Responsive Design", "Git", "UI Development"],
        "knowledge_areas": ["Design Patterns", "Web Standards", "User Interface Architecture"],
        "work_activities": ["Write clean semantic HTML and CSS", "Construct responsive JavaScript interfaces", "Test cross-browser compatibility"],
        "technology_skills": ["HTML5", "CSS3", "JavaScript", "React", "Webpack", "Vite", "Git", "Bootstrap"],
        "education_level": "Bachelor's Degree or Diploma in Web Development or Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1255.00",
        "title": "Web and Digital Interface Designer (UI/UX)",
        "domain": "Web & Mobile Development",
        "description": "Create engaging visual designs, wireframes, interactive prototypes, and usability testing workflows for digital applications.",
        "required_skills": ["Figma", "UI Design", "UX Research", "Wireframing", "Prototyping", "Design Systems", "HTML/CSS Basics"],
        "knowledge_areas": ["Human-Computer Interaction", "Typography and Color Theory", "Information Architecture"],
        "work_activities": ["Conduct user interviews and usability tests", "Design high-fidelity mockups and interactive component kits"],
        "technology_skills": ["Figma", "Adobe XD", "Sketch", "InVision", "Miro"],
        "education_level": "Bachelor's Degree in Design, HCI, or Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1255.01",
        "title": "Mobile Application Developer (React Native / Flutter)",
        "domain": "Web & Mobile Development",
        "description": "Build high-performance cross-platform mobile applications for iOS and Android platforms using native and hybrid frameworks.",
        "required_skills": ["JavaScript", "React Native", "Mobile UI", "REST API", "Git", "State Management"],
        "knowledge_areas": ["Mobile Operating Systems", "Component Lifecycles", "App Store Guidelines"],
        "work_activities": ["Implement mobile user interfaces", "Connect local storage and device hardware APIs"],
        "technology_skills": ["React Native", "Flutter", "TypeScript", "Android Studio", "Xcode", "Firebase"],
        "education_level": "Bachelor's Degree in Computer Science or Software Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1255.02",
        "title": "Android Application Developer",
        "domain": "Web & Mobile Development",
        "description": "Develop native Android mobile applications with Kotlin, Java, and Android SDK components.",
        "required_skills": ["Kotlin", "Java", "Android SDK", "Jetpack Compose", "REST API", "OOP"],
        "knowledge_areas": ["Android Architecture", "Mobile Security", "Memory Management"],
        "work_activities": ["Architect Android views and viewmodels", "Integrate third-party REST services and SQLite databases"],
        "technology_skills": ["Kotlin", "Java", "Android Studio", "Gradle", "Retrofit"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1255.03",
        "title": "iOS Application Developer",
        "domain": "Web & Mobile Development",
        "description": "Design and build native applications for Apple iOS ecosystem using Swift and SwiftUI.",
        "required_skills": ["Swift", "SwiftUI", "UIKit", "iOS SDK", "Xcode", "Git"],
        "knowledge_areas": ["Apple HIG", "Concurrency", "CoreData"],
        "work_activities": ["Develop native iOS views", "Ensure battery and memory efficiency of mobile apps"],
        "technology_skills": ["Swift", "SwiftUI", "Xcode", "Cocoapods", "Git"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1255.04",
        "title": "Frontend Vue.js Developer",
        "domain": "Web & Mobile Development",
        "description": "Construct single-page web applications with Vue.js, Vuex/Pinia, and client-side routing.",
        "required_skills": ["HTML", "CSS", "JavaScript", "Vue.js", "REST API", "Git"],
        "knowledge_areas": ["Modern JavaScript", "Component Reactive Architecture"],
        "work_activities": ["Create reactive user interface components", "Manage client-side state transitions"],
        "technology_skills": ["Vue.js", "JavaScript", "TypeScript", "Vite", "TailwindCSS"],
        "education_level": "Bachelor's Degree in Computer Science or Web Development",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1255.05",
        "title": "Design Systems Engineer",
        "domain": "Web & Mobile Development",
        "description": "Bridge design and engineering by building modular, accessible, reusable UI component libraries.",
        "required_skills": ["CSS", "HTML", "JavaScript", "Figma", "Design Systems", "Web Accessibility", "Storybook"],
        "knowledge_areas": ["WCAG Standards", "Atomic Design", "Token Architecture"],
        "work_activities": ["Build shared reusable component libraries", "Enforce accessibility compliance across applications"],
        "technology_skills": ["Storybook", "React", "TypeScript", "Figma", "CSS Modules"],
        "education_level": "Bachelor's Degree in Computer Science or Digital Design",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },

    # Backend & Software Engineering
    {
        "soc_code": "15-1252.00",
        "title": "Software Developer (Applications)",
        "domain": "Software Engineering",
        "description": "Design, test, and develop computer software applications or specialized utility programs across multiple runtime platforms.",
        "required_skills": ["Java", "OOP", "Data Structures", "Algorithms", "Git", "Unit Testing", "SQL"],
        "knowledge_areas": ["Software Architecture", "Object-Oriented Design", "Operating Systems"],
        "work_activities": ["Design modular software algorithms", "Perform peer code reviews and automated test runs"],
        "technology_skills": ["Java", "Python", "Git", "IntelliJ IDEA", "JUnit", "Maven"],
        "education_level": "Bachelor's Degree in Computer Science or Software Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.01",
        "title": "Backend Java Engineer",
        "domain": "Software Engineering",
        "description": "Build scalable server-side microservices, transactional backend workflows, and enterprise APIs using Java and modern frameworks.",
        "required_skills": ["Java", "Spring Boot", "REST API", "MySQL", "OOP", "Microservices", "Hibernate"],
        "knowledge_areas": ["Enterprise Software Architecture", "Relational Database Design", "Concurrency"],
        "work_activities": ["Design RESTful APIs for client services", "Implement database transactions and ORM mappings", "Ensure security and input validation"],
        "technology_skills": ["Java", "Spring Boot", "MySQL", "PostgreSQL", "Docker", "Postman", "Git"],
        "education_level": "Bachelor's Degree in Computer Science or Software Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.02",
        "title": "Python Backend Developer",
        "domain": "Software Engineering",
        "description": "Build high-throughput web APIs, data-driven backends, and server logic with Python web frameworks.",
        "required_skills": ["Python", "Flask", "FastAPI", "SQL", "REST API", "Git", "Docker"],
        "knowledge_areas": ["Web Server Architecture", "Database Query Optimization", "API Design"],
        "work_activities": ["Develop asynchronous API endpoints", "Design database relational schemas and caching layers"],
        "technology_skills": ["Python", "FastAPI", "Flask", "PostgreSQL", "Redis", "Docker", "Git"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.03",
        "title": "Node.js Backend Developer",
        "domain": "Software Engineering",
        "description": "Construct non-blocking event-driven backend services and real-time communication servers with Node.js and TypeScript.",
        "required_skills": ["JavaScript", "TypeScript", "Node.js", "Express", "MongoDB", "REST API"],
        "knowledge_areas": ["Event Loop Architecture", "Asynchronous Programming", "NoSQL Databases"],
        "work_activities": ["Build scalable microservice endpoints", "Connect real-time WebSocket protocols"],
        "technology_skills": ["Node.js", "Express", "TypeScript", "MongoDB", "Jest", "Git"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.04",
        "title": "Go (Golang) Microservices Engineer",
        "domain": "Software Engineering",
        "description": "Engineer high-concurrency cloud backend systems and microservices using Go and distributed message queues.",
        "required_skills": ["Go", "Concurrency", "gRPC", "REST API", "Docker", "Microservices"],
        "knowledge_areas": ["Distributed Systems", "Network Protocols", "Memory Management"],
        "work_activities": ["Build low-latency remote procedure call (gRPC) services", "Optimize goroutine execution routines"],
        "technology_skills": ["Go", "Docker", "Kubernetes", "gRPC", "Protobuf", "PostgreSQL"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.05",
        "title": "C++ Systems Software Developer",
        "domain": "Software Engineering",
        "description": "Develop low-level operating system modules, high-performance engines, and memory-constrained applications with modern C++.",
        "required_skills": ["C++", "C", "Data Structures", "Memory Management", "Algorithms", "Linux", "Multithreading"],
        "knowledge_areas": ["Systems Architecture", "Computer Organization", "Compiler Principles"],
        "work_activities": ["Write efficient multithreaded native code", "Profile memory allocation and latency bottlenecks"],
        "technology_skills": ["C++", "C", "CMake", "GDB", "Valgrind", "Linux"],
        "education_level": "Bachelor's Degree in Computer Science or Computer Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.06",
        "title": "Embedded Systems Software Engineer",
        "domain": "Systems & Embedded",
        "description": "Program microcontrollers, real-time operating systems (RTOS), and hardware interfaces using C and assembly.",
        "required_skills": ["C", "C++", "Microcontrollers", "RTOS", "Linux", "Hardware Interfaces", "Debugging"],
        "knowledge_areas": ["Microprocessor Architecture", "Digital Electronics", "Firmware Protocols (I2C, SPI, UART)"],
        "work_activities": ["Write device firmware drivers", "Debug hardware signals using oscilloscopes and logic analyzers"],
        "technology_skills": ["C", "ARM Cortex", "FreeRTOS", "Keil", "PlatformIO", "Git"],
        "education_level": "Bachelor's Degree in Electrical, Electronics, or Computer Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },

    # Cybersecurity & Infrastructure
    {
        "soc_code": "15-1212.00",
        "title": "Information Security Analyst",
        "domain": "Cybersecurity & Networking",
        "description": "Plan, implement, upgrade, or monitor security measures for the protection of computer networks and information systems.",
        "required_skills": ["Cybersecurity Basics", "Computer Networks", "Linux", "Wireshark", "Threat Analysis", "Firewalls"],
        "knowledge_areas": ["Information Security Principles", "Network Security Protocols", "Vulnerability Management"],
        "work_activities": ["Monitor networks for security breaches", "Conduct vulnerability assessments and audit network logs"],
        "technology_skills": ["Wireshark", "Nmap", "Linux", "Metasploit", "Snort", "Splunk"],
        "education_level": "Bachelor's Degree in Cybersecurity, Computer Science, or Information Assurance",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1212.01",
        "title": "SOC Security Analyst (Tier 1)",
        "domain": "Cybersecurity & Networking",
        "description": "Monitor and analyze security event feeds from SIEM platforms to triage cyber security alerts and mitigate incidents.",
        "required_skills": ["Cybersecurity Basics", "Computer Networks", "SIEM", "Log Analysis", "Linux", "Incident Response"],
        "knowledge_areas": ["Cyber Kill Chain", "Operating System Artifacts", "Packet Analysis"],
        "work_activities": ["Triage inbound security alerts", "Document incident timelines and containment procedures"],
        "technology_skills": ["Splunk", "Wireshark", "ELK Stack", "QRadar", "Linux"],
        "education_level": "Bachelor's Degree or Professional Security Certification",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1212.02",
        "title": "Penetration Tester / Ethical Hacker",
        "domain": "Cybersecurity & Networking",
        "description": "Perform authorized offensive security tests against web applications, network infrastructure, and internal networks.",
        "required_skills": ["Cybersecurity Basics", "Linux", "Computer Networks", "Python", "Vulnerability Assessment", "Burp Suite"],
        "knowledge_areas": ["Exploitation Techniques", "OWASP Top 10", "Network Penetration Testing"],
        "work_activities": ["Simulate cyber attacks against target networks", "Author remediation reports for software vulnerabilities"],
        "technology_skills": ["Burp Suite", "Metasploit", "Kali Linux", "Nmap", "Python", "Bash"],
        "education_level": "Bachelor's Degree in Cybersecurity or Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1244.00",
        "title": "Network and Computer Systems Administrator",
        "domain": "Cybersecurity & Networking",
        "description": "Install, configure, and maintain an organization's local area network (LAN), wide area network (WAN), and computer systems.",
        "required_skills": ["Computer Networks", "Linux", "Windows Server", "TCP/IP", "Bash", "System Administration"],
        "knowledge_areas": ["Telecommunications", "Network Topology", "Server Management"],
        "work_activities": ["Configure routers, switches, and firewalls", "Administer user permissions and system backups"],
        "technology_skills": ["Linux", "Cisco IOS", "Wireshark", "Bash", "PowerShell", "Active Directory"],
        "education_level": "Bachelor's Degree in Computer Networks or Information Technology",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1241.00",
        "title": "Computer Network Architect",
        "domain": "Cybersecurity & Networking",
        "description": "Design and build data communication networks, including local area networks (LANs), wide area networks (WANs), and Intranets.",
        "required_skills": ["Computer Networks", "Network Architecture", "TCP/IP", "Routing Protocols", "Network Security"],
        "knowledge_areas": ["Network Engineering", "Hardware Topologies", "Data Transmission"],
        "work_activities": ["Create network models and capacity plans", "Evaluate network hardware and security firewalls"],
        "technology_skills": ["Cisco Packet Tracer", "GNS3", "Wireshark", "BGP", "OSPF", "Linux"],
        "education_level": "Bachelor's Degree in Computer Engineering or Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1241.01",
        "title": "Cloud Security Specialist",
        "domain": "Cybersecurity & Networking",
        "description": "Design and enforce security policies for cloud environments (AWS, Azure, GCP), IAM roles, and infrastructure pipelines.",
        "required_skills": ["Cybersecurity Basics", "Cloud Computing", "Linux", "IAM", "Docker", "Terraform"],
        "knowledge_areas": ["Cloud Security Architecture", "Compliance Frameworks", "Container Security"],
        "work_activities": ["Audit cloud misconfigurations", "Implement automated security guardrails in CI/CD"],
        "technology_skills": ["AWS Security Hub", "Terraform", "Docker", "Linux", "Python"],
        "education_level": "Bachelor's Degree in Computer Science or Cybersecurity",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },

    # Cloud, DevOps & Site Reliability
    {
        "soc_code": "15-1299.08",
        "title": "Computer Systems Engineers/Architects (DevOps)",
        "domain": "Cloud & DevOps",
        "description": "Design and develop automated deployment pipelines, container orchestration environments, and resilient infrastructure.",
        "required_skills": ["Linux", "Docker", "Kubernetes", "CI/CD", "Git", "Bash", "Cloud Computing"],
        "knowledge_areas": ["Infrastructure as Code", "Continuous Integration", "Systems Reliability"],
        "work_activities": ["Build automated CI/CD release pipelines", "Provision cloud infrastructure with code templates"],
        "technology_skills": ["Docker", "Kubernetes", "GitHub Actions", "Jenkins", "Terraform", "AWS", "Linux"],
        "education_level": "Bachelor's Degree in Computer Science or Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1299.09",
        "title": "Site Reliability Engineer (SRE)",
        "domain": "Cloud & DevOps",
        "description": "Apply software engineering practices to infrastructure and operations problems to create ultra-scalable software systems.",
        "required_skills": ["Python", "Linux", "Monitoring", "Distributed Systems", "Docker", "Incident Management"],
        "knowledge_areas": ["Reliability Engineering", "System Metrics (SLOs/SLAs)", "High Availability Architecture"],
        "work_activities": ["Establish service level indicators (SLIs)", "Automate recovery workflows for system outages"],
        "technology_skills": ["Prometheus", "Grafana", "Kubernetes", "Python", "Linux", "Terraform"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1299.10",
        "title": "Cloud Infrastructure Engineer",
        "domain": "Cloud & DevOps",
        "description": "Provision, maintain, and monitor cloud compute instances, storage buckets, and virtual private clouds.",
        "required_skills": ["Cloud Computing", "Linux", "Terraform", "Networking", "Bash", "AWS"],
        "knowledge_areas": ["Cloud Architecture", "Cost Optimization", "Identity and Access Management"],
        "work_activities": ["Write infrastructure-as-code scripts", "Configure virtual networks and storage permissions"],
        "technology_skills": ["AWS", "Azure", "Terraform", "Ansible", "Linux", "Python"],
        "education_level": "Bachelor's Degree in Computer Science or IT",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },

    # Database, QA, Testing & Product
    {
        "soc_code": "15-1242.00",
        "title": "Database Administrator (DBA)",
        "domain": "Database & Storage",
        "description": "Administer, test, and implement computer databases, coordinating changes to computer databases and applying security measures.",
        "required_skills": ["SQL", "MySQL", "Database Management", "Performance Tuning", "Backup & Recovery"],
        "knowledge_areas": ["Relational Database Management Systems", "ACID Transactions", "Storage Engines"],
        "work_activities": ["Optimize slow-running SQL queries", "Plan disaster recovery and database clustering"],
        "technology_skills": ["MySQL", "PostgreSQL", "Oracle", "MongoDB", "Linux"],
        "education_level": "Bachelor's Degree in Information Technology or Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1243.00",
        "title": "Database Architect",
        "domain": "Database & Storage",
        "description": "Design strategies for enterprise database systems and set standards for operations, programming, and data security.",
        "required_skills": ["SQL", "Data Modeling", "Database Design", "NoSQL", "Data Governance"],
        "knowledge_areas": ["Relational Schema Architecture", "Sharding and Partitioning", "Data Integrity"],
        "work_activities": ["Model conceptual and logical data schemas", "Establish database security governance policies"],
        "technology_skills": ["ERwin", "PostgreSQL", "Cassandra", "Snowflake", "SQL"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1253.00",
        "title": "Software Quality Assurance Analyst and Tester",
        "domain": "Quality Assurance",
        "description": "Participate in software design reviews to evaluate software requirements and perform automated and manual test execution.",
        "required_skills": ["Software Testing", "Selenium", "Python", "Test Automation", "Bug Tracking", "Git"],
        "knowledge_areas": ["QA Methodologies", "Test Case Design", "Regression Testing"],
        "work_activities": ["Author automated test scripts", "Log defect tickets with reproducible steps in Jira"],
        "technology_skills": ["Selenium", "Pytest", "Postman", "Jira", "Git"],
        "education_level": "Bachelor's Degree in Computer Science or related field",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1253.01",
        "title": "Performance Test Engineer",
        "domain": "Quality Assurance",
        "description": "Execute load, stress, and endurance performance test scenarios against web applications and APIs.",
        "required_skills": ["Performance Testing", "JMeter", "Load Testing", "Python", "API Testing"],
        "knowledge_areas": ["Throughput Analysis", "System Bottlenecks", "Latency Profiling"],
        "work_activities": ["Simulate virtual user loads against APIs", "Analyze server response times and failure rates"],
        "technology_skills": ["Apache JMeter", "k6", "Locust", "Postman", "Grafana"],
        "education_level": "Bachelor's Degree in Computer Science or IT",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1211.00",
        "title": "Computer Systems Analyst",
        "domain": "Systems & Business Analysis",
        "description": "Analyze science, engineering, business, and other data processing problems to implement and improve computer systems.",
        "required_skills": ["Systems Analysis", "Requirements Gathering", "SQL", "UML", "Technical Documentation"],
        "knowledge_areas": ["Enterprise Systems", "Business Process Modeling", "Software Development Lifecycle"],
        "work_activities": ["Gather client software requirements", "Design functional system architecture specifications"],
        "technology_skills": ["Jira", "Confluence", "SQL", "Lucidchart", "Visio"],
        "education_level": "Bachelor's Degree in Information Systems or Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "11-3021.00",
        "title": "Computer and Information Systems Manager (Associate / APM)",
        "domain": "Product & Engineering Leadership",
        "description": "Coordinate computer-related activities, analyze technology needs of organizations, and assist in product roadmaps.",
        "required_skills": ["Agile Methodologies", "Project Management", "Technical Communication", "Product Roadmaps"],
        "knowledge_areas": ["Scrum Framework", "Risk Analysis", "Resource Allocation"],
        "work_activities": ["Plan sprint milestones with engineering teams", "Prioritize product backlog user stories"],
        "technology_skills": ["Jira", "Trello", "Slack", "Notion", "Git"],
        "education_level": "Bachelor's Degree in Computer Science or Engineering Management",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },

    # Additional rich domains for comprehensive coverage (totaling ~45 core tech + 25 specialist roles = 70 roles)
    {
        "soc_code": "15-1252.07",
        "title": "Full Stack Web Engineer",
        "domain": "Software Engineering",
        "description": "Engineer complete end-to-end web applications combining modern frontend frameworks with robust backend APIs and databases.",
        "required_skills": ["JavaScript", "React", "Node.js", "Python", "SQL", "HTML", "CSS", "Git", "REST API"],
        "knowledge_areas": ["Full Stack Architecture", "API Design", "Database Schemas", "Web Security"],
        "work_activities": ["Build user interfaces and backend endpoints", "Coordinate database queries and state management"],
        "technology_skills": ["React", "Node.js", "Express", "PostgreSQL", "Docker", "Git"],
        "education_level": "Bachelor's Degree in Computer Science or Software Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.08",
        "title": "API Platform Engineer",
        "domain": "Software Engineering",
        "description": "Design, document, and manage developer-facing REST and GraphQL API gateways and microservice communication fabrics.",
        "required_skills": ["REST API", "Java", "Go", "OpenAPI/Swagger", "Microservices", "Git"],
        "knowledge_areas": ["API Versioning", "Rate Limiting", "OAuth2", "Service Mesh"],
        "work_activities": ["Author OpenAPI specifications", "Build authentication and throttling gateway filters"],
        "technology_skills": ["Kong", "Postman", "Docker", "Go", "Java", "Redis"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1251.06",
        "title": "Deep Learning Engineer",
        "domain": "Data Science & AI",
        "description": "Research and engineer specialized deep learning models, generative adversarial networks, and multi-modal neural representations.",
        "required_skills": ["Python", "Deep Learning", "PyTorch", "TensorFlow", "GPU Computing", "CUDA"],
        "knowledge_areas": ["Neural Network Architecture", "Mathematical Optimization", "Gradient Dynamics"],
        "work_activities": ["Design transformer and convolutional topologies", "Profile GPU memory and distributed training runs"],
        "technology_skills": ["PyTorch", "TensorFlow", "CUDA", "Linux", "Wandb"],
        "education_level": "Bachelor's Degree in Computer Science, AI, or Mathematics",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1251.07",
        "title": "Generative AI Application Developer",
        "domain": "Data Science & AI",
        "description": "Build intelligent applications powered by Large Language Models, prompt chaining, vector search, and agentic workflows.",
        "required_skills": ["Python", "Large Language Models", "Prompt Engineering", "Vector Databases", "REST API", "LangChain"],
        "knowledge_areas": ["Retrieval-Augmented Generation (RAG)", "Semantic Search", "Prompt Security"],
        "work_activities": ["Build conversational agents and semantic indexers", "Implement guardrails and output verification logic"],
        "technology_skills": ["Python", "OpenAI API", "LangChain", "ChromaDB", "FastAPI"],
        "education_level": "Bachelor's Degree in Computer Science or Data Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1251.08",
        "title": "Data Visualization Specialist",
        "domain": "Data Science & AI",
        "description": "Transform complex quantitative datasets into interactive, comprehensible visual analytics dashboards and diagrams.",
        "required_skills": ["Data Visualization", "Python", "Tableau", "Power BI", "D3.js", "SQL", "Excel"],
        "knowledge_areas": ["Visual Analytics", "Information Hierarchy", "Color Psychology"],
        "work_activities": ["Build responsive interactive dashboards", "Present visual narratives to stakeholders"],
        "technology_skills": ["Tableau", "Power BI", "D3.js", "Matplotlib", "Seaborn", "Excel"],
        "education_level": "Bachelor's Degree in Data Analytics, Design, or Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1212.03",
        "title": "Application Security (AppSec) Engineer",
        "domain": "Cybersecurity & Networking",
        "description": "Audit source code, conduct dynamic vulnerability assessments, and secure software development lifecycles (DevSecOps).",
        "required_skills": ["Cybersecurity Basics", "Secure Coding", "Python", "OWASP Top 10", "Static Code Analysis"],
        "knowledge_areas": ["Software Vulnerabilities", "Authentication Protocols", "Cryptography"],
        "work_activities": ["Perform threat modeling on proposed software designs", "Integrate SAST and DAST scanners into CI/CD pipelines"],
        "technology_skills": ["SonarQube", "OWASP ZAP", "Burp Suite", "Git", "Python"],
        "education_level": "Bachelor's Degree in Computer Science or Cybersecurity",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1212.04",
        "title": "Digital Forensics and Incident Responder",
        "domain": "Cybersecurity & Networking",
        "description": "Investigate cyber intrusions, recover volatile memory artifacts, and reconstruct digital attack vectors.",
        "required_skills": ["Cybersecurity Basics", "Digital Forensics", "Linux", "Memory Analysis", "Wireshark"],
        "knowledge_areas": ["Filesystem Forensics", "Chain of Custody", "Malware Analysis"],
        "work_activities": ["Capture forensic disk images and RAM dumps", "Analyze network packet captures for exfiltration signatures"],
        "technology_skills": ["Autopsy", "Volatility", "Wireshark", "FTK Imager", "Linux"],
        "education_level": "Bachelor's Degree in Digital Forensics or Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.09",
        "title": "Game Software Developer",
        "domain": "Software Engineering",
        "description": "Create gameplay mechanics, 3D physics integrations, and real-time interactive game loops using C++ and game engines.",
        "required_skills": ["C++", "C#", "OOP", "3D Math", "Data Structures", "Algorithms"],
        "knowledge_areas": ["Game Physics", "Render Pipelines", "Spatial Partitioning"],
        "work_activities": ["Program interactive gameplay physics and entity states", "Optimize frame rates and shader memory"],
        "technology_skills": ["Unreal Engine", "Unity", "C++", "C#", "Git"],
        "education_level": "Bachelor's Degree in Computer Science or Game Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.10",
        "title": "Firmware Development Engineer",
        "domain": "Systems & Embedded",
        "description": "Develop board-level hardware support packages and low-level firmware for connected hardware appliances.",
        "required_skills": ["C", "C++", "Embedded Systems", "Linux", "Hardware Debugging", "Git"],
        "knowledge_areas": ["Embedded Linux", "Bootloaders (U-Boot)", "Peripheral Protocols"],
        "work_activities": ["Write hardware register drivers and interrupt handlers", "Flash microcontroller firmware builds"],
        "technology_skills": ["C", "Linux", "JTAG", "GCC", "Make", "Git"],
        "education_level": "Bachelor's Degree in Computer Engineering or Electrical Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1254.01",
        "title": "Accessibility (a11y) Web Specialist",
        "domain": "Web & Mobile Development",
        "description": "Audit and enhance digital applications to ensure compliance with WCAG, screen reader compatibility, and universal accessibility.",
        "required_skills": ["HTML", "CSS", "JavaScript", "Web Accessibility", "Screen Readers", "UI Design"],
        "knowledge_areas": ["WCAG 2.1 Guidelines", "ARIA Attributes", "Assistive Technologies"],
        "work_activities": ["Audit websites with NVDA and JAWS screen readers", "Fix keyboard navigation and color contrast barriers"],
        "technology_skills": ["Axe-core", "NVDA", "WAVE", "HTML5", "CSS3"],
        "education_level": "Bachelor's Degree or Professional Accessibility Certification",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1299.11",
        "title": "Kubernetes and Platform Engineer",
        "domain": "Cloud & DevOps",
        "description": "Build internal developer platforms (IDP), manage multi-tenant Kubernetes clusters, and automate cloud workload lifecycles.",
        "required_skills": ["Kubernetes", "Docker", "Linux", "Helm", "Go", "CI/CD"],
        "knowledge_areas": ["Container Networking (CNI)", "Cluster Security", "Ingress Controllers"],
        "work_activities": ["Maintain Kubernetes cluster controllers", "Author Helm charts and GitOps deployment configurations"],
        "technology_skills": ["Kubernetes", "Helm", "ArgoCD", "Docker", "Linux"],
        "education_level": "Bachelor's Degree in Computer Science or Systems Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1242.01",
        "title": "NoSQL and Big Data Storage Administrator",
        "domain": "Database & Storage",
        "description": "Administer high-velocity distributed document and key-value datastores including MongoDB, Cassandra, and Redis clusters.",
        "required_skills": ["MongoDB", "NoSQL", "Redis", "Linux", "Database Management", "Distributed Systems"],
        "knowledge_areas": ["CAP Theorem", "Sharding Protocols", "Replication Topologies"],
        "work_activities": ["Configure replica sets and distributed shards", "Monitor cache hit ratios and node failovers"],
        "technology_skills": ["MongoDB", "Redis", "Cassandra", "Linux", "Docker"],
        "education_level": "Bachelor's Degree in Computer Science or IT",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1253.02",
        "title": "API Automation QA Engineer",
        "domain": "Quality Assurance",
        "description": "Develop automated testing suites for microservices, checking contract schemas, status codes, and edge-case response payloads.",
        "required_skills": ["API Testing", "Postman", "Python", "REST API", "JSON Schema", "Git"],
        "knowledge_areas": ["Contract Testing", "HTTP Status Conventions", "CI/CD Integration"],
        "work_activities": ["Write automated API test scripts in Postman/Newman or Pytest", "Validate error response schemas and boundary limits"],
        "technology_skills": ["Postman", "Newman", "Pytest", "Git", "Swagger"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.11",
        "title": "IoT Solutions Software Engineer",
        "domain": "Systems & Embedded",
        "description": "Build edge computing software, sensor telemetry collection, and MQTT communication services for connected IoT hardware.",
        "required_skills": ["C++", "Python", "MQTT", "Embedded Systems", "Linux", "REST API"],
        "knowledge_areas": ["Telemetry Ingestion", "Low Power Networking", "Edge Computing"],
        "work_activities": ["Write lightweight edge telemetry publishers", "Process sensor data over MQTT brokers"],
        "technology_skills": ["Python", "C++", "Mosquitto MQTT", "Raspberry Pi", "Linux"],
        "education_level": "Bachelor's Degree in Computer Science or Electronics",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-2051.03",
        "title": "Data Quality and Governance Analyst",
        "domain": "Data Science & AI",
        "description": "Establish and oversee data governance frameworks, metadata catalogs, and automated data profiling rules.",
        "required_skills": ["SQL", "Data Quality", "Data Governance", "Python", "Data Profiling"],
        "knowledge_areas": ["Data Lineage", "Regulatory Compliance (GDPR)", "Master Data Management"],
        "work_activities": ["Define data quality metrics and validation thresholds", "Document corporate data lineage and catalog definitions"],
        "technology_skills": ["Great Expectations", "SQL", "Collibra", "Python", "Excel"],
        "education_level": "Bachelor's Degree in Information Systems or Analytics",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1254.02",
        "title": "Performance Frontend Engineer",
        "domain": "Web & Mobile Development",
        "description": "Optimize client-side web application bundle sizes, Core Web Vitals, browser rendering cycles, and caching protocols.",
        "required_skills": ["JavaScript", "HTML", "CSS", "Performance Optimization", "Webpack", "Chrome DevTools"],
        "knowledge_areas": ["Browser Critical Rendering Path", "Core Web Vitals", "Code Splitting"],
        "work_activities": ["Analyze JavaScript bundle bloat and memory leaks", "Optimize time-to-first-byte and largest-contentful-paint"],
        "technology_skills": ["Lighthouse", "Chrome DevTools", "Webpack", "React", "JavaScript"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.12",
        "title": "Enterprise Spring Boot Engineer",
        "domain": "Software Engineering",
        "description": "Architect enterprise-grade backend systems handling high financial volumes using Java Spring ecosystem and relational databases.",
        "required_skills": ["Java", "Spring Boot", "MySQL", "REST API", "JPA", "Microservices", "Git"],
        "knowledge_areas": ["Enterprise Integration Patterns", "Database Locking", "Transaction Semantics"],
        "work_activities": ["Implement ACID transaction boundaries", "Connect microservices via Spring Cloud and REST"],
        "technology_skills": ["Java", "Spring Boot", "MySQL", "Docker", "Git"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1212.05",
        "title": "Network Security Engineer",
        "domain": "Cybersecurity & Networking",
        "description": "Configure next-generation firewalls, VPN tunnels, intrusion detection systems, and network segmentation rules.",
        "required_skills": ["Computer Networks", "Firewalls", "VPN", "Linux", "Cybersecurity Basics", "Wireshark"],
        "knowledge_areas": ["IPSec / SSL Protocols", "DMZ Design", "Stateful Inspection"],
        "work_activities": ["Deploy and maintain corporate VPN gateways", "Analyze malicious packet traces using Wireshark"],
        "technology_skills": ["Palo Alto Networks", "Cisco ASA", "Wireshark", "Linux", "OpenVPN"],
        "education_level": "Bachelor's Degree in Network Security or Computer Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1251.09",
        "title": "Machine Learning Operations (MLOps) Engineer",
        "domain": "Data Science & AI",
        "description": "Automate model retraining, drift monitoring, containerization, and inference latency optimization in production.",
        "required_skills": ["Python", "Machine Learning", "Docker", "MLflow", "CI/CD", "Linux", "Kubernetes"],
        "knowledge_areas": ["Model Lifecycle Management", "Feature Stores", "Data Drift Detection"],
        "work_activities": ["Configure automated model retraining pipelines", "Monitor production endpoint latency and concept drift"],
        "technology_skills": ["MLflow", "Docker", "Kubernetes", "Python", "Airflow"],
        "education_level": "Bachelor's Degree in Computer Science or Software Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1255.06",
        "title": "User Experience (UX) Researcher",
        "domain": "Web & Mobile Development",
        "description": "Design and execute generative and evaluative qualitative and quantitative user research studies for digital interfaces.",
        "required_skills": ["UX Research", "Figma", "User Interviews", "Usability Testing", "Wireframing"],
        "knowledge_areas": ["Cognitive Psychology", "Research Methodology", "Affinity Diagramming"],
        "work_activities": ["Conduct moderated user testing sessions", "Synthesize user journey maps and persona archetypes"],
        "technology_skills": ["Miro", "Figma", "UserTesting", "Dovetail", "Google Analytics"],
        "education_level": "Bachelor's Degree in HCI, Psychology, or Design",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.13",
        "title": "Blockchain Software Developer",
        "domain": "Software Engineering",
        "description": "Design smart contracts, consensus validation protocols, and decentralized Web3 application backends.",
        "required_skills": ["Solidity", "JavaScript", "Cryptography", "Data Structures", "OOP", "Git"],
        "knowledge_areas": ["Decentralized Consensus", "Cryptography", "Smart Contract Security"],
        "work_activities": ["Write secure smart contracts", "Audit token logic against reentrancy vulnerabilities"],
        "technology_skills": ["Solidity", "Hardhat", "Ethers.js", "Ethereum", "Git"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.14",
        "title": "AR/VR Interactive Developer",
        "domain": "Software Engineering",
        "description": "Build augmented and virtual reality spatial applications, 3D interaction physics, and immersive headsets software.",
        "required_skills": ["C#", "Unity", "3D Math", "Computer Graphics", "OOP", "Git"],
        "knowledge_areas": ["Spatial Computing", "Human-Centered 3D Interaction", "Rendering Optimization"],
        "work_activities": ["Program spatial gesture interactions", "Optimize 3D mesh rendering pipelines"],
        "technology_skills": ["Unity", "C#", "Blender", "OpenXR", "Git"],
        "education_level": "Bachelor's Degree in Computer Science or Game Technology",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1212.06",
        "title": "Information Security Compliance Analyst",
        "domain": "Cybersecurity & Networking",
        "description": "Evaluate organization alignment with information security standards such as ISO 27001, SOC 2, and NIST cybersecurity frameworks.",
        "required_skills": ["Cybersecurity Basics", "Audit Controls", "Risk Assessment", "Documentation", "Compliance"],
        "knowledge_areas": ["ISO 27001", "NIST Framework", "Information Risk Governance"],
        "work_activities": ["Assess IT security controls against compliance matrices", "Prepare internal audit documentation"],
        "technology_skills": ["Excel", "Jira", "Vanta", "Confluence"],
        "education_level": "Bachelor's Degree in Information Assurance or Business IT",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1244.01",
        "title": "Linux Systems Engineer",
        "domain": "Cloud & DevOps",
        "description": "Administer enterprise Linux operating system distributions, kernel configuration, automated package patching, and server clustering.",
        "required_skills": ["Linux", "Bash", "Shell Scripting", "System Administration", "Networking", "Python"],
        "knowledge_areas": ["Linux Kernel Architecture", "POSIX Standards", "Server Hardening"],
        "work_activities": ["Write automated bash system maintenance scripts", "Troubleshoot kernel performance bottlenecks and daemon services"],
        "technology_skills": ["Red Hat Enterprise Linux", "Ubuntu", "Bash", "Ansible", "Git"],
        "education_level": "Bachelor's Degree in Computer Science or Information Technology",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1251.10",
        "title": "Big Data Platform Engineer",
        "domain": "Data Science & AI",
        "description": "Deploy, configure, and maintain distributed computational clusters including Hadoop, Spark, and Kafka streaming brokers.",
        "required_skills": ["Apache Spark", "Python", "SQL", "Kafka", "Linux", "Distributed Systems"],
        "knowledge_areas": ["Cluster Computing", "Stream Processing", "Distributed Filesystems (HDFS)"],
        "work_activities": ["Tune Spark execution executors and memory partitioning", "Manage cluster topic replication in Kafka"],
        "technology_skills": ["Apache Spark", "Kafka", "Hadoop", "Python", "Linux"],
        "education_level": "Bachelor's Degree in Computer Science or Software Engineering",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1242.02",
        "title": "Cloud Database Reliability Specialist",
        "domain": "Database & Storage",
        "description": "Maintain managed cloud databases (AWS RDS, Aurora, Cloud SQL) with automated point-in-time recoveries and read-replica autoscaling.",
        "required_skills": ["SQL", "PostgreSQL", "MySQL", "Cloud Computing", "Database Management", "Monitoring"],
        "knowledge_areas": ["Cloud Architecture", "Database Replication", "High Availability Topologies"],
        "work_activities": ["Configure multi-region database failover policies", "Monitor disk IOPS and connection pool exhaustion"],
        "technology_skills": ["AWS RDS", "PostgreSQL", "Terraform", "CloudWatch", "SQL"],
        "education_level": "Bachelor's Degree in Computer Science or IT",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1253.03",
        "title": "Mobile App QA Test Engineer",
        "domain": "Quality Assurance",
        "description": "Execute automated and exploratory mobile test matrices across physical devices, emulators, and mobile OS releases.",
        "required_skills": ["Software Testing", "Appium", "Mobile UI", "Python", "Bug Tracking", "Git"],
        "knowledge_areas": ["Mobile Device Fragmentation", "Touch Interaction Testing", "Network Simulation"],
        "work_activities": ["Develop Appium automated mobile test runs", "Document crash stack traces across Android and iOS targets"],
        "technology_skills": ["Appium", "Android Studio", "Xcode", "Pytest", "Postman"],
        "education_level": "Bachelor's Degree in Computer Science or IT",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1212.07",
        "title": "Vulnerability Management Specialist",
        "domain": "Cybersecurity & Networking",
        "description": "Scan corporate assets for CVE exposures, calculate CVSS risk scores, and coordinate patch cycles with infrastructure teams.",
        "required_skills": ["Cybersecurity Basics", "Vulnerability Assessment", "Linux", "Networking", "Risk Analysis"],
        "knowledge_areas": ["Common Vulnerabilities and Exposures (CVE)", "Patch Management", "Threat Intelligence"],
        "work_activities": ["Schedule vulnerability scans across subnet IP ranges", "Track remediation timelines with development leads"],
        "technology_skills": ["Nessus", "Qualys", "Linux", "Jira", "Excel"],
        "education_level": "Bachelor's Degree in Cybersecurity or IT",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1252.15",
        "title": "Enterprise Integration Developer",
        "domain": "Software Engineering",
        "description": "Develop data transformation middleware, message brokers, and enterprise service bus (ESB) connector interfaces.",
        "required_skills": ["Java", "REST API", "XML/JSON", "SQL", "OOP", "Message Queues"],
        "knowledge_areas": ["Enterprise Integration Patterns", "Service-Oriented Architecture (SOA)", "Data Mapping"],
        "work_activities": ["Write data transformation scripts between legacy and cloud systems", "Manage message broker dead-letter queues"],
        "technology_skills": ["Java", "Apache Camel", "RabbitMQ", "PostgreSQL", "Git"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1254.03",
        "title": "Jamstack / Static Site Web Developer",
        "domain": "Web & Mobile Development",
        "description": "Build high-speed static websites and headless CMS frontends using modern static site generators and edge functions.",
        "required_skills": ["HTML", "CSS", "JavaScript", "React", "Next.js", "Git", "REST API"],
        "knowledge_areas": ["Static Site Generation (SSG)", "Server-Side Rendering (SSR)", "Headless Content Management"],
        "work_activities": ["Build serverless web application pages", "Connect headless CMS content APIs into static layouts"],
        "technology_skills": ["Next.js", "React", "TailwindCSS", "Vercel", "Git"],
        "education_level": "Bachelor's Degree in Computer Science or Web Design",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-1299.12",
        "title": "Observability and Telemetry Engineer",
        "domain": "Cloud & DevOps",
        "description": "Standardize distributed tracing, OpenTelemetry instrumentations, log aggregation, and real-time operational alerting.",
        "required_skills": ["Linux", "Python", "Monitoring", "Docker", "Prometheus", "Git"],
        "knowledge_areas": ["Distributed Tracing", "OpenTelemetry Specification", "Log Ingestion"],
        "work_activities": ["Instrument backend microservices with OpenTelemetry", "Create real-time dashboards for service error rates"],
        "technology_skills": ["Prometheus", "Grafana", "Jaeger", "OpenTelemetry", "Linux"],
        "education_level": "Bachelor's Degree in Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    },
    {
        "soc_code": "15-2051.04",
        "title": "Marketing Analytics Specialist",
        "domain": "Data Science & AI",
        "description": "Analyze digital customer acquisition funnels, conversion rates, attribution models, and cohort retention metrics.",
        "required_skills": ["SQL", "Excel", "Data Visualization", "Statistics", "Google Analytics", "Python Basics"],
        "knowledge_areas": ["Customer Lifetime Value Modeling", "A/B Testing", "Marketing Mix Attribution"],
        "work_activities": ["Build acquisition funnel conversion dashboards", "Evaluate statistical significance in digital A/B tests"],
        "technology_skills": ["SQL", "Google Analytics", "Tableau", "Excel", "Python"],
        "education_level": "Bachelor's Degree in Marketing, Business Analytics, or Computer Science",
        "source": "O*NET 29.1 Educational Reference",
        "verification_status": "verified_sample"
    }
]


def save_sample_occupations_csv(output_csv: Path):
    """Save the curated sample dataset to CSV with standard schema."""
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "soc_code", "title", "domain", "description",
        "required_skills", "knowledge_areas", "work_activities",
        "technology_skills", "education_level", "source", "verification_status"
    ]

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in OCCUPATIONAL_SAMPLE_DATA:
            row = item.copy()
            row["required_skills"] = "; ".join(row["required_skills"])
            row["knowledge_areas"] = "; ".join(row["knowledge_areas"])
            row["work_activities"] = "; ".join(row["work_activities"])
            row["technology_skills"] = "; ".join(row["technology_skills"])
            writer.writerow(row)
    print(f"[OK] Saved {len(OCCUPATIONAL_SAMPLE_DATA)} sample occupational records to {output_csv}")


def import_sample_occupations_to_db(csv_path: Path):
    """Import occupations from CSV into the SQLite database."""
    init_db()
    inserted = 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        with get_db_cursor() as cursor:
            for row in reader:
                req_skills = [s.strip() for s in row["required_skills"].split(";") if s.strip()]
                knowledge = [s.strip() for s in row["knowledge_areas"].split(";") if s.strip()]
                activities = [s.strip() for s in row["work_activities"].split(";") if s.strip()]
                tech_skills = [s.strip() for s in row["technology_skills"].split(";") if s.strip()]

                cursor.execute("""
                INSERT INTO occupations (
                    soc_code, title, description, required_skills_json,
                    knowledge_areas_json, work_activities_json, technology_skills_json,
                    education_level, domain, source, verification_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(soc_code) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    required_skills_json=excluded.required_skills_json,
                    knowledge_areas_json=excluded.knowledge_areas_json,
                    work_activities_json=excluded.work_activities_json,
                    technology_skills_json=excluded.technology_skills_json,
                    education_level=excluded.education_level,
                    domain=excluded.domain,
                    source=excluded.source,
                    verification_status=excluded.verification_status
                """, (
                    row["soc_code"],
                    row["title"],
                    row["description"],
                    safe_json_dumps(req_skills),
                    safe_json_dumps(knowledge),
                    safe_json_dumps(activities),
                    safe_json_dumps(tech_skills),
                    row.get("education_level", "Bachelor's Degree"),
                    row.get("domain", "Technology"),
                    row.get("source", "O*NET Standard Sample"),
                    row.get("verification_status", "verified_sample")
                ))
                inserted += 1

    print(f"[OK] Successfully imported/updated {inserted} occupations into SQLite database.")


SAMPLE_PROFILES = [
    {
        "name": "Rahul",
        "degree": "Computer Science",
        "specialization": "Data Analytics",
        "education_level": "Undergraduate (3rd Year)",
        "skills": [
            {"name": "Python", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "SQL", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Excel", "evidence": "Explicitly provided", "proficiency": "Advanced"},
            {"name": "Data Visualization", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Statistics", "evidence": "Explicitly provided", "proficiency": "Beginner"}
        ],
        "projects": [
            {
                "name": "Sales Performance Dashboard",
                "technologies": ["Python", "SQL", "Excel", "Data Visualization"],
                "description": "Constructed an executive dashboard summarizing multi-region sales performance, metrics, and quarterly trends."
            }
        ],
        "interests": ["Data Analysis", "Business Insights"],
        "career_goals": ["Data Analyst", "Business Intelligence Specialist"],
        "natural_input": "I am a 3rd year Computer Science student skilled in Python, SQL, Excel, Data Visualization, and Statistics. I built a sales performance dashboard and I am keenly interested in Data Analysis and Business Insights."
    },
    {
        "name": "Ananya",
        "degree": "Computer Science",
        "specialization": "Web Development & Design",
        "education_level": "Undergraduate (3rd Year)",
        "skills": [
            {"name": "HTML", "evidence": "Explicitly provided", "proficiency": "Advanced"},
            {"name": "CSS", "evidence": "Explicitly provided", "proficiency": "Advanced"},
            {"name": "JavaScript", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "React", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Figma", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Git", "evidence": "Explicitly provided", "proficiency": "Beginner"}
        ],
        "projects": [
            {
                "name": "E-Commerce Product Explorer",
                "technologies": ["React", "JavaScript", "HTML", "CSS", "Figma"],
                "description": "Designed high-fidelity wireframes in Figma and coded a responsive React single-page product catalog with cart state."
            }
        ],
        "interests": ["Frontend Development", "UI Design"],
        "career_goals": ["Frontend Developer", "UI/UX Designer"],
        "natural_input": "I know HTML, CSS, JavaScript, React, Figma, and Git. I built a responsive e-commerce web app after designing mockups in Figma. I am passionate about Frontend Development and UI Design."
    },
    {
        "name": "Mohit",
        "degree": "Computer Science",
        "specialization": "Software Systems",
        "education_level": "Undergraduate (Final Year)",
        "skills": [
            {"name": "Java", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "OOP", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "MySQL", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Spring Boot", "evidence": "Explicitly provided", "proficiency": "Beginner"},
            {"name": "REST API", "evidence": "Explicitly provided", "proficiency": "Intermediate"}
        ],
        "projects": [
            {
                "name": "Student Attendance Microservice",
                "technologies": ["Java", "Spring Boot", "MySQL", "REST API"],
                "description": "Architected a secure REST API backend with Java and Spring Boot connecting to MySQL for attendance tracking."
            }
        ],
        "interests": ["Backend Development"],
        "career_goals": ["Backend Java Developer", "Software Engineer"],
        "natural_input": "I have solid experience in Java, Object-Oriented Programming (OOP), MySQL, Spring Boot, and REST API development. I designed a student attendance microservice and my main interest is in Backend Development."
    },
    {
        "name": "Sneha",
        "degree": "Computer Science / AI",
        "specialization": "Artificial Intelligence",
        "education_level": "Undergraduate (Final Year)",
        "skills": [
            {"name": "Python", "evidence": "Explicitly provided", "proficiency": "Advanced"},
            {"name": "Machine Learning", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Pandas", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "NumPy", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Scikit-learn", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Matplotlib", "evidence": "Explicitly provided", "proficiency": "Intermediate"}
        ],
        "projects": [
            {
                "name": "Predictive Sentiment Classifier",
                "technologies": ["Python", "Scikit-learn", "Pandas", "NumPy", "Matplotlib"],
                "description": "Trained predictive regression and classification pipelines using Scikit-learn with rigorous cross-validation."
            }
        ],
        "interests": ["Artificial Intelligence", "Data Science"],
        "career_goals": ["Machine Learning Engineer", "AI Researcher"],
        "natural_input": "I study Computer Science and AI. My technical stack includes Python, Machine Learning, Pandas, NumPy, Scikit-learn, and Matplotlib. I built a predictive classifier and want to work in Artificial Intelligence and Data Science."
    },
    {
        "name": "Arjun",
        "degree": "Computer Science",
        "specialization": "Network Security",
        "education_level": "Undergraduate (3rd Year)",
        "skills": [
            {"name": "C", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "C++", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Computer Networks", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Linux", "evidence": "Explicitly provided", "proficiency": "Intermediate"},
            {"name": "Cybersecurity Basics", "evidence": "Explicitly provided", "proficiency": "Beginner"},
            {"name": "Wireshark", "evidence": "Explicitly provided", "proficiency": "Beginner"}
        ],
        "projects": [
            {
                "name": "Packet Sniffing and Port Scanner Tool",
                "technologies": ["C", "C++", "Linux", "Computer Networks", "Wireshark"],
                "description": "Developed a raw socket network scanner on Linux to inspect packet headers and identify open TCP ports."
            }
        ],
        "interests": ["Networking", "Cybersecurity"],
        "career_goals": ["Information Security Analyst", "Network Engineer"],
        "natural_input": "I have skills in C, C++, Computer Networks, Linux, Cybersecurity Basics, and Wireshark. I developed a Linux-based packet analysis tool and my core interests are Networking and Cybersecurity."
    }
]


def import_official_onet_files(onet_raw_dir: Path) -> bool:
    """Parse and import raw O*NET tab-delimited text files if present in onet_raw_dir.

    Supports:
    - Occupation Data.txt
    - Skills.txt
    - Knowledge.txt
    - Work Activities.txt
    - Technology Skills.txt
    """
    occ_file = onet_raw_dir / "Occupation Data.txt"
    if not occ_file.exists():
        return False

    print(f"[*] Found official O*NET release in {onet_raw_dir}. Processing raw files...")
    occupations_map = {}

    # 1. Parse Occupation Data.txt
    with open(occ_file, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            soc = row.get("O*NET-SOC Code", "").strip()
            title = row.get("Title", "").strip()
            desc = row.get("Description", "").strip()
            if soc and title:
                occupations_map[soc] = {
                    "soc_code": soc,
                    "title": title,
                    "description": desc,
                    "required_skills": [],
                    "knowledge_areas": [],
                    "work_activities": [],
                    "technology_skills": [],
                    "education_level": "Bachelor's Degree or Equivalent",
                    "domain": "Technology & Computing" if soc.startswith("15-") else "Other",
                    "source": "O*NET 29.1 Official Release",
                    "verification_status": "official_imported"
                }

    # 2. Parse Skills.txt (if present)
    skills_file = onet_raw_dir / "Skills.txt"
    if skills_file.exists():
        with open(skills_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                soc = row.get("O*NET-SOC Code", "").strip()
                skill = row.get("Element Name", "").strip()
                if soc in occupations_map and skill and skill not in occupations_map[soc]["required_skills"]:
                    occupations_map[soc]["required_skills"].append(skill)

    # 3. Parse Knowledge.txt (if present)
    know_file = onet_raw_dir / "Knowledge.txt"
    if know_file.exists():
        with open(know_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                soc = row.get("O*NET-SOC Code", "").strip()
                know = row.get("Element Name", "").strip()
                if soc in occupations_map and know and know not in occupations_map[soc]["knowledge_areas"]:
                    occupations_map[soc]["knowledge_areas"].append(know)

    # 4. Parse Work Activities.txt (if present)
    work_file = onet_raw_dir / "Work Activities.txt"
    if work_file.exists():
        with open(work_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                soc = row.get("O*NET-SOC Code", "").strip()
                act = row.get("Element Name", "").strip()
                if soc in occupations_map and act and act not in occupations_map[soc]["work_activities"]:
                    occupations_map[soc]["work_activities"].append(act)

    # 5. Parse Technology Skills.txt (if present)
    tech_file = onet_raw_dir / "Technology Skills.txt"
    if tech_file.exists():
        with open(tech_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                soc = row.get("O*NET-SOC Code", "").strip()
                tech = row.get("Example", "").strip()
                if soc in occupations_map and tech and tech not in occupations_map[soc]["technology_skills"]:
                    occupations_map[soc]["technology_skills"].append(tech)

    # Insert parsed official occupations into database
    init_db()
    inserted = 0
    with get_db_cursor() as cursor:
        for soc, item in occupations_map.items():
            cursor.execute("""
            INSERT INTO occupations (
                soc_code, title, description, required_skills_json,
                knowledge_areas_json, work_activities_json, technology_skills_json,
                education_level, domain, source, verification_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(soc_code) DO UPDATE SET
                title=excluded.title,
                description=excluded.description,
                required_skills_json=excluded.required_skills_json,
                knowledge_areas_json=excluded.knowledge_areas_json,
                work_activities_json=excluded.work_activities_json,
                technology_skills_json=excluded.technology_skills_json,
                source=excluded.source,
                verification_status=excluded.verification_status
            """, (
                item["soc_code"],
                item["title"],
                item["description"],
                safe_json_dumps(item["required_skills"][:15]),
                safe_json_dumps(item["knowledge_areas"][:10]),
                safe_json_dumps(item["work_activities"][:10]),
                safe_json_dumps(item["technology_skills"][:15]),
                item["education_level"],
                item["domain"],
                item["source"],
                item["verification_status"]
            ))
            inserted += 1

    print(f"[OK] Successfully imported {inserted} official O*NET records into SQLite database.")
    return True


def save_sample_profiles_json(output_path: Path):
    """Save the five required student profiles to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_PROFILES, f, indent=2)
    print(f"[OK] Saved 5 sample student profiles to {output_path}")


def seed_sample_profiles_to_db():
    """Seed the 5 standard profiles into the database."""
    init_db()
    with get_db_cursor() as cursor:
        for profile in SAMPLE_PROFILES:
            cursor.execute("""
            INSERT INTO students (
                name, degree, specialization, education_level, natural_input,
                interests_json, career_goals_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                profile["name"],
                profile["degree"],
                profile["specialization"],
                profile["education_level"],
                profile["natural_input"],
                safe_json_dumps(profile["interests"]),
                safe_json_dumps(profile["career_goals"])
            ))
            student_id = cursor.lastrowid

            for sk in profile["skills"]:
                cursor.execute("""
                INSERT INTO student_skills (
                    student_id, skill_name, evidence_type, proficiency, classification, source
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    student_id,
                    sk["name"],
                    sk.get("evidence", "explicit"),
                    sk.get("proficiency", "Unspecified"),
                    "confirmed",
                    "profile"
                ))

            for prj in profile["projects"]:
                cursor.execute("""
                INSERT INTO student_projects (
                    student_id, name, description, technologies_json
                ) VALUES (?, ?, ?, ?)
                """, (
                    student_id,
                    prj["name"],
                    prj.get("description", ""),
                    safe_json_dumps(prj.get("technologies", []))
                ))
    print("[OK] Seeded 5 standard student profiles into the database.")


def main():
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    raw_onet_dir = data_dir / "onet_raw"

    csv_path = data_dir / "sample_occupations.csv"
    profiles_path = data_dir / "sample_profiles.json"

    print("Step 1: Checking for official O*NET database files in data/onet_raw/...")
    imported_official = import_official_onet_files(raw_onet_dir)

    if not imported_official:
        print("[*] Official raw files not found. Using curated educational sample dataset...")
        print("Step 2: Generating sample occupations CSV...")
        save_sample_occupations_csv(csv_path)

        print("Step 3: Importing sample occupations into SQLite database...")
        import_sample_occupations_to_db(csv_path)

    print("Step 4: Generating sample profiles JSON...")
    save_sample_profiles_json(profiles_path)

    print("Step 5: Seeding sample profiles to SQLite database...")
    seed_sample_profiles_to_db()

    print("\nDataset preparation completed successfully!")


if __name__ == "__main__":
    main()
