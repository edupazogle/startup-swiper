"""
Create Topics and Use Cases hierarchical structure in the database.

This script creates tables to establish a parent-child relationship between
topics and use cases, allowing filtering with dependency (use cases can only
be selected when parent topic is chosen).
"""

import sys
sys.path.insert(0, '/home/akyo/startup_swiper/api')

from database import engine
from sqlalchemy import text

# Topic and Use Case definitions
TOPICS_HIERARCHY = {
    "AI - Software development": [
        "Code Generation",
        "Testing Automation",
        "Debugging & Monitoring",
        "Documentation Generation",
        "Code Optimization"
    ],
    "AI - Agentic": [
        "Workflow Automation",
        "Business Process Automation",
        "Customer Service Automation",
        "Data Processing Automation",
        "Decision Making Support"
    ],
    "Cybersecurity": [
        "Threat Detection",
        "Vulnerability Management",
        "Access Control",
        "Data Protection",
        "Incident Response"
    ],
    "Data & Analytics": [
        "Data Integration",
        "Data Visualization",
        "Business Intelligence",
        "Predictive Analytics",
        "Real-time Analytics"
    ],
    "Fintech": [
        "Payment Processing",
        "Lending",
        "Investment Management",
        "Risk Management",
        "Regulatory Compliance"
    ],
    "Healthcare": [
        "Patient Management",
        "Medical Imaging",
        "Drug Discovery",
        "Telemedicine",
        "Health Monitoring"
    ],
    "InsurTech": [
        "Claims Processing",
        "Policy Administration",
        "Risk Assessment",
        "Fraud Detection",
        "Customer Engagement"
    ],
    "Cloud Computing": [
        "Infrastructure Management",
        "Container Orchestration",
        "Serverless Computing",
        "Cost Optimization",
        "Disaster Recovery"
    ],
    "IoT": [
        "Device Management",
        "Real-time Monitoring",
        "Predictive Maintenance",
        "Edge Computing",
        "Data Collection"
    ],
    "Workflow Automation": [
        "Process Automation",
        "Document Processing",
        "Task Management",
        "Integration",
        "Approval Workflows"
    ]
}

def create_tables():
    """Create topics and use_cases tables"""
    with engine.connect() as conn:
        # Create topics table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                color_code VARCHAR(50),
                icon VARCHAR(50),
                order_index INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create use_cases table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS use_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                order_index INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics(id),
                UNIQUE(topic_id, name)
            )
        """))
        
        conn.commit()
        print("✓ Tables created successfully")

def populate_topics_and_use_cases():
    """Populate topics and use cases from hierarchy"""
    with engine.connect() as conn:
        # Check if data already exists
        result = conn.execute(text("SELECT COUNT(*) as count FROM topics"))
        count = result.scalar()
        
        if count > 0:
            print(f"✓ Topics already populated ({count} topics found)")
            return
        
        topic_ids = {}
        
        # Insert topics
        for idx, topic_name in enumerate(TOPICS_HIERARCHY.keys(), 1):
            try:
                conn.execute(text("""
                    INSERT INTO topics (name, order_index)
                    VALUES (:name, :order_index)
                """), {"name": topic_name, "order_index": idx})
                
                # Get the inserted topic ID
                result = conn.execute(text("SELECT id FROM topics WHERE name = :name"), 
                                     {"name": topic_name})
                topic_ids[topic_name] = result.scalar()
                print(f"  ✓ Created topic: {topic_name}")
            except Exception as e:
                print(f"  ⚠ Topic '{topic_name}' already exists: {e}")
        
        # Insert use cases
        for topic_name, use_cases in TOPICS_HIERARCHY.items():
            topic_id = topic_ids.get(topic_name)
            if not topic_id:
                # Try to get existing topic ID
                result = conn.execute(text("SELECT id FROM topics WHERE name = :name"), 
                                     {"name": topic_name})
                topic_id = result.scalar()
            
            if topic_id:
                for order_idx, use_case_name in enumerate(use_cases, 1):
                    try:
                        conn.execute(text("""
                            INSERT INTO use_cases (topic_id, name, order_index)
                            VALUES (:topic_id, :name, :order_index)
                        """), {
                            "topic_id": topic_id,
                            "name": use_case_name,
                            "order_index": order_idx
                        })
                        print(f"    ✓ Created use case: {use_case_name}")
                    except Exception as e:
                        print(f"    ⚠ Use case '{use_case_name}' already exists: {e}")
        
        conn.commit()
        print("\n✓ Topics and use cases populated successfully")

def verify_data():
    """Verify the data was created correctly"""
    with engine.connect() as conn:
        # Count topics
        topics_result = conn.execute(text("SELECT COUNT(*) as count FROM topics"))
        topics_count = topics_result.scalar()
        
        # Count use cases
        use_cases_result = conn.execute(text("SELECT COUNT(*) as count FROM use_cases"))
        use_cases_count = use_cases_result.scalar()
        
        print(f"\n📊 Database Statistics:")
        print(f"  Topics: {topics_count}")
        print(f"  Use Cases: {use_cases_count}")
        
        # Show sample
        print(f"\n📋 Sample Topics:")
        sample = conn.execute(text("SELECT id, name FROM topics LIMIT 3"))
        for row in sample:
            topic_id, topic_name = row
            use_cases = conn.execute(text(
                "SELECT name FROM use_cases WHERE topic_id = :topic_id ORDER BY order_index"
            ), {"topic_id": topic_id})
            uc_names = [uc[0] for uc in use_cases]
            print(f"  - {topic_name}: {', '.join(uc_names)}")

if __name__ == "__main__":
    print("🗃️  Creating Topics & Use Cases Database Structure...\n")
    
    try:
        create_tables()
        populate_topics_and_use_cases()
        verify_data()
        print("\n✅ Database setup complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
