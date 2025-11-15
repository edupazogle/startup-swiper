#!/usr/bin/env python3
"""
AXA Comprehensive Startup Evaluator with NVIDIA NIM LLM

This script performs extensive AI-powered evaluation of ALL startups in the database
to identify opportunities for AXA across multiple strategic categories.

Categories Evaluated:
1. Agentic Platform Enablers - Infrastructure for building AI agents
2. Agentic Solution Providers - Ready-to-use AI agent solutions
3. Workflow Automation - Business process automation
4. Sales Training & Coaching - AI-powered sales enablement
5. Insurance Solutions - General insurance tech (underwriting, claims, policy)
6. Underwriting Triage - AI for risk assessment and underwriting
7. Claims Recovery & Subrogation - Automated claims processing
8. Coding Automation - Developer tools and AI coding assistants
9. Health & Wellness - Digital health platforms for employee benefits
10. AI Evals & Testing - LLM evaluation and testing frameworks
11. LLM Observability - Monitoring and debugging for AI systems
12. Contact Center Solutions - AI for customer service and support

Features:
- Uses NVIDIA NIM (DeepSeek-R1) for deep analysis
- Evaluates ALL startups with no filtering
- Multi-category scoring (startup can match multiple categories)
- Extensive prompt engineering for thorough evaluation
- Confidence scoring for each category match
- Detailed reasoning for each evaluation
- Progress tracking and checkpointing
- Parallel processing for speed

Usage:
    # Run full evaluation
    python3 api/axa_comprehensive_evaluator.py
    
    # Resume from checkpoint
    python3 api/axa_comprehensive_evaluator.py --resume
    
    # Evaluate specific categories only
    python3 api/axa_comprehensive_evaluator.py --categories agentic,insurance,health
    
    # Run with different batch size
    python3 api/axa_comprehensive_evaluator.py --batch-size 5
    
    # Export results to JSON
    python3 api/axa_comprehensive_evaluator.py --output results/axa_evaluation.json
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import asyncio
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Imports
from database import SessionLocal
from models_startup import Startup
from llm_config import llm_completion_sync, is_nvidia_nim_configured


# ====================
# CATEGORY DEFINITIONS
# ====================

class CategoryType(Enum):
    """AXA Strategic Categories"""
    AGENTIC_PLATFORM = "agentic_platform_enablers"
    AGENTIC_SOLUTIONS = "agentic_solution_providers"
    WORKFLOW_AUTOMATION = "workflow_automation"
    SALES_TRAINING = "sales_training_coaching"
    INSURANCE_GENERAL = "insurance_general"
    UNDERWRITING_TRIAGE = "underwriting_triage"
    CLAIMS_RECOVERY = "claims_recovery_subrogation"
    CODING_AUTOMATION = "coding_automation"
    HEALTH_WELLNESS = "health_wellness"
    AI_EVALS = "ai_evals_testing"
    LLM_OBSERVABILITY = "llm_observability"
    CONTACT_CENTER = "contact_center_solutions"


@dataclass
class CategoryMatch:
    """Represents a match between a startup and a category"""
    category: str
    matches: bool
    confidence: float  # 0-100
    reasoning: str
    key_indicators: List[str]
    potential_use_cases: List[str]
    risk_factors: List[str]


@dataclass
class StartupEvaluation:
    """Complete evaluation result for a startup"""
    startup_id: int
    startup_name: str
    evaluation_date: str
    categories_matched: List[CategoryMatch]
    overall_score: float
    priority_tier: str
    recommended_actions: List[str]
    axa_fit_summary: str


# ====================
# CATEGORY PROMPTS
# ====================

CATEGORY_DEFINITIONS = {
    CategoryType.AGENTIC_PLATFORM: {
        "name": "Agentic Platform Enablers",
        "description": """Infrastructure, frameworks, and tools for building, deploying, and managing AI agents.
        
        Key characteristics:
        - Agent orchestration frameworks (LangChain, CrewAI, AutoGPT-style)
        - Multi-agent coordination platforms
        - Agent workflow builders and low-code platforms
        - Agent deployment and hosting infrastructure
        - Agent monitoring and observability tools
        - Vector databases and embeddings infrastructure
        - Agent mesh and communication protocols
        - Agent testing and simulation frameworks
        - Tool/function calling infrastructure
        - Agent memory and state management systems
        
        Examples: LangChain, LlamaIndex, agent orchestration platforms, vector DB providers""",
        "keywords": [
            "agent orchestration", "multi-agent", "agent framework", "agent platform",
            "agent builder", "agent workflow", "autonomous agent", "agent infrastructure",
            "vector database", "embeddings", "RAG", "LangChain", "agent mesh",
            "agent coordination", "agent testing", "agent deployment", "agent tools"
        ]
    },
    
    CategoryType.AGENTIC_SOLUTIONS: {
        "name": "Agentic Solution Providers",
        "description": """Ready-to-use AI agent applications and vertical-specific agent solutions that AXA can adopt.
        
        Key characteristics:
        - Pre-built AI agents for specific business functions
        - Vertical-specific autonomous agents (insurance, finance, HR)
        - Intelligent automation agents
        - Conversational AI agents with complex reasoning
        - Research and analysis agents
        - Customer service agents
        - Data processing agents
        - Autonomous workflow agents
        - Decision-making agents
        - Task completion agents
        
        Examples: Customer support agents, insurance claim agents, research agents, data analysis agents""",
        "keywords": [
            "AI agent", "autonomous", "intelligent assistant", "AI workforce",
            "virtual agent", "smart agent", "cognitive agent", "agentic AI",
            "agent solution", "agent application", "task automation agent",
            "decision agent", "research agent", "analysis agent"
        ]
    },
    
    CategoryType.WORKFLOW_AUTOMATION: {
        "name": "Workflow Automation",
        "description": """Business process automation, intelligent workflows, and BPM tools.
        
        Key characteristics:
        - Business process automation (BPA)
        - Robotic process automation (RPA)
        - Workflow orchestration and management
        - Document processing automation
        - Approval workflows and routing
        - Integration platforms (iPaaS)
        - Low-code/no-code automation
        - Process mining and optimization
        - Task automation and scheduling
        - API orchestration and workflow
        
        Examples: Zapier, UiPath, Automation Anywhere, workflow engines, process automation""",
        "keywords": [
            "workflow automation", "process automation", "BPA", "RPA",
            "workflow orchestration", "task automation", "business process",
            "document automation", "approval workflow", "process management",
            "workflow engine", "automation platform", "iPaaS", "process mining"
        ]
    },
    
    CategoryType.SALES_TRAINING: {
        "name": "Sales Training & Coaching",
        "description": """AI-powered sales enablement, training, and coaching platforms.
        
        Key characteristics:
        - AI-powered sales coaching and training
        - Conversation intelligence for sales
        - Sales performance analytics
        - Role-playing and simulation tools
        - Sales content and playbook management
        - Onboarding and enablement platforms
        - Call analysis and feedback
        - Pipeline coaching and forecasting
        - Deal coaching and guidance
        - Skills assessment and development
        
        Examples: Gong, Chorus, sales coaching platforms, training simulators""",
        "keywords": [
            "sales training", "sales coaching", "sales enablement",
            "conversation intelligence", "call coaching", "sales performance",
            "sales analytics", "deal coaching", "pipeline coaching",
            "sales development", "onboarding", "sales playbook",
            "role play", "sales simulation", "sales skills"
        ]
    },
    
    CategoryType.INSURANCE_GENERAL: {
        "name": "Insurance Solutions (General)",
        "description": """General insurance technology solutions across the insurance lifecycle.
        
        Key characteristics:
        - Policy administration systems
        - Claims management platforms
        - Insurance CRM and customer portals
        - Rating and quoting engines
        - Distribution and agency management
        - Insurance data and analytics
        - Fraud detection for insurance
        - Reinsurance technology
        - Insurance core systems
        - Compliance and regulatory tech
        
        Examples: Insurtech platforms, policy admin, claims systems, insurance analytics""",
        "keywords": [
            "insurance", "insurtech", "policy", "claims", "underwriting",
            "insurance platform", "insurance tech", "claims management",
            "policy administration", "insurance analytics", "insurance data",
            "fraud detection insurance", "reinsurance", "insurance CRM",
            "quoting engine", "rating engine", "insurance distribution"
        ]
    },
    
    CategoryType.UNDERWRITING_TRIAGE: {
        "name": "Underwriting Triage & Risk Assessment",
        "description": """AI-powered underwriting automation, risk assessment, and triage systems.
        
        Key characteristics:
        - Automated underwriting decisions
        - Risk scoring and assessment AI
        - Application triage and routing
        - Medical underwriting automation
        - Straight-through processing (STP)
        - Risk analytics and modeling
        - Data enrichment for underwriting
        - Decisioning engines
        - Mortality and morbidity assessment
        - Underwriting workbench and tools
        
        Examples: Automated underwriting, risk scoring, triage systems, decisioning platforms""",
        "keywords": [
            "underwriting", "risk assessment", "triage", "risk scoring",
            "automated underwriting", "underwriting automation", "STP",
            "straight-through processing", "underwriting decisioning",
            "risk analytics", "medical underwriting", "application triage",
            "risk modeling", "underwriting AI", "risk evaluation"
        ]
    },
    
    CategoryType.CLAIMS_RECOVERY: {
        "name": "Claims Recovery & Subrogation",
        "description": """Automated claims processing, recovery, subrogation, and fraud detection.
        
        Key characteristics:
        - Claims automation and AI
        - First notice of loss (FNOL) automation
        - Claims triage and routing
        - Fraud detection and prevention
        - Subrogation identification and recovery
        - Claims analytics and insights
        - Document processing for claims
        - Damage assessment AI
        - Claims adjudication automation
        - Recovery and collection systems
        
        Examples: Claims automation, fraud detection, subrogation platforms, FNOL systems""",
        "keywords": [
            "claims", "claims automation", "FNOL", "first notice of loss",
            "claims processing", "fraud detection", "subrogation", "recovery",
            "claims triage", "claims adjudication", "damage assessment",
            "claims analytics", "claims AI", "fraud prevention", "loss recovery",
            "claims investigation", "salvage", "claims routing"
        ]
    },
    
    CategoryType.CODING_AUTOMATION: {
        "name": "Coding Automation & Developer Tools",
        "description": """AI-powered coding assistants, code generation, and developer productivity tools.
        
        Key characteristics:
        - AI code generation and completion
        - Code review and analysis automation
        - Test generation and automation
        - Legacy code modernization
        - Code migration and translation
        - Documentation generation
        - Bug detection and fixing
        - DevOps automation
        - CI/CD and deployment automation
        - Code intelligence and search
        
        Examples: GitHub Copilot, code generation tools, test automation, legacy modernization""",
        "keywords": [
            "code generation", "AI coding", "code assistant", "copilot",
            "developer tools", "test automation", "code review",
            "legacy modernization", "code migration", "devops automation",
            "CI/CD", "code intelligence", "code analysis", "bug detection",
            "documentation generation", "code completion", "programming AI"
        ]
    },
    
    CategoryType.HEALTH_WELLNESS: {
        "name": "Health & Wellness Platforms",
        "description": """Digital health, telemedicine, wellness, and employee health benefit platforms that AXA can integrate.
        
        Key characteristics:
        - Corporate wellness platforms
        - Employee health benefits
        - Telemedicine and virtual care
        - Health analytics and population health
        - Mental health and wellbeing
        - Chronic disease management
        - Preventive health and screening
        - Health data platforms
        - Wearables and remote monitoring
        - Health insurance integration
        - B2B health platforms
        
        Examples: Corporate wellness, telemedicine, mental health platforms, health benefits""",
        "keywords": [
            "health", "wellness", "telemedicine", "digital health",
            "employee wellness", "corporate wellness", "mental health",
            "telehealth", "health platform", "population health",
            "chronic disease", "preventive health", "health analytics",
            "health benefits", "wellbeing", "health insurance",
            "care management", "health engagement", "B2B health"
        ]
    },
    
    CategoryType.AI_EVALS: {
        "name": "AI Evaluation & Testing",
        "description": """LLM evaluation, testing frameworks, and quality assurance for AI systems.
        
        Key characteristics:
        - LLM evaluation frameworks
        - AI testing and validation
        - Model benchmarking
        - Output quality assessment
        - Prompt testing and optimization
        - AI safety and alignment testing
        - Performance evaluation tools
        - Regression testing for AI
        - Red teaming for AI
        - Evaluation datasets and metrics
        
        Examples: LLM evaluation tools, AI testing platforms, model assessment, benchmarking""",
        "keywords": [
            "AI evaluation", "LLM testing", "model evaluation", "AI evals",
            "benchmarking", "testing framework", "quality assessment",
            "prompt testing", "AI testing", "evaluation framework",
            "model testing", "AI validation", "performance testing",
            "red teaming", "AI safety testing", "eval platform"
        ]
    },
    
    CategoryType.LLM_OBSERVABILITY: {
        "name": "LLM Observability & Monitoring",
        "description": """Monitoring, debugging, and observability tools for LLM applications and AI agents.
        
        Key characteristics:
        - LLM monitoring and logging
        - Prompt tracking and versioning
        - Token usage and cost tracking
        - Performance monitoring for AI
        - Tracing and debugging for LLM chains
        - Agent observability and tracking
        - LLM analytics and insights
        - Error tracking for AI systems
        - Model drift detection
        - LLMOps platforms
        
        Examples: LangSmith, Weights & Biases, LLM monitoring tools, tracing platforms""",
        "keywords": [
            "LLM observability", "AI monitoring", "LLMOps", "prompt tracking",
            "tracing", "LLM logging", "model monitoring", "AI debugging",
            "token tracking", "performance monitoring", "agent monitoring",
            "LLM analytics", "observability platform", "AI tracing",
            "prompt management", "model tracking", "LLM insights"
        ]
    },
    
    CategoryType.CONTACT_CENTER: {
        "name": "Contact Center Solutions",
        "description": """AI-powered contact center, customer service, and support automation platforms.
        
        Key characteristics:
        - AI-powered contact center platforms
        - Conversational AI for customer service
        - Call center automation
        - Agent assist and copilot tools
        - Quality assurance and coaching
        - Sentiment analysis and analytics
        - Omnichannel support platforms
        - IVR and voice automation
        - Chatbots and virtual assistants
        - Workforce management for contact centers
        
        Examples: Contact center AI, customer service automation, agent assist, call analytics""",
        "keywords": [
            "contact center", "call center", "customer service", "customer support",
            "agent assist", "contact center AI", "call automation",
            "customer service automation", "chatbot", "virtual assistant",
            "IVR", "voice automation", "omnichannel", "agent copilot",
            "quality assurance", "call analytics", "sentiment analysis",
            "workforce management", "support automation"
        ]
    }
}


# ====================
# EVALUATION ENGINE
# ====================

class StartupEvaluator:
    """AI-powered startup evaluation engine"""
    
    def __init__(self, use_nvidia_nim: bool = True):
        self.use_nvidia_nim = use_nvidia_nim and is_nvidia_nim_configured()
        self.db = SessionLocal()
        self.checkpoint_file = Path("downloads/axa_evaluation_checkpoint.json")
        self.evaluated_ids = set()
        
        if not self.use_nvidia_nim:
            logger.warning("NVIDIA NIM not configured. Using fallback LLM.")
    
    def _load_checkpoint(self) -> Dict[str, Any]:
        """Load evaluation checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                data = json.load(f)
                self.evaluated_ids = set(data.get('evaluated_ids', []))
                logger.info(f"Loaded checkpoint: {len(self.evaluated_ids)} startups already evaluated")
                return data
        return {'evaluated_ids': [], 'results': []}
    
    def _save_checkpoint(self, results: List[Dict[str, Any]]):
        """Save evaluation checkpoint"""
        checkpoint_data = {
            'evaluated_ids': list(self.evaluated_ids),
            'results': results,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
    
    def _build_evaluation_prompt(
        self,
        startup: Startup,
        category_type: CategoryType
    ) -> str:
        """Build comprehensive evaluation prompt for a category"""
        
        category_info = CATEGORY_DEFINITIONS[category_type]
        
        # Gather all startup information
        startup_info = f"""
STARTUP INFORMATION:
====================
Name: {startup.company_name}
Industry: {startup.primary_industry or 'Not specified'}
Secondary Industries: {startup.secondary_industry or 'Not specified'}
Business Types: {startup.business_types or 'Not specified'}
Country: {startup.company_country or 'Not specified'}
City: {startup.company_city or 'Not specified'}

Description:
{startup.company_description or startup.shortDescription or 'No description available'}

Short Description: {startup.shortDescription or 'N/A'}

Website: {startup.website or 'Not provided'}
LinkedIn: {startup.company_linked_in or 'Not provided'}

Funding: ${startup.totalFunding or 0}M
Stage: {startup.currentInvestmentStage or 'Unknown'}
Employees: {startup.employees or 'Unknown'}
Founded: {startup.founding_year or 'Unknown'}

Focus Industries: {startup.focus_industries or 'Not specified'}
"""

        # Add enrichment data if available
        if startup.is_enriched and hasattr(startup, 'team_info'):
            startup_info += f"\nTeam Info: {startup.team_info}"
        if startup.is_enriched and hasattr(startup, 'tech_stack'):
            startup_info += f"\nTech Stack: {startup.tech_stack}"
        if startup.is_enriched and hasattr(startup, 'social_presence'):
            startup_info += f"\nSocial Presence: {startup.social_presence}"
        
        prompt = f"""You are an expert analyst evaluating startups for AXA, a major insurance company.

CATEGORY TO EVALUATE:
{category_info['name']}

CATEGORY DEFINITION:
{category_info['description']}

KEY INDICATORS (reference keywords):
{', '.join(category_info['keywords'])}

{startup_info}

EVALUATION TASK:
Thoroughly analyze this startup and determine if it matches the "{category_info['name']}" category.

Consider:
1. Does the startup's solution/product directly align with this category?
2. Could AXA leverage this startup as a provider/vendor?
3. What specific capabilities does it offer for this category?
4. Are there any red flags or concerns?
5. What would be the potential value for AXA?

Provide your evaluation in the following JSON format:
{{
    "matches": true/false,
    "confidence": <0-100 integer representing confidence level>,
    "reasoning": "<detailed explanation of why it matches or doesn't match>",
    "key_indicators": ["<list of 3-5 specific features/capabilities that indicate a match>"],
    "potential_use_cases": ["<list of 2-4 specific ways AXA could use this startup>"],
    "risk_factors": ["<list of any concerns, limitations, or risks>"]
}}

IMPORTANT:
- Be thorough but honest - if it doesn't match, say so clearly
- Consider both direct and indirect matches
- Think about integration possibilities with AXA's operations
- Consider the startup's maturity and readiness
- A startup can be relevant even if not a perfect keyword match

Provide ONLY the JSON response, no additional text.
"""
        return prompt
    
    def _evaluate_category_sync(
        self,
        startup: Startup,
        category_type: CategoryType
    ) -> CategoryMatch:
        """Evaluate a single category for a startup"""
        try:
            prompt = self._build_evaluation_prompt(startup, category_type)
            
            # Call LLM
            messages = [{"role": "user", "content": prompt}]
            
            response = llm_completion_sync(
                messages=messages,
                model=None,  # Use default NVIDIA NIM model
                temperature=0.3,  # Lower temp for more consistent evaluation
                max_tokens=1000,
                use_nvidia_nim=self.use_nvidia_nim,
                metadata={
                    "feature": "axa_evaluation",
                    "startup_id": startup.id,
                    "category": category_type.value
                }
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response (in case there's extra text)
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
            else:
                result = json.loads(content)
            
            return CategoryMatch(
                category=category_type.value,
                matches=result.get('matches', False),
                confidence=result.get('confidence', 0),
                reasoning=result.get('reasoning', ''),
                key_indicators=result.get('key_indicators', []),
                potential_use_cases=result.get('potential_use_cases', []),
                risk_factors=result.get('risk_factors', [])
            )
            
        except Exception as e:
            logger.error(f"Error evaluating {startup.company_name} for {category_type.value}: {e}")
            return CategoryMatch(
                category=category_type.value,
                matches=False,
                confidence=0,
                reasoning=f"Evaluation error: {str(e)}",
                key_indicators=[],
                potential_use_cases=[],
                risk_factors=["Evaluation failed"]
            )
    
    def evaluate_startup(
        self,
        startup: Startup,
        categories: Optional[List[CategoryType]] = None
    ) -> StartupEvaluation:
        """Evaluate a startup across all or specified categories"""
        
        if categories is None:
            categories = list(CategoryType)
        
        logger.info(f"Evaluating: {startup.company_name} ({len(categories)} categories)")
        
        # Evaluate each category
        category_matches = []
        for category_type in categories:
            match = self._evaluate_category_sync(startup, category_type)
            category_matches.append(match)
            
            if match.matches:
                logger.info(f"  ✓ Matched {category_type.value} (confidence: {match.confidence}%)")
        
        # Calculate overall score
        matched_categories = [m for m in category_matches if m.matches]
        if matched_categories:
            overall_score = sum(m.confidence for m in matched_categories) / len(matched_categories)
        else:
            overall_score = 0
        
        # Determine priority tier
        if overall_score >= 80 and len(matched_categories) >= 2:
            tier = "Tier 1: Critical Priority"
        elif overall_score >= 60 or len(matched_categories) >= 2:
            tier = "Tier 2: High Priority"
        elif overall_score >= 40 or len(matched_categories) >= 1:
            tier = "Tier 3: Medium Priority"
        else:
            tier = "Tier 4: Low Priority"
        
        # Generate recommended actions
        recommended_actions = self._generate_recommendations(matched_categories, startup)
        
        # Generate summary
        if matched_categories:
            matched_names = [CATEGORY_DEFINITIONS[CategoryType(m.category)]['name'] for m in matched_categories]
            summary = f"Matches {len(matched_categories)} categories: {', '.join(matched_names)}. "
            summary += f"Overall confidence: {overall_score:.0f}%. "
            top_match = max(matched_categories, key=lambda m: m.confidence)
            summary += f"Strongest fit: {CATEGORY_DEFINITIONS[CategoryType(top_match.category)]['name']}."
        else:
            summary = "No strong matches found across evaluated categories."
        
        evaluation = StartupEvaluation(
            startup_id=startup.id,
            startup_name=startup.company_name,
            evaluation_date=datetime.now().isoformat(),
            categories_matched=category_matches,
            overall_score=overall_score,
            priority_tier=tier,
            recommended_actions=recommended_actions,
            axa_fit_summary=summary
        )
        
        return evaluation
    
    def _generate_recommendations(
        self,
        matched_categories: List[CategoryMatch],
        startup: Startup
    ) -> List[str]:
        """Generate recommended actions based on matches"""
        
        recommendations = []
        
        if not matched_categories:
            return ["Continue monitoring for future relevance"]
        
        # High confidence matches
        high_conf = [m for m in matched_categories if m.confidence >= 70]
        if high_conf:
            recommendations.append(f"Schedule evaluation meeting - {len(high_conf)} high-confidence matches")
        
        # Multiple category matches
        if len(matched_categories) >= 3:
            recommendations.append("Strategic partnership potential - matches multiple AXA needs")
        
        # Specific category recommendations
        for match in matched_categories:
            if match.confidence >= 60:
                cat_name = CATEGORY_DEFINITIONS[CategoryType(match.category)]['name']
                recommendations.append(f"Explore {cat_name} integration options")
        
        # Funding/maturity check
        funding = float(startup.totalFunding or 0)
        if funding >= 10:
            recommendations.append("Well-funded startup - likely has mature product")
        elif funding < 1:
            recommendations.append("Early stage - assess product readiness before engagement")
        
        return recommendations
    
    def evaluate_all_startups(
        self,
        categories: Optional[List[CategoryType]] = None,
        resume: bool = False,
        batch_size: int = 3
    ) -> List[StartupEvaluation]:
        """Evaluate all startups in database"""
        
        # Load checkpoint if resuming
        checkpoint_data = {'results': []}
        if resume:
            checkpoint_data = self._load_checkpoint()
        
        results = checkpoint_data.get('results', [])
        
        # Get all startups
        all_startups = self.db.query(Startup).all()
        logger.info(f"Found {len(all_startups)} total startups in database")
        
        # Filter out already evaluated
        startups_to_evaluate = [s for s in all_startups if s.id not in self.evaluated_ids]
        logger.info(f"Evaluating {len(startups_to_evaluate)} startups (skipping {len(self.evaluated_ids)} already done)")
        
        # Process in batches
        for i in range(0, len(startups_to_evaluate), batch_size):
            batch = startups_to_evaluate[i:i+batch_size]
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Batch {i//batch_size + 1}/{(len(startups_to_evaluate)-1)//batch_size + 1}")
            logger.info(f"{'='*60}")
            
            for startup in batch:
                try:
                    evaluation = self.evaluate_startup(startup, categories)
                    results.append(asdict(evaluation))
                    self.evaluated_ids.add(startup.id)
                    
                    # Save checkpoint after each startup
                    self._save_checkpoint(results)
                    
                except Exception as e:
                    logger.error(f"Failed to evaluate {startup.company_name}: {e}")
                    continue
            
            logger.info(f"Progress: {len(self.evaluated_ids)}/{len(all_startups)} startups evaluated")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Evaluation Complete!")
        logger.info(f"{'='*60}")
        
        return results
    
    def close(self):
        """Close database connection"""
        self.db.close()


# ====================
# RESULTS ANALYSIS
# ====================

def analyze_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze evaluation results and generate insights"""
    
    analysis = {
        'total_startups': len(results),
        'category_matches': {},
        'tier_distribution': {},
        'top_opportunities': [],
        'multi_category_startups': []
    }
    
    # Count matches by category
    for cat_type in CategoryType:
        matches = []
        for result in results:
            for cat_match in result['categories_matched']:
                if cat_match['category'] == cat_type.value and cat_match['matches']:
                    matches.append({
                        'startup_name': result['startup_name'],
                        'confidence': cat_match['confidence'],
                        'reasoning': cat_match['reasoning']
                    })
        
        analysis['category_matches'][cat_type.value] = {
            'count': len(matches),
            'startups': sorted(matches, key=lambda x: x['confidence'], reverse=True)[:10]
        }
    
    # Tier distribution
    for result in results:
        tier = result['priority_tier']
        analysis['tier_distribution'][tier] = analysis['tier_distribution'].get(tier, 0) + 1
    
    # Top opportunities (multiple categories)
    multi_cat = []
    for result in results:
        matched = [c for c in result['categories_matched'] if c['matches']]
        if len(matched) >= 2:
            multi_cat.append({
                'startup_name': result['startup_name'],
                'categories_count': len(matched),
                'categories': [c['category'] for c in matched],
                'overall_score': result['overall_score']
            })
    
    analysis['multi_category_startups'] = sorted(
        multi_cat,
        key=lambda x: (x['categories_count'], x['overall_score']),
        reverse=True
    )[:20]
    
    # Top opportunities overall
    top_opps = sorted(
        [r for r in results if r['overall_score'] > 0],
        key=lambda x: x['overall_score'],
        reverse=True
    )[:30]
    
    analysis['top_opportunities'] = [
        {
            'startup_name': r['startup_name'],
            'overall_score': r['overall_score'],
            'tier': r['priority_tier'],
            'summary': r['axa_fit_summary']
        }
        for r in top_opps
    ]
    
    return analysis


def print_summary(analysis: Dict[str, Any]):
    """Print evaluation summary"""
    
    print("\n" + "="*80)
    print("AXA COMPREHENSIVE STARTUP EVALUATION - RESULTS SUMMARY")
    print("="*80)
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Total startups evaluated: {analysis['total_startups']}")
    print(f"\n  Tier Distribution:")
    for tier, count in sorted(analysis['tier_distribution'].items()):
        print(f"    {tier}: {count}")
    
    print(f"\n📈 Category Matches:")
    for cat_value, data in analysis['category_matches'].items():
        cat_name = CATEGORY_DEFINITIONS[CategoryType(cat_value)]['name']
        print(f"\n  {cat_name}: {data['count']} matches")
        if data['startups']:
            print(f"    Top startups:")
            for s in data['startups'][:5]:
                print(f"      • {s['startup_name']} (confidence: {s['confidence']}%)")
    
    print(f"\n🎯 Multi-Category Startups (Strategic Opportunities):")
    for i, startup in enumerate(analysis['multi_category_startups'][:10], 1):
        cats = ', '.join([CATEGORY_DEFINITIONS[CategoryType(c)]['name'] for c in startup['categories']])
        print(f"  {i}. {startup['startup_name']}")
        print(f"     Categories: {cats}")
        print(f"     Score: {startup['overall_score']:.0f}%")
    
    print(f"\n🏆 Top 15 Overall Opportunities:")
    for i, opp in enumerate(analysis['top_opportunities'][:15], 1):
        print(f"  {i}. {opp['startup_name']} (Score: {opp['overall_score']:.0f}%, {opp['tier']})")
        print(f"     {opp['summary']}")


# ====================
# MAIN EXECUTION
# ====================

def main():
    parser = argparse.ArgumentParser(
        description='AXA Comprehensive Startup Evaluator with NVIDIA NIM'
    )
    parser.add_argument(
        '--categories',
        type=str,
        help='Comma-separated list of categories to evaluate (default: all)'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from checkpoint'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=3,
        help='Number of startups to process in each batch (default: 3)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='downloads/axa_comprehensive_evaluation.json',
        help='Output file path'
    )
    parser.add_argument(
        '--no-nvidia',
        action='store_true',
        help='Disable NVIDIA NIM (use fallback LLM)'
    )
    
    args = parser.parse_args()
    
    # Parse categories
    categories = None
    if args.categories:
        cat_names = [c.strip().upper() for c in args.categories.split(',')]
        categories = []
        for name in cat_names:
            # Try to match category
            for cat_type in CategoryType:
                if name in cat_type.value.upper() or name in cat_type.name:
                    categories.append(cat_type)
                    break
        
        if not categories:
            logger.error(f"No valid categories found in: {args.categories}")
            logger.info(f"Available categories: {', '.join([c.value for c in CategoryType])}")
            return
        
        logger.info(f"Evaluating categories: {', '.join([c.value for c in categories])}")
    
    # Create evaluator
    evaluator = StartupEvaluator(use_nvidia_nim=not args.no_nvidia)
    
    try:
        # Run evaluation
        logger.info("\n🚀 Starting comprehensive evaluation...")
        results = evaluator.evaluate_all_startups(
            categories=categories,
            resume=args.resume,
            batch_size=args.batch_size
        )
        
        # Save results
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✅ Results saved to: {output_path}")
        
        # Generate and print analysis
        analysis = analyze_results(results)
        print_summary(analysis)
        
        # Save analysis
        analysis_path = output_path.parent / f"{output_path.stem}_analysis.json"
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"\n✅ Analysis saved to: {analysis_path}")
        
    finally:
        evaluator.close()


if __name__ == '__main__':
    main()
