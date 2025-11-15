#!/usr/bin/env python3
"""
AXA Agentic AI Startup Filter - NVIDIA NIM Enhanced
====================================================

Identifies startups building autonomous agents, agentic workflows, and AI automation
that could provide enterprise solutions to AXA.

Focus Areas:
- Agentic AI platforms (autonomous decision-making agents)
- AI workflow orchestration and automation
- Multi-agent systems and swarms
- Autonomous process execution
- AI-powered RPA (Robotic Process Automation)
- Cognitive automation platforms
- Agent-based insurance/claims processing
- Autonomous customer service agents
- AI copilots and assistants for enterprises

Author: AXA Digital Team
Date: 2025-11-15
"""

import json
import logging
import argparse
import os
import sys
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
from collections import Counter, defaultdict
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Set LiteLLM logging
os.environ['LITELLM_LOG'] = 'INFO'

# NVIDIA NIM Configuration
NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY', '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')
NVIDIA_BASE_URL = 'https://integrate.api.nvidia.com/v1'

# Try to import LiteLLM for NVIDIA NIM
try:
    from litellm import completion
    LITELLM_AVAILABLE = True
    logger.info("✓ LiteLLM loaded - NVIDIA NIM enabled")
except ImportError:
    LITELLM_AVAILABLE = False
    logger.warning("⚠ LiteLLM not available - LLM features disabled")


# ============================================================================
# AGENTIC AI DETECTION PATTERNS
# ============================================================================

AGENTIC_AI_KEYWORDS = {
    # Core agentic concepts
    'agentic_core': [
        'agentic ai', 'agentic platform', 'agentic system', 'agentic workflow',
        'autonomous agent', 'autonomous ai', 'ai agent', 'intelligent agent',
        'multi-agent', 'multi agent', 'agent swarm', 'agent orchestration',
        'agentic reasoning', 'agentic automation', 'agentic decision'
    ],
    
    # Workflow automation
    'workflow_automation': [
        'workflow automation', 'workflow orchestration', 'process automation',
        'autonomous workflow', 'intelligent workflow', 'ai workflow',
        'workflow agent', 'automated decision', 'autonomous decision-making',
        'self-executing', 'autonomous execution', 'ai orchestration'
    ],
    
    # AI copilots and assistants
    'ai_copilot': [
        'ai copilot', 'ai assistant', 'autonomous assistant', 'intelligent assistant',
        'ai-powered assistant', 'virtual agent', 'digital agent', 'cognitive assistant',
        'enterprise copilot', 'business copilot', 'ai teammate'
    ],
    
    # RPA and cognitive automation
    'rpa_cognitive': [
        'robotic process automation', 'rpa', 'cognitive automation',
        'intelligent automation', 'hyperautomation', 'autonomous rpa',
        'ai-powered rpa', 'intelligent rpa', 'agentic rpa'
    ],
    
    # Enterprise AI systems
    'enterprise_ai': [
        'enterprise ai platform', 'ai infrastructure', 'ai operations',
        'aiops', 'mlops agent', 'autonomous operations', 'intelligent operations',
        'self-healing', 'self-optimizing', 'autonomous monitoring'
    ],
    
    # Insurance/claims specific
    'insurance_agents': [
        'claims automation', 'autonomous claims', 'ai claims processing',
        'automated underwriting', 'intelligent underwriting', 'risk agent',
        'fraud detection agent', 'autonomous fraud', 'claims agent'
    ],
    
    # Customer service agents
    'customer_service': [
        'autonomous customer service', 'ai customer agent', 'intelligent customer support',
        'automated customer service', 'conversational ai', 'dialogue agent',
        'customer service automation', 'support automation'
    ],
    
    # Technical capabilities
    'technical_capabilities': [
        'llm agent', 'foundation model agent', 'generative ai agent',
        'reasoning engine', 'decision engine', 'inference engine',
        'autonomous reasoning', 'chain of thought', 'tool calling',
        'function calling', 'agent framework', 'langchain', 'autogen',
        'crew ai', 'task delegation', 'agent collaboration'
    ]
}

# B2B/Enterprise indicators
ENTERPRISE_INDICATORS = [
    'b2b', 'enterprise', 'saas', 'platform', 'api',
    'integration', 'infrastructure', 'business', 'corporate',
    'workplace', 'productivity', 'operations', 'developers'
]

# Strong exclusions (consumer-only)
CONSUMER_EXCLUSIONS = [
    'b2c only', 'consumer app', 'mobile game', 'dating app',
    'food delivery', 'social media', 'influencer', 'entertainment only',
    'retail consumer', 'shopping app', 'fashion marketplace'
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_search_text(startup: Dict) -> str:
    """Extract all searchable text from startup"""
    fields = [
        'company_name', 'company_description', 'shortDescription',
        'primary_industry', 'secondary_industry', 'business_types',
        'curated_collections_tags', 'topics', 'tech'
    ]
    
    text_parts = []
    for field in fields:
        value = startup.get(field)
        if value:
            if isinstance(value, list):
                text_parts.extend([str(v) for v in value])
            else:
                text_parts.append(str(value))
    
    return ' '.join(text_parts).lower()


def parse_funding(startup: Dict) -> Tuple[float, str]:
    """Parse funding amount in millions USD"""
    funding = startup.get('totalFunding', 0) or startup.get('originalTotalFunding', 0)
    
    try:
        if isinstance(funding, (int, float)):
            return float(funding) / 1_000_000, 'Disclosed'
        elif isinstance(funding, str):
            funding = funding.replace(',', '').replace(' ', '')
            if 'M' in funding.upper():
                return float(re.sub(r'[^\d.]', '', funding)), 'Disclosed'
            elif 'K' in funding.upper():
                return float(re.sub(r'[^\d.]', '', funding)) / 1000, 'Disclosed'
            else:
                return float(re.sub(r'[^\d.]', '', funding)) / 1_000_000, 'Disclosed'
    except:
        pass
    
    return 0, 'Undisclosed'


def parse_employees(startup: Dict) -> Tuple[int, str]:
    """Parse employee count"""
    employees = startup.get('employees', 0)
    
    try:
        if isinstance(employees, (int, float)):
            count = int(employees)
        elif isinstance(employees, str):
            # Handle ranges like "50-100"
            if '-' in employees:
                parts = employees.split('-')
                count = int(parts[1])  # Use upper bound
            else:
                count = int(re.sub(r'[^\d]', '', employees))
        else:
            count = 0
    except:
        count = 0
    
    if count == 0:
        return 0, 'Unknown'
    elif count < 10:
        return count, 'Micro (<10)'
    elif count < 50:
        return count, 'Small (10-49)'
    elif count < 200:
        return count, 'Medium (50-199)'
    else:
        return count, 'Large (200+)'


def parse_founding_year(startup: Dict) -> int:
    """Parse founding year"""
    year = startup.get('founding_year') or startup.get('dateFounded')
    
    try:
        if isinstance(year, int):
            return year
        elif isinstance(year, str):
            match = re.search(r'(\d{4})', year)
            if match:
                return int(match.group(1))
    except:
        pass
    
    return 0


# ============================================================================
# AGENTIC AI SCORING
# ============================================================================

def detect_agentic_signals(startup: Dict) -> Dict:
    """Detect agentic AI signals with categorization"""
    search_text = get_search_text(startup)
    
    detected_categories = defaultdict(list)
    total_matches = 0
    
    for category, keywords in AGENTIC_AI_KEYWORDS.items():
        for keyword in keywords:
            if keyword in search_text:
                detected_categories[category].append(keyword)
                total_matches += 1
    
    # Calculate category scores
    category_scores = {}
    for category, matches in detected_categories.items():
        # Weight different categories
        weights = {
            'agentic_core': 10,
            'workflow_automation': 8,
            'ai_copilot': 7,
            'rpa_cognitive': 7,
            'enterprise_ai': 6,
            'insurance_agents': 9,
            'customer_service': 6,
            'technical_capabilities': 5
        }
        
        weight = weights.get(category, 5)
        category_scores[category] = len(matches) * weight
    
    return {
        'categories': dict(detected_categories),
        'category_scores': category_scores,
        'total_matches': total_matches,
        'total_score': sum(category_scores.values())
    }


def is_enterprise_focused(startup: Dict) -> Tuple[bool, int]:
    """Check if startup is B2B/enterprise focused"""
    search_text = get_search_text(startup)
    
    enterprise_count = sum(1 for ind in ENTERPRISE_INDICATORS if ind in search_text)
    consumer_count = sum(1 for exc in CONSUMER_EXCLUSIONS if exc in search_text)
    
    # Strong enterprise signals
    if enterprise_count >= 3:
        return True, 100
    
    # Some enterprise signals, no consumer signals
    if enterprise_count >= 1 and consumer_count == 0:
        return True, 70
    
    # Mixed signals
    if enterprise_count > consumer_count:
        return True, 50
    
    # Unclear or consumer-focused
    return False, 0


def calculate_agentic_score(startup: Dict, use_llm: bool = False) -> Dict:
    """
    Calculate comprehensive agentic AI score
    
    Scoring:
    - Agentic signals: 0-40 points
    - Enterprise focus: 0-20 points
    - Funding: 0-20 points
    - Company size: 0-10 points
    - Maturity: 0-10 points
    - LLM validation: +/-10 points
    
    Total: 0-110 points (normalized to 0-100)
    """
    
    # Detect agentic signals
    agentic_detection = detect_agentic_signals(startup)
    agentic_score = min(40, int(agentic_detection['total_score'] / 2))
    
    # If no agentic signals, exclude
    if agentic_detection['total_matches'] == 0:
        return {
            'total_score': 0,
            'tier': 'Not Agentic',
            'agentic_categories': [],
            'matched_keywords': {},
            'exclusion_reason': 'No agentic AI signals detected'
        }
    
    # Enterprise focus
    is_enterprise, enterprise_confidence = is_enterprise_focused(startup)
    enterprise_score = int(20 * enterprise_confidence / 100)
    
    # Funding score
    funding_amount, _ = parse_funding(startup)
    if funding_amount >= 100:
        funding_score = 20
    elif funding_amount >= 50:
        funding_score = 15
    elif funding_amount >= 10:
        funding_score = 10
    elif funding_amount >= 1:
        funding_score = 5
    else:
        funding_score = 0
    
    # Size score
    employee_count, _ = parse_employees(startup)
    if employee_count >= 200:
        size_score = 10
    elif employee_count >= 50:
        size_score = 7
    elif employee_count >= 10:
        size_score = 4
    else:
        size_score = 0
    
    # Maturity score
    founding_year = parse_founding_year(startup)
    current_year = datetime.now().year
    age = current_year - founding_year if founding_year > 0 else 0
    
    if age >= 5:
        maturity_score = 10
    elif age >= 3:
        maturity_score = 7
    elif age >= 1:
        maturity_score = 4
    else:
        maturity_score = 0
    
    # LLM validation (optional)
    llm_adjustment = 0
    llm_reasoning = None
    
    if use_llm and LITELLM_AVAILABLE and agentic_score >= 15:
        llm_viable, llm_reasoning = validate_with_llm(startup)
        llm_adjustment = 10 if llm_viable else -10
    
    # Calculate total
    raw_score = agentic_score + enterprise_score + funding_score + size_score + maturity_score + llm_adjustment
    normalized_score = min(100, max(0, int(raw_score * 100 / 110)))
    
    # Determine tier
    if normalized_score >= 75:
        tier = 'Tier 1: Top Agentic'
    elif normalized_score >= 60:
        tier = 'Tier 2: Strong Agentic'
    elif normalized_score >= 45:
        tier = 'Tier 3: Emerging Agentic'
    elif normalized_score >= 30:
        tier = 'Tier 4: Early Agentic'
    else:
        tier = 'Low Priority'
    
    return {
        'total_score': normalized_score,
        'tier': tier,
        'agentic_categories': list(agentic_detection['categories'].keys()),
        'matched_keywords': agentic_detection['categories'],
        'category_scores': agentic_detection['category_scores'],
        'breakdown': {
            'agentic_signals': agentic_score,
            'enterprise_focus': enterprise_score,
            'funding': funding_score,
            'size': size_score,
            'maturity': maturity_score,
            'llm_adjustment': llm_adjustment,
            'raw_total': raw_score
        },
        'metadata': {
            'funding_millions': funding_amount,
            'employee_count': employee_count,
            'founding_year': founding_year,
            'is_enterprise': is_enterprise,
            'llm_reasoning': llm_reasoning
        }
    }


def validate_with_llm(startup: Dict) -> Tuple[bool, str]:
    """Use NVIDIA NIM to validate agentic AI viability"""
    
    if not LITELLM_AVAILABLE:
        return True, "LLM not available"
    
    company_name = startup.get('company_name', 'Unknown')
    description = startup.get('company_description') or startup.get('shortDescription', 'No description')
    industry = startup.get('primary_industry', 'Unknown')
    business_model = startup.get('business_types', 'Unknown')
    
    prompt = f"""You are an expert in agentic AI and enterprise automation solutions.

STARTUP TO EVALUATE:
Company: {company_name}
Industry: {industry}
Business Model: {business_model}
Description: {description[:500]}

EVALUATION CRITERIA - Is this a TRUE agentic AI/autonomous agent company?

✅ AGENTIC if:
• Builds autonomous agents that make decisions without human intervention
• Develops multi-agent systems or agent orchestration platforms
• Creates AI workflows that self-execute and self-optimize
• Provides agentic RPA, cognitive automation, or intelligent process automation
• Builds AI copilots/assistants that take autonomous actions
• Develops reasoning engines, decision engines for autonomous operations
• Has agent-based insurance, claims, or financial automation
• Enterprise-focused with B2B offerings

❌ NOT AGENTIC if:
• Just traditional ML/AI without autonomous agents
• Simple chatbots or Q&A systems (not autonomous)
• Pure analytics/BI tools without automation
• Consumer-only apps
• No clear autonomous decision-making capability

PROVIDE:
DECISION: AGENTIC or NOT_AGENTIC
CONFIDENCE: 0-100
REASON: One sentence why

Format:
DECISION: [AGENTIC or NOT_AGENTIC]
CONFIDENCE: [number]
REASON: [explanation]"""
    
    try:
        response = completion(
            model='openai/deepseek-ai/deepseek-r1',
            messages=[{'role': 'user', 'content': prompt}],
            api_base=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY,
            temperature=0.3,
            max_tokens=300
        )
        
        content = response.choices[0].message.get('reasoning_content') or response.choices[0].message.get('content', '')
        
        if not content:
            logger.warning(f"Empty LLM response for {company_name}")
            return True, "LLM empty response - defaulting to viable"
        
        # Parse response
        decision = 'AGENTIC' in content.upper() and 'NOT_AGENTIC' not in content.upper()
        
        # Extract confidence
        confidence = 70
        for line in content.split('\n'):
            if 'CONFIDENCE:' in line.upper():
                try:
                    confidence = int(''.join(filter(str.isdigit, line.split(':', 1)[1])))
                except:
                    pass
        
        # Extract reason
        reason = "LLM validation"
        for line in content.split('\n'):
            if 'REASON:' in line.upper():
                reason = line.split(':', 1)[1].strip()
                break
        
        return decision and confidence >= 60, reason
        
    except Exception as e:
        logger.warning(f"LLM validation failed for {company_name}: {e}")
        return True, f"LLM error - defaulting to viable"


# ============================================================================
# MAIN FILTERING
# ============================================================================

def filter_agentic_startups(startups: List[Dict], min_score: int = 30, 
                           use_llm: bool = False) -> Tuple[List[Dict], Dict]:
    """Filter startups for agentic AI capabilities"""
    
    logger.info(f"Starting agentic AI filtering on {len(startups)} startups...")
    logger.info(f"Minimum score: {min_score}")
    logger.info(f"LLM validation: {'Enabled' if use_llm else 'Disabled'}")
    
    filtered = []
    stats = {
        'total': len(startups),
        'agentic_signals': 0,
        'passed_filter': 0,
        'excluded_no_signals': 0,
        'excluded_low_score': 0,
        'tier_distribution': Counter(),
        'category_distribution': Counter()
    }
    
    for i, startup in enumerate(startups):
        if i > 0 and i % 500 == 0:
            logger.info(f"  Processed {i}/{len(startups)} startups ({filtered.__len__()} matches so far)")
        
        # Calculate score
        scoring = calculate_agentic_score(startup, use_llm=use_llm)
        
        # Track stats
        if scoring['tier'] == 'Not Agentic':
            stats['excluded_no_signals'] += 1
            continue
        
        stats['agentic_signals'] += 1
        
        if scoring['total_score'] < min_score:
            stats['excluded_low_score'] += 1
            continue
        
        # Passed filter
        stats['passed_filter'] += 1
        stats['tier_distribution'][scoring['tier']] += 1
        
        for category in scoring['agentic_categories']:
            stats['category_distribution'][category] += 1
        
        # Add to results
        startup['agentic_scoring'] = scoring
        filtered.append(startup)
    
    # Sort by score
    filtered.sort(key=lambda x: x['agentic_scoring']['total_score'], reverse=True)
    
    logger.info(f"✓ Filtered to {len(filtered)} agentic AI startups")
    
    return filtered, stats


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Filter agentic AI startups for AXA')
    parser.add_argument('--input', required=True, help='Input JSON file')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--min-score', type=int, default=30, help='Minimum score (default: 30)')
    parser.add_argument('--use-llm', action='store_true', help='Enable NVIDIA NIM validation')
    parser.add_argument('--stats', action='store_true', help='Show detailed statistics')
    
    args = parser.parse_args()
    
    # Load data
    logger.info(f"Loading startups from {args.input}...")
    with open(args.input, 'r') as f:
        startups = json.load(f)
    
    logger.info(f"Loaded {len(startups)} startups")
    
    # Filter
    filtered, stats = filter_agentic_startups(startups, args.min_score, args.use_llm)
    
    # Save
    logger.info(f"Saving {len(filtered)} startups to {args.output}...")
    with open(args.output, 'w') as f:
        json.dump(filtered, f, indent=2)
    
    # Show stats
    if args.stats:
        print("\n" + "="*80)
        print("AGENTIC AI STARTUP FILTERING RESULTS")
        print("="*80)
        print(f"\n📊 OVERVIEW:")
        print(f"  Total startups: {stats['total']}")
        print(f"  With agentic signals: {stats['agentic_signals']} ({stats['agentic_signals']/stats['total']*100:.1f}%)")
        print(f"  Passed filter: {stats['passed_filter']} ({stats['passed_filter']/stats['total']*100:.1f}%)")
        print(f"  Excluded (no signals): {stats['excluded_no_signals']}")
        print(f"  Excluded (low score): {stats['excluded_low_score']}")
        
        print(f"\n🎯 TIER DISTRIBUTION:")
        for tier, count in stats['tier_distribution'].most_common():
            print(f"  {tier}: {count}")
        
        print(f"\n🤖 CATEGORY DISTRIBUTION:")
        for category, count in stats['category_distribution'].most_common():
            print(f"  {category}: {count}")
        
        print(f"\n🏆 TOP 15 AGENTIC STARTUPS:")
        for i, s in enumerate(filtered[:15], 1):
            score = s['agentic_scoring']['total_score']
            tier = s['agentic_scoring']['tier']
            categories = ', '.join(s['agentic_scoring']['agentic_categories'][:3])
            funding = s['agentic_scoring']['metadata']['funding_millions']
            employees = s['agentic_scoring']['metadata']['employee_count']
            
            funding_str = f"${funding:.0f}M" if funding > 0 else "Undisclosed"
            size_str = f"{employees} emp" if employees > 0 else "Size unknown"
            
            print(f"  {i}. {s.get('company_name', 'Unknown')}")
            print(f"     Score: {score}/100 | {funding_str} | {size_str}")
            print(f"     Categories: {categories}")
        
        print("="*80 + "\n")


if __name__ == '__main__':
    main()
