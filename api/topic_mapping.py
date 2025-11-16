"""
Mapping between Topic/Use Case codes and friendly names
"""

# Topic code to friendly name
TOPIC_CODE_TO_NAME = {
    "Topic 1": "AI - Agentic",
    "Topic 2": "AI - Software development",
    "Topic 3": "AI - Claims",
    "Topic 4": "AI - Underwriting",
    "Topic 5": "AI - Contact centers",
    "Topic 6": "Health",
    "Topic 7": "Growth",
    "Topic 8": "Responsibility",
    "Topic 9": "Insurance disruptor",
    "Topic 10": "DeepTech",
    "Topic 11": "Other"
}

# Use case code to friendly name
USE_CASE_CODE_TO_NAME = {
    # Topic 1: AI - Agentic
    "F1.1_observability_monitoring": "Observability & monitoring",
    "F1.2_agent_orchestration": "Agent orchestration",
    "F1.3_llm_operations": "LLM operations",
    "F1.4_agent_frameworks": "Agent frameworks & SDKs",
    "F1.5_data_infrastructure": "Data infrastructure - Vector DBs & RAG",
    "F1.6_agent_testing": "Agent testing & validation",
    
    # Topic 2: AI - Software Development
    "F5.1_code_development": "Code development",
    "F5.2_automated_testing": "Automated testing",
    "F5.3_legacy_migration": "Legacy migration",
    "F5.4_system_integration": "System integration",
    "F5.5_code_intelligence": "Code intelligence",
    "F5.6_devops_cicd": "DevOps & CI/CD",
    
    # Topic 3: AI - Claims
    "F3.1_claims_management": "Claims management",
    "F3.7_claims_fraud_detection": "Claims fraud detection",
    
    # Topic 4: AI - Underwriting
    "F3.2_underwriting": "Underwriting",
    
    # Topic 5: AI - Contact Centers
    "F2.3_customer_support": "Customer support",
    "F3.5_customer_experience": "Customer experience",
    
    # Topic 6: Health
    "F4.1_health_analytics": "Health analytics",
    "F4.2_wellness_prevention": "Wellness & prevention",
    "F4.3_remote_monitoring": "Remote monitoring",
    "F4.4_telemedicine": "Telemedicine",
    "F4.5_healthcare_fraud": "Healthcare fraud",
    "F4.6_mental_health": "Mental health",
    
    # Topic 7: Growth
    "F2.1_marketing_automation": "Marketing automation",
    "F2.2_sales_enablement": "Sales enablement",
    "F2.6_data_analytics": "Data analytics",
    
    # Topic 8: Responsibility
    "F3.6_compliance_regulatory": "Compliance & regulatory",
    "F3.7_insurance_fraud": "Insurance fraud",
    
    # Topic 9: Insurance Disruptor
    "F3.3_policy_administration": "Policy administration",
    "F3.4_distribution_agency": "Distribution & agency",
    
    # Topic 10: DeepTech
    "F10.1_advanced_ai_ml": "Advanced AI/ML",
    "F10.2_emerging_technologies": "Emerging technologies",
    
    # Topic 11: Other
    "F2.4_hr_recruiting": "HR & recruiting",
    "F2.5_finance_procurement": "Finance & procurement",
    "F2.7_workflow_automation": "Workflow automation"
}

# Use case to topic mapping
USE_CASE_TO_TOPIC = {
    # Topic 1: AI - Agentic
    "F1.1_observability_monitoring": "AI - Agentic",
    "F1.2_agent_orchestration": "AI - Agentic",
    "F1.3_llm_operations": "AI - Agentic",
    "F1.4_agent_frameworks": "AI - Agentic",
    "F1.5_data_infrastructure": "AI - Agentic",
    "F1.6_agent_testing": "AI - Agentic",
    
    # Topic 2: AI - Software Development
    "F5.1_code_development": "AI - Software development",
    "F5.2_automated_testing": "AI - Software development",
    "F5.3_legacy_migration": "AI - Software development",
    "F5.4_system_integration": "AI - Software development",
    "F5.5_code_intelligence": "AI - Software development",
    "F5.6_devops_cicd": "AI - Software development",
    
    # Topic 3: AI - Claims
    "F3.1_claims_management": "AI - Claims",
    "F3.7_claims_fraud_detection": "AI - Claims",
    
    # Topic 4: AI - Underwriting
    "F3.2_underwriting": "AI - Underwriting",
    
    # Topic 5: AI - Contact Centers
    "F2.3_customer_support": "AI - Contact centers",
    "F3.5_customer_experience": "AI - Contact centers",
    
    # Topic 6: Health
    "F4.1_health_analytics": "Health",
    "F4.2_wellness_prevention": "Health",
    "F4.3_remote_monitoring": "Health",
    "F4.4_telemedicine": "Health",
    "F4.5_healthcare_fraud": "Health",
    "F4.6_mental_health": "Health",
    
    # Topic 7: Growth
    "F2.1_marketing_automation": "Growth",
    "F2.2_sales_enablement": "Growth",
    "F2.6_data_analytics": "Growth",
    
    # Topic 8: Responsibility
    "F3.6_compliance_regulatory": "Responsibility",
    "F3.7_insurance_fraud": "Responsibility",
    
    # Topic 9: Insurance Disruptor
    "F3.3_policy_administration": "Insurance disruptor",
    "F3.4_distribution_agency": "Insurance disruptor",
    
    # Topic 10: DeepTech
    "F10.1_advanced_ai_ml": "DeepTech",
    "F10.2_emerging_technologies": "DeepTech",
    
    # Topic 11: Other
    "F2.4_hr_recruiting": "Other",
    "F2.5_finance_procurement": "Other",
    "F2.7_workflow_automation": "Other"
}

def convert_topic_code_to_name(topic_code: str) -> str:
    """Convert Topic X to friendly name"""
    return TOPIC_CODE_TO_NAME.get(topic_code, topic_code)

def convert_use_case_code_to_name(use_case_code: str) -> str:
    """Convert FX.Y_code to friendly name"""
    return USE_CASE_CODE_TO_NAME.get(use_case_code, use_case_code)

def get_topic_for_use_case(use_case_code: str) -> str:
    """Get the topic name for a use case code"""
    return USE_CASE_TO_TOPIC.get(use_case_code, "Other")
