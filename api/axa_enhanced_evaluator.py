#!/usr/bin/env python3
"""
AXA Enhanced Startup Evaluator with 35+ Feature Categories

Based on AXA Selection Rules:
- Rule 1: Platform Enablers (F1.1-F1.6)
- Rule 2: Service Providers (F2.1-F2.7)
- Rule 3: Insurance Solutions (F3.1-F3.6)
- Rule 4: Health Innovations (F4.1-F4.5)
- Rule 5: Dev & Legacy (F5.1-F5.6)

Usage:
    python3 api/axa_enhanced_evaluator.py --max-startups 10
    python3 api/axa_enhanced_evaluator.py --workers 15 --batch-size 3
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Imports
from database import SessionLocal
from models_startup import Startup
from llm_config import get_nvidia_nim_model
import os

# Get NVIDIA API config
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = get_nvidia_nim_model()


class FeatureCategory(Enum):
    """Enhanced AXA Feature Categories - 35+ categories across 5 rules"""
    
    # RULE 1: Platform Enablers (6 categories)
    F1_1_OBSERVABILITY = "F1.1_observability_monitoring"
    F1_2_ORCHESTRATION = "F1.2_agent_orchestration"
    F1_3_LLM_OPS = "F1.3_llm_operations"
    F1_4_FRAMEWORKS = "F1.4_agent_frameworks"
    F1_5_DATA_INFRA = "F1.5_data_infrastructure"
    F1_6_TESTING = "F1.6_agent_testing"
    
    # RULE 2: Service Providers (7 categories)
    F2_1_MARKETING = "F2.1_marketing_automation"
    F2_2_SALES = "F2.2_sales_enablement"
    F2_3_SUPPORT = "F2.3_customer_support"
    F2_4_HR = "F2.4_hr_recruiting"
    F2_5_FINANCE = "F2.5_finance_procurement"
    F2_6_ANALYTICS = "F2.6_data_analytics"
    F2_7_WORKFLOW = "F2.7_workflow_automation"
    
    # RULE 3: Insurance Solutions (6 categories)
    F3_1_CLAIMS = "F3.1_claims_management"
    F3_2_UNDERWRITING = "F3.2_underwriting"
    F3_3_POLICY = "F3.3_policy_administration"
    F3_4_DISTRIBUTION = "F3.4_distribution_agency"
    F3_5_CUSTOMER_EXP = "F3.5_customer_experience"
    F3_6_COMPLIANCE = "F3.6_compliance_regulatory"
    
    # RULE 4: Health Innovations (5 categories)
    F4_1_HEALTH_ANALYTICS = "F4.1_health_analytics"
    F4_2_WELLNESS = "F4.2_wellness_prevention"
    F4_3_MONITORING = "F4.3_remote_monitoring"
    F4_4_TELEMEDICINE = "F4.4_telemedicine"
    F4_5_FRAUD = "F4.5_healthcare_fraud"
    
    # RULE 5: Dev & Legacy (6 categories)
    F5_1_CODING = "F5.1_code_development"
    F5_2_TESTING = "F5.2_automated_testing"
    F5_3_MIGRATION = "F5.3_legacy_migration"
    F5_4_INTEGRATION = "F5.4_system_integration"
    F5_5_INTELLIGENCE = "F5.5_code_intelligence"
    F5_6_DEVOPS = "F5.6_devops_cicd"


# Enhanced keyword mappings
FEATURE_KEYWORDS = {
    # Rule 1: Platform Enablers
    FeatureCategory.F1_1_OBSERVABILITY: [
        "observability", "monitoring", "tracing", "langsmith", "arize",
        "weights & biases", "mlflow", "wandb", "agent monitoring",
        "llm monitoring", "model monitoring", "performance tracking"
    ],
    FeatureCategory.F1_2_ORCHESTRATION: [
        "orchestration", "multi-agent", "agent mesh", "crewai",
        "autogen", "agent coordination", "workflow engine",
        "agent communication", "task distribution"
    ],
    FeatureCategory.F1_3_LLM_OPS: [
        "llm ops", "mlops", "model deployment", "model management",
        "prompt engineering", "prompt management", "model serving",
        "vellum", "humanloop"
    ],
    FeatureCategory.F1_4_FRAMEWORKS: [
        "agent framework", "langchain", "llamaindex", "haystack",
        "agent builder", "low-code agents", "sdk", "api",
        "development platform", "agent studio"
    ],
    FeatureCategory.F1_5_DATA_INFRA: [
        "vector database", "pinecone", "weaviate", "qdrant", "milvus",
        "embedding", "rag", "retrieval", "semantic search",
        "knowledge graph", "neo4j"
    ],
    FeatureCategory.F1_6_TESTING: [
        "ai evaluation", "evals", "testing", "validation",
        "quality assurance", "benchmark", "evaluation framework",
        "agent testing", "model testing"
    ],
    
    # Rule 2: Service Providers
    FeatureCategory.F2_1_MARKETING: [
        "marketing automation", "jasper", "copy.ai", "content generation",
        "social media automation", "campaign automation",
        "marketing agents", "content agents", "seo automation"
    ],
    FeatureCategory.F2_2_SALES: [
        "sales intelligence", "gong", "chorus", "sales enablement",
        "lead generation", "sales automation", "lavender",
        "outreach automation", "sales ai", "conversation intelligence"
    ],
    FeatureCategory.F2_3_SUPPORT: [
        "customer support", "intercom", "zendesk", "ada",
        "support automation", "chatbot", "conversational ai",
        "helpdesk", "service desk", "ticket automation", "contact center"
    ],
    FeatureCategory.F2_4_HR: [
        "recruiting", "hirevue", "phenom", "eightfold",
        "talent acquisition", "hr automation", "ats",
        "candidate screening", "employee onboarding"
    ],
    FeatureCategory.F2_5_FINANCE: [
        "finance automation", "appzen", "stampli", "invoice processing",
        "accounts payable", "procurement", "contract analysis",
        "expense management", "financial planning"
    ],
    FeatureCategory.F2_6_ANALYTICS: [
        "business intelligence", "thoughtspot", "looker", "tableau",
        "data analytics", "automated insights", "predictive analytics",
        "reporting automation", "data visualization"
    ],
    FeatureCategory.F2_7_WORKFLOW: [
        "workflow automation", "zapier", "make", "n8n",
        "process automation", "rpa", "business process",
        "automation platform", "integration"
    ],
    
    # Rule 3: Insurance Solutions
    FeatureCategory.F3_1_CLAIMS: [
        "claims", "tractable", "shift technology", "claims automation",
        "fnol", "first notice of loss", "claims processing",
        "claims assessment", "claims settlement", "snapsheet"
    ],
    FeatureCategory.F3_2_UNDERWRITING: [
        "underwriting", "zelros", "gradient ai", "risk assessment",
        "pricing", "underwriting automation", "risk modeling",
        "planck", "cytora", "bdeo"
    ],
    FeatureCategory.F3_3_POLICY: [
        "policy administration", "majesco", "duck creek", "eis",
        "socotra", "policy management", "policy automation",
        "renewals", "policy issuance"
    ],
    FeatureCategory.F3_4_DISTRIBUTION: [
        "insurance distribution", "vertafore", "applied systems",
        "agent portal", "broker platform", "quote and bind",
        "digital distribution", "agency management"
    ],
    FeatureCategory.F3_5_CUSTOMER_EXP: [
        "digital insurance", "customer experience", "policyholder",
        "self-service", "mobile app", "policyholder portal",
        "insurance chatbot", "digital onboarding"
    ],
    FeatureCategory.F3_6_COMPLIANCE: [
        "insurance compliance", "regulatory", "kyc", "aml",
        "audit", "reporting", "solvency", "gdpr",
        "compliance automation", "regulatory reporting"
    ],
    
    # Rule 4: Health Innovations
    FeatureCategory.F4_1_HEALTH_ANALYTICS: [
        "health analytics", "komodo health", "tempus", "lumiata",
        "health risk", "medical ai", "population health",
        "health data", "claims analytics", "predictive health"
    ],
    FeatureCategory.F4_2_WELLNESS: [
        "wellness", "omada health", "virta", "noom",
        "preventive health", "chronic disease", "disease management",
        "health coaching", "mental health", "lyra health"
    ],
    FeatureCategory.F4_3_MONITORING: [
        "remote monitoring", "wearables", "biointellisense",
        "connected health", "patient monitoring", "vital signs",
        "continuous monitoring", "health tracking", "iot health"
    ],
    FeatureCategory.F4_4_TELEMEDICINE: [
        "telemedicine", "telehealth", "teladoc", "virtual care",
        "digital health", "remote consultation", "virtual doctor",
        "digital therapeutics", "e-prescribing"
    ],
    FeatureCategory.F4_5_FRAUD: [
        "healthcare fraud", "medical fraud", "claims fraud",
        "provider fraud", "billing fraud", "cotiviti",
        "fraud detection", "anomaly detection"
    ],
    
    # Rule 5: Dev & Legacy
    FeatureCategory.F5_1_CODING: [
        "ai coding", "github copilot", "tabnine", "codeium",
        "code generation", "code completion", "cursor",
        "code assistant", "pair programming", "code review"
    ],
    FeatureCategory.F5_2_TESTING: [
        "test automation", "testim", "mabl", "functionize",
        "qa automation", "automated testing", "test generation",
        "selenium", "cypress", "quality assurance"
    ],
    FeatureCategory.F5_3_MIGRATION: [
        "legacy modernization", "code migration", "mainframe",
        "cobol", "heirloom", "bluage", "code translation",
        "language migration", "platform migration"
    ],
    FeatureCategory.F5_4_INTEGRATION: [
        "legacy integration", "mulesoft", "boomi", "api generation",
        "middleware", "integration platform", "esb",
        "service mesh", "api gateway"
    ],
    FeatureCategory.F5_5_INTELLIGENCE: [
        "code intelligence", "sourcegraph", "code search",
        "documentation", "technical debt", "code analysis",
        "architecture", "dependency analysis"
    ],
    FeatureCategory.F5_6_DEVOPS: [
        "devops", "ci/cd", "harness", "gitlab", "jenkins",
        "deployment automation", "infrastructure as code",
        "terraform", "kubernetes", "containerization"
    ]
}


# Rule priority weights
RULE_BASE_SCORES = {
    "Rule 1": 40,  # Platform Enablers
    "Rule 2": 40,  # Service Providers
    "Rule 3": 40,  # Insurance Solutions
    "Rule 4": 40,  # Health Innovations
    "Rule 5": 40   # Dev & Legacy
}


@dataclass
class CategoryMatch:
    category: str
    rule: str
    matches: bool
    confidence: int
    reasoning: str


@dataclass
class StartupEvaluation:
    startup_id: int
    startup_name: str
    evaluation_date: str
    categories_matched: List[CategoryMatch]
    matched_rules: List[str]
    rule_scores: Dict[str, int]
    overall_score: float
    priority_tier: str
    axa_fit_summary: str
    can_use_as_provider: bool
    business_leverage: str


class EnhancedEvaluator:
    """Enhanced evaluator with 35+ feature categories"""
    
    def __init__(self, workers: int = 10, batch_size: int = 3, checkpoint_interval: int = 10):
        self.workers = workers
        self.batch_size = batch_size
        self.checkpoint_interval = checkpoint_interval  # Save every N batches
        self.db = SessionLocal()
        self.checkpoint_file = Path("downloads/axa_enhanced_checkpoint.json")
        self.evaluated_ids = set()
        
        # Ensure downloads directory exists
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY not configured!")
        
        logger.info(f"✓ Enhanced Evaluator: {workers} workers × {batch_size} startups/batch")
        logger.info(f"✓ Feature Categories: 35+ across 5 AXA rules")
        logger.info(f"✓ Checkpoint: Auto-save every {checkpoint_interval} batches per worker")
    
    def _load_checkpoint(self) -> Dict[str, Any]:
        """Load checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                data = json.load(f)
                self.evaluated_ids = set(data.get('evaluated_ids', []))
                logger.info(f"✓ Checkpoint: {len(self.evaluated_ids)} already evaluated")
                return data
        return {'evaluated_ids': [], 'results': []}
    
    def _save_checkpoint(self, results: List[Dict[str, Any]]):
        """Save checkpoint with metadata"""
        checkpoint_data = {
            'evaluated_ids': list(self.evaluated_ids),
            'results': results,
            'last_updated': datetime.now().isoformat(),
            'total_evaluated': len(self.evaluated_ids),
            'config': {
                'workers': self.workers,
                'batch_size': self.batch_size,
                'checkpoint_interval': self.checkpoint_interval
            },
            'stats': {
                'provider_count': sum(1 for r in results if r.get('can_use_as_provider', False)),
                'non_provider_count': sum(1 for r in results if not r.get('can_use_as_provider', False)),
                'tier_1': sum(1 for r in results if 'Tier 1' in r.get('priority_tier', '')),
                'tier_2': sum(1 for r in results if 'Tier 2' in r.get('priority_tier', '')),
                'tier_3': sum(1 for r in results if 'Tier 3' in r.get('priority_tier', '')),
                'tier_4': sum(1 for r in results if 'Tier 4' in r.get('priority_tier', ''))
            }
        }
        
        # Write to temp file first, then rename (atomic operation)
        temp_file = self.checkpoint_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            temp_file.replace(self.checkpoint_file)
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            if temp_file.exists():
                temp_file.unlink()
    
    def _should_evaluate(self, startup: Startup) -> bool:
        """Pre-filtering - skip obvious non-matches"""
        
        if not startup.company_description and not startup.shortDescription:
            return False
        
        text = f"{startup.company_description or ''} {startup.shortDescription or ''} {startup.primary_industry or ''}".lower()
        industry = (startup.primary_industry or '').lower()
        
        # Exclude irrelevant industries
        excluded = ['gaming', 'game', 'entertainment', 'food', 'restaurant', 
                   'hospitality', 'dating', 'fashion', 'beauty', 'cosmetics',
                   'luxury', 'jewelry', 'travel', 'tourism', 'event']
        
        for excl in excluded:
            if excl in industry or excl in text[:100]:
                return False
        
        # Include if relevant
        relevant = [
            'ai', 'insurance', 'health', 'enterprise', 'software', 'automation',
            'agent', 'workflow', 'saas', 'platform', 'analytics', 'data',
            'fintech', 'insurtech', 'healthtech', 'developer', 'code',
            'claims', 'underwriting', 'policy', 'risk', 'medical'
        ]
        
        return any(kw in text[:300] for kw in relevant)
    
    def _get_relevant_features(self, startup: Startup) -> List[FeatureCategory]:
        """Smart feature selection based on startup profile"""
        text = f"{startup.company_description or ''} {startup.shortDescription or ''} {startup.primary_industry or ''}".lower()
        
        relevant = []
        
        # Rule 1: Platform Enablers
        if any(kw in text for kw in ['observability', 'monitoring', 'tracing', 'llm', 'agent']):
            relevant.append(FeatureCategory.F1_1_OBSERVABILITY)
        if any(kw in text for kw in ['orchestration', 'multi-agent', 'workflow engine']):
            relevant.append(FeatureCategory.F1_2_ORCHESTRATION)
        if any(kw in text for kw in ['mlops', 'llm ops', 'model deployment']):
            relevant.append(FeatureCategory.F1_3_LLM_OPS)
        if any(kw in text for kw in ['framework', 'sdk', 'platform', 'langchain']):
            relevant.append(FeatureCategory.F1_4_FRAMEWORKS)
        if any(kw in text for kw in ['vector', 'embedding', 'rag', 'semantic search']):
            relevant.append(FeatureCategory.F1_5_DATA_INFRA)
        if any(kw in text for kw in ['evaluation', 'testing', 'benchmark']):
            relevant.append(FeatureCategory.F1_6_TESTING)
        
        # Rule 2: Service Providers
        if any(kw in text for kw in ['marketing', 'content generation', 'campaign']):
            relevant.append(FeatureCategory.F2_1_MARKETING)
        if any(kw in text for kw in ['sales', 'crm', 'lead generation']):
            relevant.append(FeatureCategory.F2_2_SALES)
        if any(kw in text for kw in ['customer support', 'chatbot', 'contact center']):
            relevant.append(FeatureCategory.F2_3_SUPPORT)
        if any(kw in text for kw in ['recruiting', 'hr', 'talent']):
            relevant.append(FeatureCategory.F2_4_HR)
        if any(kw in text for kw in ['finance', 'invoice', 'procurement', 'contract']):
            relevant.append(FeatureCategory.F2_5_FINANCE)
        if any(kw in text for kw in ['analytics', 'business intelligence', 'insights']):
            relevant.append(FeatureCategory.F2_6_ANALYTICS)
        if any(kw in text for kw in ['workflow', 'automation', 'rpa']):
            relevant.append(FeatureCategory.F2_7_WORKFLOW)
        
        # Rule 3: Insurance
        if any(kw in text for kw in ['claims', 'fnol']):
            relevant.append(FeatureCategory.F3_1_CLAIMS)
        if any(kw in text for kw in ['underwriting', 'risk assessment']):
            relevant.append(FeatureCategory.F3_2_UNDERWRITING)
        if any(kw in text for kw in ['policy', 'administration']):
            relevant.append(FeatureCategory.F3_3_POLICY)
        if any(kw in text for kw in ['distribution', 'agent portal', 'broker']):
            relevant.append(FeatureCategory.F3_4_DISTRIBUTION)
        if 'insurance' in text and any(kw in text for kw in ['digital', 'customer', 'experience']):
            relevant.append(FeatureCategory.F3_5_CUSTOMER_EXP)
        if any(kw in text for kw in ['compliance', 'regulatory', 'kyc']):
            relevant.append(FeatureCategory.F3_6_COMPLIANCE)
        
        # Rule 4: Health
        if any(kw in text for kw in ['health analytics', 'medical ai', 'population health']):
            relevant.append(FeatureCategory.F4_1_HEALTH_ANALYTICS)
        if any(kw in text for kw in ['wellness', 'preventive', 'chronic disease']):
            relevant.append(FeatureCategory.F4_2_WELLNESS)
        if any(kw in text for kw in ['remote monitoring', 'wearables', 'patient monitoring']):
            relevant.append(FeatureCategory.F4_3_MONITORING)
        if any(kw in text for kw in ['telemedicine', 'telehealth', 'virtual care']):
            relevant.append(FeatureCategory.F4_4_TELEMEDICINE)
        if any(kw in text for kw in ['healthcare fraud', 'medical fraud']):
            relevant.append(FeatureCategory.F4_5_FRAUD)
        
        # Rule 5: Dev & Legacy
        if any(kw in text for kw in ['code generation', 'copilot', 'coding']):
            relevant.append(FeatureCategory.F5_1_CODING)
        if any(kw in text for kw in ['test automation', 'qa', 'testing']):
            relevant.append(FeatureCategory.F5_2_TESTING)
        if any(kw in text for kw in ['legacy', 'migration', 'mainframe', 'cobol']):
            relevant.append(FeatureCategory.F5_3_MIGRATION)
        if any(kw in text for kw in ['integration', 'middleware', 'api']):
            relevant.append(FeatureCategory.F5_4_INTEGRATION)
        if any(kw in text for kw in ['code intelligence', 'documentation', 'technical debt']):
            relevant.append(FeatureCategory.F5_5_INTELLIGENCE)
        if any(kw in text for kw in ['devops', 'ci/cd', 'deployment']):
            relevant.append(FeatureCategory.F5_6_DEVOPS)
        
        # Default if nothing matched
        if not relevant:
            relevant = [FeatureCategory.F2_7_WORKFLOW, FeatureCategory.F1_4_FRAMEWORKS]
        
        return list(set(relevant))[:8]  # Max 8 features per startup
    
    def _build_multi_startup_prompt(self, startups: List[Startup]) -> str:
        """Build prompt for batch evaluation"""
        
        startup_blocks = []
        for i, startup in enumerate(startups, 1):
            features = self._get_relevant_features(startup)
            feature_names = [f.value for f in features]
            
            # Build comprehensive startup profile
            funding_info = f"${startup.total_funding/1e6:.1f}M USD" if startup.total_funding and startup.total_funding > 0 else 'Unknown'
            if startup.total_funding and startup.total_funding > 0 and startup.last_funding_date_str:
                funding_info += f" (as of {startup.last_funding_date_str})"
            
            # Get full product description (prioritize extracted_product, then company_description, then shortDescription)
            product_desc = startup.extracted_product or startup.company_description or startup.shortDescription or 'No description available'
            
            # Include additional context from extracted data
            extracted_market = startup.extracted_market or ''
            extracted_tech = startup.extracted_technologies or ''
            
            # Include business types and focus industries for context
            business_type = startup.business_types or 'Unknown'
            focus_industries = startup.focus_industries or ''
            
            # Build enriched startup profile
            startup_blocks.append(f"""
STARTUP {i}: {startup.company_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRODUCT/SERVICE DESCRIPTION:
{product_desc[:700]}

{f"TARGET MARKET: {extracted_market[:300]}" if extracted_market else ""}

{f"TECHNOLOGIES USED: {extracted_tech[:300]}" if extracted_tech else ""}

COMPANY PROFILE:
- Industry: {startup.primary_industry or 'Unknown'}
- Business Type: {business_type}
- Focus Industries: {focus_industries or 'N/A'}
- Website: {startup.website or 'N/A'}

MATURITY & FUNDING:
- Maturity Stage: {startup.maturity or 'Unknown'}
- Funding Stage: {startup.funding_stage or 'Unknown'}
- Total Funding: {funding_info}
- Employees: {startup.employees or 'Unknown'}
- Founded: {startup.founding_year or 'Unknown'}
- Location: {startup.company_city or 'Unknown'}, {startup.company_country or 'Unknown'}

FEATURES TO EVALUATE: {', '.join(feature_names)}
""")
        
        startups_text = "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n".join(startup_blocks)
        
        prompt = f"""You are an INSURANCE INDUSTRY EXPERT evaluating {len(startups)} startups for AXA, a global insurance company.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVALUATION PRINCIPLE: Focus on CORE BUSINESS ONLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are an INSURANCE EXPERT evaluating startups for AXA, a global insurance company.

For EACH startup, carefully read their PRODUCT/SERVICE DESCRIPTION and ask:

1. "What does this company SELL as their PRIMARY product/service?"
2. "What specific problem does their core product solve?"
3. "Who is their target customer and what do they buy?"

Classify based on WHAT THEY SELL (their core product/service), NOT:
❌ What they use internally (Pandatron uses AI agents but SELLS consulting - Rule 2)
❌ What they could theoretically enable (focus on their actual product)
❌ Secondary features or capabilities (only their main offering)
❌ Who might use their product (focus on what the product IS, not who uses it)
❌ Technology they use (focus on what they deliver to customers)

EXAMPLES OF CORRECT CATEGORIZATION:
✓ "Pandatron is an AI agent that helps Fortune 500 identify opportunities"
  → SELLS: AI adoption consulting services to enterprises
  → Rule 2, F2.7_workflow_automation, Provider=true
  
✓ "Bankify provides Smart Collections for debt recovery in financial institutions"
  → SELLS: Debt collection software to banks/lenders (NOT insurance)
  → Rule 2, F2.7_workflow_automation, Provider=false ("Debt recovery for finance sector - not insurance relevant")
  
✓ "LangSmith is a platform for monitoring AI agents"
  → SELLS: Monitoring SaaS platform
  → Rule 1, F1.1_observability_monitoring, Provider=true
  
✓ "Tractable sells claims AI to insurance companies"
  → SELLS: Claims automation software to insurers
  → Rule 3, F3.1_claims_management, Provider=true
  
✓ "Intercom provides customer support platform for enterprises"
  → SELLS: Support platform SaaS
  → Rule 2, F2.3_customer_support, Provider=true

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AXA'S 5 STRATEGIC RULES (Pick ONE Primary Rule per Startup)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RULE 1 - AGENTIC PLATFORM ENABLERS (Infrastructure They SELL)
  Core Business: Selling AI/ML/Agent infrastructure, frameworks, monitoring tools
  Examples: LangSmith (sells monitoring SaaS), Pinecone (sells vector DB), CrewAI (sells agent framework)
  Categories: F1.1-F1.6 (Observability, Orchestration, LLM Ops, Frameworks, Data Infra, Testing)
  
RULE 2 - SERVICE PROVIDERS (Enterprise Solutions They SELL)
  Core Business: Selling ready-to-deploy B2B enterprise solutions (any industry except insurance)
  Examples: Intercom (sells support platform), Gong (sells sales tool), Jasper (sells marketing automation)
  Categories: F2.1-F2.7 (Marketing, Sales, Support, HR, Finance, Analytics, Workflow)
  NOT: B2C apps, marketplaces, platforms
  
RULE 3 - INSURANCE SOLUTIONS (Insurance Tools They SELL)
  Core Business: Selling insurance-specific software/solutions TO insurance companies
  Examples: Tractable (sells claims AI), Zelros (sells underwriting AI), Shift Technology (sells fraud detection)
  Categories: F3.1-F3.6 (Claims, Underwriting, Policy, Distribution, Customer Experience, Compliance)
  
RULE 4 - HEALTH INNOVATIONS (Health Tech They SELL with Insurance Relevance)
  Core Business: Selling healthcare/health tech that insurers can use/benefit from
  Examples: Omada Health (sells wellness programs), Komodo Health (sells health data platform), Teladoc (sells telemedicine)
  Categories: F4.1-F4.5 (Health Analytics, Wellness, Monitoring, Telemedicine, Fraud)
  
RULE 5 - DEV & LEGACY (Development Tools They SELL)
  Core Business: Selling software development, testing, modernization, or integration tools
  Examples: GitHub Copilot (sells coding assistant), Harness (sells CI/CD platform), Heirloom (sells legacy migration)
  Categories: F5.1-F5.6 (Coding, Testing, Migration, Integration, Code Intelligence, DevOps)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STARTUPS TO EVALUATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{startups_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVALUATION STEPS FOR EACH STARTUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: Identify Core Business (READ CAREFULLY)
Look at the PRODUCT/SERVICE DESCRIPTION and ask:
- What is their PRIMARY product/service they SELL TO CUSTOMERS?
- Who PAYS them and for what specific deliverable/solution?
- What is their MAIN REVENUE SOURCE?

CRITICAL: Distinguish "What they ARE" vs "What they SELL":
- "Company X is an AI agent that helps enterprises..." → They SELL: consulting/services (Rule 2)
- "Company Y is a platform that provides..." → They SELL: SaaS platform (Rule 1 or 2)
- "Company Z sells monitoring tools for..." → They SELL: monitoring product (Rule 1)

Look for revenue-generating phrases:
- "We help clients..." → Consulting/services (Rule 2)
- "We provide a platform..." → Platform product (Rule 1 or 2)
- "We sell software that..." → Software product (Rule 1-5)
- "We offer a solution for..." → Solution product (Rule 2-5)

STEP 2: Pick ONE Primary Rule
- Based on core business, which ONE rule matches best?
- Rule 1: If they SELL AI/agent infrastructure
- Rule 2: If they SELL enterprise business solutions
- Rule 3: If they SELL insurance-specific tools
- Rule 4: If they SELL health tech with insurance applicability
- Rule 5: If they SELL development/modernization tools

STEP 3: Mark ONLY Core Features
- Within the primary rule, which features match their CORE offering?
- ONLY mark features that are central to their business model
- Do NOT mark features they could theoretically support
- Do NOT mark features based on internal tech they use

STEP 4: Provider Assessment - CRITICAL QUESTION
Ask: "Can AXA use this startup as a PROVIDER (buy their core product/service)?"

✅ TRUE = AXA can become a paying B2B customer for their solution:
- Enterprise SaaS/software products
- Professional services sold to enterprises (consulting, implementation)
- B2B platforms/tools with enterprise pricing
- Insurance-specific solutions sold to carriers
- Health tech sold to payers/insurers
- Infrastructure/platform tools sold to enterprises

❌ FALSE = AXA CANNOT use them as a provider:
- B2C consumer apps (no B2B offering)
- Insurance carriers (direct competitors)
- Marketplaces/platforms where AXA would be listed (not a buyable solution)
- Irrelevant industries (gaming, food, entertainment)
- Early-stage concepts with no product yet
- Companies that sell to consumers, not enterprises

STEP 5: Business Leverage (Insurance Perspective)
- If TRUE: Provide specific insurance use cases from an INSURANCE EXPERT view:
  * How would AXA's claims, underwriting, distribution, or IT teams use this?
  * What specific insurance processes would it improve?
  * What value does it bring to an insurance company specifically?
  
- If FALSE: Clearly state why (e.g., "B2C consumer banking app - no enterprise solution", "Insurance carrier competitor", "Gaming platform - not relevant to insurance")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MATURITY WEIGHTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Consider maturity/funding/stage in confidence scoring:
- Series C+, 100+ employees, $50M+ funding → Confidence: 90-100
- Series B, 50-100 employees, $10-50M funding → Confidence: 75-90
- Series A, 20-50 employees, $5-10M funding → Confidence: 60-75
- Seed/Pre-seed, <20 employees, <$5M funding → Confidence: 40-60
- Very early (founded <1 year) → Confidence: 20-40

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMMON MISTAKES TO AVOID
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ WRONG: "Pandatron uses AI agents internally" → Rule 1 (Platform Enablers)
✅ RIGHT: "Pandatron SELLS: 'We help Fortune 500 identify AI opportunities' = consulting" → Rule 2, F2.7

❌ WRONG: "Bankify helps enterprises" → Provider = true
✅ RIGHT: "Bankify sells to finance/banks for debt collection, not insurance" → Provider = false

❌ WRONG: "This tool mentions claims in description" → Mark as insurance
✅ RIGHT: Only mark insurance (Rule 3) if they explicitly sell TO insurance companies

❌ WRONG: "They describe themselves as 'an AI agent'" → Rule 1
✅ RIGHT: Look at what they CHARGE FOR: "help clients" = services (Rule 2), "sell platform" = product (Rule 1)

READ THE PRODUCT DESCRIPTION CAREFULLY. Focus on:
1. What customers PAY FOR (not what the company calls itself)
2. Who their BUYERS are (B2B enterprise? Insurance? Health? Banks?)
3. What SPECIFIC PROBLEM they solve for those buyers

❌ WRONG: "Bankify helps with finance" → Mark Rule 2.5
✅ RIGHT: "Bankify is B2C consumer banking" → Provider = false

❌ WRONG: "Has APIs, could integrate" → Mark Rule 5.4
✅ RIGHT: "Is integration their core business?" → If no, don't mark

❌ WRONG: "Uses AI internally" → Mark Rule 1
✅ RIGHT: "Do they SELL AI infrastructure?" → If no, don't mark

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REQUIRED JSON OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[
  {{
    "startup_name": "Company Name",
    "primary_rule": "Rule X" (ONE rule only based on core business),
    "evaluations": [
      {{
        "feature": "FX.Y_category_name",
        "matches": true/false (only if CORE to their business),
        "confidence": 0-100 (weighted by maturity),
        "reasoning": "Brief reason why this IS or IS NOT core to their business"
      }},
      ...
    ],
    "can_use_as_provider": true/false (Can AXA buy their core product?),
    "business_leverage": "If true: specific insurance use cases. If false: why not suitable (e.g., 'B2C consumer app', 'Marketplace platform', 'Insurance carrier competitor', 'Gaming industry - not relevant')"
  }},
  ...
]

RESPOND WITH ONLY THE JSON ARRAY. NO OTHER TEXT."""

        return prompt
    
    async def _call_llm_async(self, prompt: str, session: aiohttp.ClientSession, retry: int = 3) -> Optional[str]:
        """Async LLM call with retry"""
        
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": NVIDIA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 4000
        }
        
        for attempt in range(retry):
            try:
                async with session.post(
                    f"{NVIDIA_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        logger.warning(f"API error {response.status}, attempt {attempt+1}/{retry}")
                        if attempt < retry - 1:
                            await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"LLM error: {e}, attempt {attempt+1}/{retry}")
                if attempt < retry - 1:
                    await asyncio.sleep(2 ** attempt)
        
        return None
    
    def _get_rule_from_feature(self, feature: str) -> str:
        """Extract rule number from feature code"""
        if feature.startswith("F1."):
            return "Rule 1"
        elif feature.startswith("F2."):
            return "Rule 2"
        elif feature.startswith("F3."):
            return "Rule 3"
        elif feature.startswith("F4."):
            return "Rule 4"
        elif feature.startswith("F5."):
            return "Rule 5"
        return "Unknown"
    
    async def _evaluate_startup_batch_async(
        self,
        startups: List[Startup],
        session: aiohttp.ClientSession
    ) -> List[StartupEvaluation]:
        """Evaluate batch of startups"""
        
        try:
            prompt = self._build_multi_startup_prompt(startups)
            response_text = await self._call_llm_async(prompt, session)
            
            if not response_text:
                logger.error(f"Failed to evaluate batch of {len(startups)}")
                return []
            
            # Parse JSON
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                results = json.loads(json_str)
            else:
                results = json.loads(response_text)
            
            # Convert to evaluations
            evaluations = []
            for startup, result in zip(startups, results):
                category_matches = []
                rule_scores = {}
                
                for eval_data in result.get('evaluations', []):
                    feature = eval_data['feature']
                    rule = self._get_rule_from_feature(feature)
                    
                    category_matches.append(CategoryMatch(
                        category=feature,
                        rule=rule,
                        matches=eval_data['matches'],
                        confidence=eval_data['confidence'],
                        reasoning=eval_data['reasoning']
                    ))
                    
                    # Track rule scores
                    if eval_data['matches']:
                        if rule not in rule_scores:
                            rule_scores[rule] = []
                        rule_scores[rule].append(eval_data['confidence'])
                
                # Extract provider assessment
                can_use_as_provider = result.get('can_use_as_provider', False)
                business_leverage = result.get('business_leverage', 'No clear business fit identified.')
                primary_rule = result.get('primary_rule', 'Unknown')
                
                # Calculate overall score with enhanced factors
                matched_rules = list(rule_scores.keys())
                
                # Base score: Flat 20 points if can deliver (reduced from 40)
                # All rules now worth same as they're equally important to AXA
                base_score = 20 if matched_rules else 0
                
                # Rule match bonus (max 25 points) - INCREASED
                # More emphasis on rule matches as primary driver
                rule_match_bonus = 0
                if len(matched_rules) >= 3:
                    rule_match_bonus = 25
                elif len(matched_rules) == 2:
                    rule_match_bonus = 15
                elif len(matched_rules) == 1:
                    rule_match_bonus = 10
                
                # Confidence boost (max 25 points) - INCREASED from 20
                avg_confidence = sum([avg for scores in rule_scores.values() for avg in scores]) / len([s for scores in rule_scores.values() for s in scores]) if rule_scores else 0
                confidence_points = (avg_confidence / 100) * 25
                
                # Maturity bonus (max 12 points) - REDUCED from 15
                maturity_points = 0
                if startup.maturity:
                    maturity_lower = startup.maturity.lower()
                    if 'scaleup' in maturity_lower or 'established' in maturity_lower:
                        maturity_points = 12
                    elif 'scaling' in maturity_lower or 'growth' in maturity_lower:
                        maturity_points = 8
                    elif 'deploying' in maturity_lower or 'startup' in maturity_lower:
                        maturity_points = 5
                    elif 'validating' in maturity_lower:
                        maturity_points = 3
                    elif 'emerging' in maturity_lower:
                        maturity_points = 1
                
                # Funding stage bonus (max 10 points) - UNCHANGED
                funding_points = 0
                if startup.funding_stage:
                    stage_lower = startup.funding_stage.lower()
                    if 'series c' in stage_lower or 'series d' in stage_lower or 'series e' in stage_lower:
                        funding_points = 10
                    elif 'series b' in stage_lower:
                        funding_points = 8
                    elif 'series a' in stage_lower:
                        funding_points = 6
                    elif 'seed' in stage_lower:
                        funding_points = 4
                
                # Total funding boost (max 8 points) - INCREASED from 5
                funding_amount_points = 0
                if startup.total_funding:
                    if startup.total_funding >= 100_000_000:  # $100M+
                        funding_amount_points = 8
                    elif startup.total_funding >= 50_000_000:  # $50M+
                        funding_amount_points = 6
                    elif startup.total_funding >= 20_000_000:  # $20M+
                        funding_amount_points = 5
                    elif startup.total_funding >= 10_000_000:  # $10M+
                        funding_amount_points = 3
                    elif startup.total_funding >= 5_000_000:   # $5M+
                        funding_amount_points = 1
                
                # Geographic bonus (max 15 points) - REDUCED from 20 but still substantial
                geo_points = 0
                # Check multiple possible country fields
                country = startup.company_country or startup.billingCountry or ''
                
                if country:
                    country_code = country.upper().strip()
                    # EU countries get substantial bonus (AXA is EU-focused)
                    eu_countries = ['DE', 'FR', 'GB', 'UK', 'ES', 'IT', 'NL', 'BE', 'SE', 'FI', 'DK', 'NO', 'AT', 'CH', 'LU', 'IE', 'PL', 'CZ', 'PT', 'GR', 'HU', 'RO', 'SK', 'HR']
                    
                    if country_code in eu_countries:
                        geo_points = 15  # Reduced from 20 to balance other factors
                    elif country_code in ['US', 'CA']:
                        geo_points = 8   # North America
                    elif country_code in ['SG', 'JP', 'AU', 'KR', 'NZ']:
                        geo_points = 5   # Asia-Pacific allies
                
                overall_score = min(100, base_score + rule_match_bonus + confidence_points + maturity_points + funding_points + funding_amount_points + geo_points)
                
                # Adjust score if not usable as provider (REDUCED penalty)
                if not can_use_as_provider and overall_score > 0:
                    overall_score = overall_score * 0.6  # 40% penalty (was 70%)
                
                # Determine tier
                if overall_score >= 80:
                    tier = "Tier 1: Critical Priority"
                elif overall_score >= 60:
                    tier = "Tier 2: High Priority"
                elif overall_score >= 40:
                    tier = "Tier 3: Medium Priority"
                else:
                    tier = "Tier 4: Low Priority"
                
                
                matched = [m for m in category_matches if m.matches]
                
                # Enhanced summary with detailed factors
                provider_status = "✓ Usable as provider" if can_use_as_provider else "✗ Not suitable as provider"
                maturity_info = f"Maturity: {startup.maturity or 'Unknown'}"
                funding_info = f"Stage: {startup.funding_stage or 'Unknown'}"
                if startup.total_funding and startup.total_funding > 0:
                    funding_info += f" (${startup.total_funding/1e6:.1f}M)"
                
                summary = f"Primary: {primary_rule}. Matches {len(matched)} features across {len(matched_rules)} rules. Score: {overall_score:.0f}%. {provider_status}. {maturity_info}. {funding_info}."
                
                evaluations.append(StartupEvaluation(
                    startup_id=startup.id,
                    startup_name=startup.company_name,
                    evaluation_date=datetime.now().isoformat(),
                    categories_matched=category_matches,
                    matched_rules=matched_rules,
                    rule_scores=rule_scores,
                    overall_score=overall_score,
                    priority_tier=tier,
                    axa_fit_summary=summary,
                    can_use_as_provider=can_use_as_provider,
                    business_leverage=business_leverage
                ))
            
            return evaluations
            
        except Exception as e:
            logger.error(f"Batch evaluation error: {e}")
            return []
    
    async def _worker(
        self,
        queue: asyncio.Queue,
        session: aiohttp.ClientSession,
        results_list: List[Dict],
        worker_id: int,
        checkpoint_interval: int = 10
    ):
        """Async worker with periodic checkpointing"""
        
        batches_processed = 0
        
        while True:
            try:
                batch = await queue.get()
                if batch is None:
                    break
                
                evaluations = await self._evaluate_startup_batch_async(batch, session)
                
                for eval in evaluations:
                    eval_dict = {
                        'startup_id': eval.startup_id,
                        'startup_name': eval.startup_name,
                        'evaluation_date': eval.evaluation_date,
                        'categories_matched': [asdict(cm) for cm in eval.categories_matched],
                        'matched_rules': eval.matched_rules,
                        'rule_scores': eval.rule_scores,
                        'overall_score': eval.overall_score,
                        'priority_tier': eval.priority_tier,
                        'axa_fit_summary': eval.axa_fit_summary,
                        'can_use_as_provider': eval.can_use_as_provider,
                        'business_leverage': eval.business_leverage
                    }
                    results_list.append(eval_dict)
                    self.evaluated_ids.add(eval.startup_id)
                
                batches_processed += 1
                
                # Periodic checkpoint save (every N batches per worker)
                if batches_processed % checkpoint_interval == 0:
                    self._save_checkpoint(results_list)
                    logger.info(f"Worker {worker_id}: 💾 Checkpoint saved ({len(self.evaluated_ids)} total)")
                else:
                    logger.info(f"Worker {worker_id}: Batch complete ({len(self.evaluated_ids)} total)")
                
                queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                # Save checkpoint on error
                try:
                    self._save_checkpoint(results_list)
                    logger.info(f"Worker {worker_id}: 💾 Emergency checkpoint saved after error")
                except:
                    pass
                queue.task_done()
    
    async def evaluate_all_async(
        self,
        resume: bool = False,
        max_startups: Optional[int] = None,
        startup_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """Async evaluation with automatic checkpointing"""
        
        checkpoint_data = {'results': []}
        if resume:
            checkpoint_data = self._load_checkpoint()
            if checkpoint_data.get('results'):
                logger.info(f"📂 Resuming from checkpoint:")
                logger.info(f"   - Already evaluated: {len(self.evaluated_ids)} startups")
                logger.info(f"   - Last updated: {checkpoint_data.get('last_updated', 'Unknown')}")
        
        results = checkpoint_data.get('results', [])
        
        # Get startups with safe query
        try:
            # Query all valid startups
            from sqlalchemy import text, and_
            all_startups = []
            
            if startup_ids:
                # Query specific startups by ID
                from models_startup import Startup as StartupModel
                startup_models = self.db.query(StartupModel).filter(StartupModel.id.in_(startup_ids)).all()
                all_startups = startup_models
            else:
                with self.db.begin():
                    raw_results = self.db.execute(
                        text("SELECT id, company_name, company_description, shortDescription, primary_industry, business_types, website, maturity, funding_stage, total_funding, last_funding_date_str, employees, founding_year, company_city, company_country FROM startups WHERE company_name IS NOT NULL")
                    )
                
                    for row in raw_results:
                        startup = Startup(
                            id=row[0],
                            company_name=row[1],
                            company_description=row[2],
                            shortDescription=row[3],
                            primary_industry=row[4],
                            business_types=row[5],
                            website=row[6] if len(row) > 6 else None,
                            maturity=row[7] if len(row) > 7 else None,
                            funding_stage=row[8] if len(row) > 8 else None,
                            total_funding=row[9] if len(row) > 9 else None,
                            last_funding_date_str=row[10] if len(row) > 10 else None,
                            employees=row[11] if len(row) > 11 else None,
                            founding_year=row[12] if len(row) > 12 else None,
                            company_city=row[13] if len(row) > 13 else None,
                            company_country=row[14] if len(row) > 14 else None
                        )
                        all_startups.append(startup)
        except Exception as e:
            logger.error(f"Database error: {e}")
            return results
        
        logger.info(f"📊 Total startups: {len(all_startups)}")
        
        # Filter
        if startup_ids:
            # Skip filtering if specific IDs requested
            filtered = all_startups
        else:
            filtered = [s for s in all_startups if self._should_evaluate(s) and s.id not in self.evaluated_ids]
            logger.info(f"📊 After filtering: {len(filtered)} to evaluate")
        
        if max_startups and not startup_ids:
            filtered = filtered[:max_startups]
            logger.info(f"📊 Limited to: {max_startups} startups")
        
        # Create batches
        batches = [filtered[i:i+self.batch_size] for i in range(0, len(filtered), self.batch_size)]
        
        logger.info(f"🚀 Starting: {len(batches)} batches with {self.workers} workers")
        
        start_time = datetime.now()
        
        # Queue and workers
        queue = asyncio.Queue()
        for batch in batches:
            await queue.put(batch)
        
        for _ in range(self.workers):
            await queue.put(None)
        
        # HTTP session
        connector = aiohttp.TCPConnector(limit=self.workers * 2)
        async with aiohttp.ClientSession(connector=connector) as session:
            workers = [
                asyncio.create_task(self._worker(queue, session, results, i, self.checkpoint_interval))
                for i in range(self.workers)
            ]
            
            # Add signal handler for graceful shutdown
            try:
                await asyncio.gather(*workers)
            except KeyboardInterrupt:
                logger.warning("\n⚠️  Interrupted! Saving checkpoint...")
                self._save_checkpoint(results)
                logger.info("💾 Checkpoint saved. Use --resume to continue.")
                raise
        
        # Save final checkpoint
        self._save_checkpoint(results)
        logger.info("💾 Final checkpoint saved")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Complete!")
        logger.info(f"⏱️  Time: {int(elapsed//60)}m {int(elapsed%60)}s")
        logger.info(f"📊 Evaluated: {len(self.evaluated_ids)} startups")
        logger.info(f"{'='*60}")
        
        return results
    
    def close(self):
        self.db.close()


def main():
    parser = argparse.ArgumentParser(description='Enhanced AXA Evaluator with Auto-Checkpointing')
    parser.add_argument('--workers', type=int, default=10, help='Concurrent workers')
    parser.add_argument('--batch-size', type=int, default=3, help='Startups per batch')
    parser.add_argument('--checkpoint-interval', type=int, default=10, help='Save checkpoint every N batches per worker')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    parser.add_argument('--max-startups', type=int, help='Limit for testing')
    parser.add_argument('--startup-ids', type=str, help='Comma-separated list of startup IDs to evaluate')
    parser.add_argument('--output', type=str, default='downloads/axa_enhanced_results.json')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🚀 AXA ENHANCED EVALUATOR - 35+ Feature Categories")
    print("="*80)
    
    evaluator = EnhancedEvaluator(
        workers=args.workers, 
        batch_size=args.batch_size,
        checkpoint_interval=args.checkpoint_interval
    )
    
    try:
        # Parse startup IDs if provided
        startup_ids = None
        if args.startup_ids:
            startup_ids = [int(x.strip()) for x in args.startup_ids.split(',')]
            logger.info(f"🎯 Evaluating specific startups: {startup_ids}")
        
        results = asyncio.run(evaluator.evaluate_all_async(
            resume=args.resume,
            max_startups=args.max_startups,
            startup_ids=startup_ids
        ))
        
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✅ Results saved to: {output_path}")
        
        # Print summary
        if results:
            tier_counts = {}
            rule_counts = {}
            
            for r in results:
                tier = r['priority_tier']
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
                
                for rule in r.get('matched_rules', []):
                    rule_counts[rule] = rule_counts.get(rule, 0) + 1
            
            print("\n" + "="*60)
            print("📊 SUMMARY")
            print("="*60)
            print("\nBy Tier:")
            for tier, count in sorted(tier_counts.items()):
                print(f"  {tier}: {count}")
            
            print("\nBy Rule:")
            for rule, count in sorted(rule_counts.items()):
                print(f"  {rule}: {count}")
        
    finally:
        evaluator.close()


if __name__ == '__main__':
    main()
