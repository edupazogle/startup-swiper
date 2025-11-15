#!/usr/bin/env python3
"""
AXA Startup Filter - Enhanced with MCP and NVIDIA NIM

This enhanced version uses:
1. MCP (Model Context Protocol) for intelligent startup querying
2. NVIDIA NIM for AI-powered startup analysis
3. Advanced scoring prioritizing funding and company size
4. LLM-based relevance assessment for higher quality filtering

The script evaluates 5 AXA strategic rules with LLM assistance and
prioritizes startups with substantial funding and larger teams.

Usage:
    # Standard filtering with MCP/NIM
    python3 api/filter_axa_startups_enhanced.py --output downloads/axa_enhanced.json --stats
    
    # High priority only (score >= 70)
    python3 api/filter_axa_startups_enhanced.py --min-score 70 --output downloads/axa_tier1.json
    
    # With detailed LLM analysis
    python3 api/filter_axa_startups_enhanced.py --include-llm-analysis --output downloads/axa_analyzed.json
    
    # Force local filtering (no NIM)
    python3 api/filter_axa_startups_enhanced.py --local-only --output downloads/axa_local.json
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import re
import logging
import asyncio
import concurrent.futures
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Try to import MCP and LLM tools
try:
    from api.mcp_client import StartupDatabaseMCPTools
    HAS_MCP = True
except ImportError:
    try:
        from mcp_client import StartupDatabaseMCPTools
        HAS_MCP = True
    except ImportError:
        HAS_MCP = False
        logger.warning("MCP client not available - will use local filtering only")

try:
    from api.llm_config import llm_completion_sync, is_nvidia_nim_configured, get_nvidia_nim_model
    HAS_LLM = True
except ImportError:
    try:
        from llm_config import llm_completion_sync, is_nvidia_nim_configured, get_nvidia_nim_model
        HAS_LLM = True
    except ImportError:
        HAS_LLM = False
        logger.warning("LLM config not available - will use local analysis only")

# Global MCP tools instance
MCP_TOOLS = None


# ============================================================================
# KEYWORD DEFINITIONS (Same as original, enhanced)
# ============================================================================

RULE_1_KEYWORDS = {
    'primary': [
        'observability', 'monitoring', 'tracing', 'agent orchestration',
        'llm ops', 'mlops', 'ai ops', 'agent framework', 'multi-agent',
        'vector database', 'embedding', 'rag', 'workflow automation',
        'agent builder', 'model deployment', 'ai platform', 'agent testing',
        'agentic', 'autonomous agent', 'agent swarm', 'agent mesh'
    ],
    'secondary': [
        'langchain', 'llm', 'agent', 'orchestration', 'infrastructure',
        'platform', 'framework', 'sdk', 'api management', 'agent mesh',
        'llm monitoring', 'ai infrastructure', 'model ops', 'ai governance'
    ]
}

RULE_2_KEYWORDS = {
    'primary': [
        'marketing automation', 'sales ai', 'customer support automation',
        'recruiting ai', 'hr automation', 'finance automation',
        'contract intelligence', 'data analytics ai', 'conversational ai',
        'customer service ai', 'sales enablement', 'lead generation',
        'business process automation', 'intelligent workflow'
    ],
    'secondary': [
        'automation', 'ai agent', 'intelligent assistant', 'chatbot',
        'virtual assistant', 'rpa', 'process automation', 'workflow',
        'business intelligence', 'analytics', 'crm', 'erp'
    ]
}

RULE_3_KEYWORDS = {
    'primary': [
        'insurance', 'insurtech', 'claims', 'underwriting', 'policy',
        'actuarial', 'reinsurance', 'fraud detection insurance',
        'insurance platform', 'claims automation', 'underwriting automation',
        'insurance ai', 'risk assessment insurance', 'claims management'
    ],
    'secondary': [
        'claim', 'policyholder', 'premium', 'coverage', 'fnol',
        'loss adjusting', 'insurance distribution', 'insurance compliance',
        'insurance regulatory', 'carrier', 'insurance provider'
    ]
}

RULE_4_KEYWORDS = {
    'primary': [
        'health analytics', 'medical ai', 'telemedicine', 'digital health',
        'healthtech', 'wellness platform', 'remote monitoring',
        'healthcare data', 'preventive health', 'population health',
        'mental health platform', 'chronic disease', 'digital therapeutics',
        'health insurance', 'employee wellness'
    ],
    'secondary': [
        'health', 'healthcare', 'medical', 'wellness', 'wearable',
        'telehealth', 'patient', 'clinical', 'diagnosis', 'treatment',
        'payer', 'hospital', 'care management', 'biotech'
    ]
}

RULE_5_KEYWORDS = {
    'primary': [
        'code generation', 'ai coding', 'test automation', 'qa automation',
        'legacy modernization', 'cobol migration', 'mainframe modernization',
        'code migration', 'legacy integration', 'devops automation',
        'ci/cd', 'code intelligence', 'automated testing', 'ai developer'
    ],
    'secondary': [
        'developer', 'software development', 'programming', 'code',
        'testing', 'quality assurance', 'legacy', 'migration',
        'integration', 'api', 'microservices', 'cloud migration',
        'technical debt', 'refactoring', 'copilot', 'code assistant'
    ]
}

EXCLUSION_KEYWORDS = [
    'b2c', 'consumer app', 'gaming', 'game', 'entertainment',
    'food delivery', 'restaurant', 'e-commerce platform',
    'online marketplace', 'social network', 'dating',
    'cryptocurrency', 'nft', 'blockchain gaming'
]

# AXA Provider Exclusion Criteria - Startups that cannot be used as providers
AXA_PROVIDER_EXCLUSIONS = {
    'business_model': [
        'b2c', 'consumer', 'retail', 'marketplace', 'marketplace platform',
        'social network', 'social media', 'community', 'creator economy',
        'peer-to-peer', 'p2p'
    ],
    'industries_excluded': [
        'gaming', 'entertainment', 'food', 'restaurant', 'hospitality',
        'dating', 'real estate', 'property', 'luxury', 'fashion',
        'beauty', 'cosmetics', 'wellness', 'supplement'
    ],
    'geographic_focus': [
        'asia only', 'china only', 'india only', 'southeast asia only'
    ],
    'keywords_excluded': [
        'early stage only', 'seed only', 'pre-revenue', 'no revenue',
        'not profitable', 'burn rate', 'vc-dependent', 'solely venture'
    ]
}


# ============================================================================
# FUNDING & SIZE SCORING (NEW - Enhanced)
# ============================================================================

def parse_funding_amount(startup: Dict) -> Tuple[float, str]:
    """
    Extract and parse funding amount from startup data
    
    Returns:
        (amount_in_millions, funding_stage)
    """
    # Try different funding fields
    funding = None
    funding_str = str(startup.get('totalFunding', '') or 
                     startup.get('funding', '') or 
                     startup.get('lastFunding', '') or '')
    
    if not funding_str or funding_str.lower() in ['undisclosed', 'n/a', '', 'none']:
        return 0.0, 'Undisclosed'
    
    # Parse funding amount
    try:
        # Remove common currency symbols and text
        funding_str = re.sub(r'[$€£]|M|m|USD|EUR|GBP', '', funding_str).strip()
        funding = float(funding_str)
    except (ValueError, AttributeError):
        return 0.0, 'Undisclosed'
    
    # Determine stage based on funding
    if funding >= 500:
        stage = 'Late Stage'
    elif funding >= 100:
        stage = 'Growth'
    elif funding >= 10:
        stage = 'Series A/B'
    elif funding >= 1:
        stage = 'Seed/Pre-Seed'
    else:
        stage = 'Minimal'
    
    return funding, stage


def parse_employee_count(startup: Dict) -> Tuple[int, str]:
    """
    Extract and parse employee count from startup data
    
    Returns:
        (approximate_employee_count, size_category)
    """
    employees_str = str(startup.get('employees', '') or '').strip()
    
    if not employees_str or employees_str.lower() in ['undisclosed', 'n/a', '', 'none']:
        return 0, 'Unknown'
    
    # Parse employee ranges
    if '1-10' in employees_str:
        return 5, 'Micro (1-10)'
    elif '11-50' in employees_str:
        return 30, 'Small (11-50)'
    elif '51-200' in employees_str:
        return 125, 'Medium (51-200)'
    elif '201-500' in employees_str:
        return 350, 'Large (201-500)'
    elif '501-1000' in employees_str:
        return 750, 'Enterprise (501-1000)'
    elif '1000+' in employees_str or '1001' in employees_str:
        return 1500, 'Enterprise (1000+)'
    
    # Try to parse as number
    try:
        num = int(re.search(r'\d+', employees_str).group())
        if num >= 1000:
            return num, 'Enterprise (1000+)'
        elif num >= 500:
            return num, 'Large (500+)'
        elif num >= 200:
            return num, 'Medium (200+)'
        elif num >= 50:
            return num, 'Small (50+)'
        else:
            return num, f'Micro ({num})'
    except:
        return 0, 'Unknown'


def calculate_funding_score(startup: Dict) -> int:
    """
    Calculate funding score (0-40 points)
    
    Higher funding = higher priority for AXA
    """
    funding_amount, funding_stage = parse_funding_amount(startup)
    
    if funding_amount >= 500:
        return 40
    elif funding_amount >= 100:
        return 35
    elif funding_amount >= 50:
        return 30
    elif funding_amount >= 20:
        return 25
    elif funding_amount >= 10:
        return 20
    elif funding_amount >= 5:
        return 15
    elif funding_amount >= 1:
        return 10
    elif funding_amount > 0:
        return 5
    else:
        return 0


def calculate_size_score(startup: Dict) -> int:
    """
    Calculate company size score (0-30 points)
    
    Larger, more established companies score higher
    """
    employee_count, size_category = parse_employee_count(startup)
    
    if employee_count >= 1000:
        return 30
    elif employee_count >= 500:
        return 28
    elif employee_count >= 200:
        return 26
    elif employee_count >= 100:
        return 24
    elif employee_count >= 50:
        return 22
    elif employee_count >= 30:
        return 20
    elif employee_count >= 10:
        return 12
    elif employee_count > 0:
        return 5
    else:
        return 0


def calculate_maturity_score(startup: Dict) -> int:
    """
    Calculate maturity/stage score (0-10 points)
    
    Based on company type and maturity indicator
    """
    maturity = str(startup.get('maturity', '')).lower()
    company_type = str(startup.get('company_type', '')).lower()
    
    # Scaleup is most mature
    if 'scaleup' in maturity or 'scaleup' in company_type:
        return 10
    elif 'startup' in maturity or 'startup' in company_type:
        return 7
    elif 'validating' in maturity or 'deploying' in maturity:
        return 5
    elif 'emerging' in maturity:
        return 3
    else:
        return 2


def text_search(text: str, keywords: List[str]) -> int:
    """Search for keywords in text, return count of matches"""
    if not text:
        return 0
    text_lower = text.lower()
    count = sum(1 for keyword in keywords if keyword.lower() in text_lower)
    return count


def get_search_text(startup: Dict) -> str:
    """Extract searchable text from startup"""
    return f"{startup.get('company_description', '')} {startup.get('shortDescription', '')} {' '.join(startup.get('topics', []) or [])}"


# ============================================================================
# MCP ENRICHMENT (Enhanced with database queries)
# ============================================================================

async def enrich_startup_with_mcp(startup: Dict, use_mcp: bool = False) -> Dict:
    """
    Enrich startup data using MCP server
    
    Attempts to:
    - Get verified funding amounts
    - Retrieve current employee counts
    - Access company enrichment data
    - Fetch growth metrics
    """
    
    if not use_mcp or not HAS_MCP or MCP_TOOLS is None:
        return startup
    
    try:
        company_name = startup.get('company_name', '')
        if not company_name:
            return startup
        
        # Query MCP for enriched data
        enrichment_data = await MCP_TOOLS._get_enrichment_data(company_name)
        
        if enrichment_data:
            startup['mcp_enriched'] = enrichment_data
            
            # Update funding if we found better data
            if enrichment_data.get('total_funding'):
                try:
                    verified_funding = float(enrichment_data['total_funding'])
                    startup['totalFunding'] = verified_funding
                    startup['funding_verified'] = True
                except (ValueError, TypeError):
                    pass
            
            # Add insights if available
            if enrichment_data.get('insights'):
                startup['company_insights'] = enrichment_data['insights']
        
        # Also try direct detail lookup
        details = await MCP_TOOLS._get_startup_details(company_name)
        
        if details:
            # Update with more accurate employee data
            if details.get('employees'):
                try:
                    emp_count = int(details['employees'])
                    startup['employee_count_verified'] = emp_count
                except (ValueError, TypeError):
                    pass
            
            # Update website if missing
            if not startup.get('website') and details.get('website'):
                startup['website'] = details['website']
    
    except Exception as e:
        logger.debug(f"MCP enrichment failed for {startup.get('company_name')}: {e}")
        # Continue with original data
    
    return startup


def init_mcp_tools() -> bool:
    """Initialize MCP tools"""
    global MCP_TOOLS
    
    if not HAS_MCP:
        logger.warning("MCP not available")
        return False
    
    try:
        MCP_TOOLS = StartupDatabaseMCPTools()
        logger.info("MCP tools initialized")
        return True
    except Exception as e:
        logger.warning(f"Failed to initialize MCP tools: {e}")
        return False


# ============================================================================
# RULE MATCHING (Enhanced with LLM analysis)
# ============================================================================

def matches_rule_1(startup: Dict, use_llm: bool = False) -> Tuple[bool, int, List[str]]:
    """Rule 1: Agentic Platform Enablers"""
    search_text = get_search_text(startup)
    
    primary_matches = text_search(search_text, RULE_1_KEYWORDS['primary'])
    secondary_matches = text_search(search_text, RULE_1_KEYWORDS['secondary'])
    
    # Base matching
    matches = primary_matches >= 1 or secondary_matches >= 2
    confidence = min(100, (primary_matches * 30) + (secondary_matches * 10))
    
    # LLM-based assessment if available
    if use_llm and HAS_LLM and matches:
        try:
            model = get_nvidia_nim_model() if is_nvidia_nim_configured() else None
            prompt = f"""Assess if this startup matches "Agentic Platform Enablers" (AI infrastructure, MLOps, agent orchestration, observability):
            
Company: {startup.get('company_name', 'Unknown')}
Description: {startup.get('company_description', '')[:500]}
Website: {startup.get('website', 'N/A')}

Respond ONLY with JSON: {{"matches": true/false, "confidence": 0-100}}"""
            
            response = llm_completion_sync(
                [{"role": "user", "content": prompt}],
                model=model
            )
            
            if response and hasattr(response, 'choices'):
                content = response.choices[0].message.content
                
                # Extract JSON from response (may be wrapped in markdown code blocks)
                json_str = content.strip()
                if json_str.startswith('```'):
                    # Remove markdown code blocks
                    json_str = json_str.split('```')[1]
                    if json_str.startswith('json\n'):
                        json_str = json_str[5:]
                    json_str = json_str.split('```')[0]
                
                result = json.loads(json_str)
                old_confidence = confidence
                confidence = int(result.get('confidence', confidence))
                matches = result.get('matches', matches)
                
                logger.debug(f"{startup.get('company_name')} - Rule 1: confidence {old_confidence}->{confidence}")
        except Exception as e:
            logger.debug(f"LLM assessment failed for Rule 1: {e}")
    
    matched_keywords = []
    text_lower = search_text.lower()
    for kw in RULE_1_KEYWORDS['primary']:
        if kw in text_lower:
            matched_keywords.append(kw)
    
    return matches, confidence, matched_keywords[:5]


def matches_rule_2(startup: Dict, use_llm: bool = False) -> Tuple[bool, int, List[str]]:
    """Rule 2: Agentic Service Providers (Non-Insurance)"""
    search_text = get_search_text(startup)
    
    # Exclude if insurance-specific
    if text_search(search_text, ['insurance', 'insurtech', 'claims', 'underwriting']) > 0:
        return False, 0, []
    
    primary_matches = text_search(search_text, RULE_2_KEYWORDS['primary'])
    secondary_matches = text_search(search_text, RULE_2_KEYWORDS['secondary'])
    
    matches = primary_matches >= 1 or secondary_matches >= 3
    confidence = min(100, (primary_matches * 25) + (secondary_matches * 8))
    
    matched_keywords = []
    text_lower = search_text.lower()
    for kw in RULE_2_KEYWORDS['primary']:
        if kw in text_lower:
            matched_keywords.append(kw)
    
    return matches, confidence, matched_keywords[:5]


def matches_rule_3(startup: Dict, use_llm: bool = False) -> Tuple[bool, int, List[str]]:
    """Rule 3: Insurance-Specific Solutions"""
    search_text = get_search_text(startup)
    
    primary_matches = text_search(search_text, RULE_3_KEYWORDS['primary'])
    secondary_matches = text_search(search_text, RULE_3_KEYWORDS['secondary'])
    
    matches = primary_matches >= 1 or secondary_matches >= 2
    confidence = min(100, (primary_matches * 35) + (secondary_matches * 12))
    
    matched_keywords = []
    text_lower = search_text.lower()
    for kw in RULE_3_KEYWORDS['primary']:
        if kw in text_lower:
            matched_keywords.append(kw)
    
    return matches, confidence, matched_keywords[:5]


def matches_rule_4(startup: Dict, use_llm: bool = False) -> Tuple[bool, int, List[str]]:
    """Rule 4: Health Innovations (Insurance Applicable)"""
    search_text = get_search_text(startup)
    
    primary_matches = text_search(search_text, RULE_4_KEYWORDS['primary'])
    secondary_matches = text_search(search_text, RULE_4_KEYWORDS['secondary'])
    
    matches = primary_matches >= 1 or secondary_matches >= 2
    confidence = min(100, (primary_matches * 30) + (secondary_matches * 10))
    
    matched_keywords = []
    text_lower = search_text.lower()
    for kw in RULE_4_KEYWORDS['primary']:
        if kw in text_lower:
            matched_keywords.append(kw)
    
    return matches, confidence, matched_keywords[:5]


def matches_rule_5(startup: Dict, use_llm: bool = False) -> Tuple[bool, int, List[str]]:
    """Rule 5: Development & Legacy Modernization"""
    search_text = get_search_text(startup)
    
    primary_matches = text_search(search_text, RULE_5_KEYWORDS['primary'])
    secondary_matches = text_search(search_text, RULE_5_KEYWORDS['secondary'])
    
    matches = primary_matches >= 1 or secondary_matches >= 3
    confidence = min(100, (primary_matches * 30) + (secondary_matches * 10))
    
    matched_keywords = []
    text_lower = search_text.lower()
    for kw in RULE_5_KEYWORDS['primary']:
        if kw in text_lower:
            matched_keywords.append(kw)
    
    return matches, confidence, matched_keywords[:5]


def can_be_axa_provider(startup: Dict, use_llm: bool = False) -> Tuple[bool, str]:
    """
    Check if a startup can potentially be used as a provider for AXA
    
    Uses NVIDIA NIM (DeepSeek-R1) for intelligent B2B viability assessment.
    
    Returns:
        (is_viable_provider, reason)
    """
    company_name = startup.get('company_name', startup.get('name', 'Unknown'))
    description = startup.get('company_description', startup.get('description', ''))
    industry = startup.get('primary_industry', '')
    business_types = startup.get('business_types', '')
    topics = startup.get('topics', [])
    website = startup.get('website', '')
    
    # First pass: Hard exclusions (obvious B2C/consumer)
    search_text = f"{company_name} {description} {industry} {' '.join(topics)}".lower()
    
    hard_exclusions = [
        'dating app', 'dating platform', 'matchmaking app',
        'food delivery', 'restaurant delivery', 'meal delivery',
        'social network', 'social media platform', 'influencer platform',
        'consumer marketplace', 'e-commerce platform', 'online shopping',
        'mobile game', 'gaming platform', 'game developer',
        'music streaming', 'video streaming', 'entertainment platform',
        'consumer app', 'b2c only', 'direct to consumer only'
    ]
    
    for exclusion in hard_exclusions:
        if exclusion in search_text:
            return False, f"Hard exclusion: {exclusion}"
    
    if not use_llm or not HAS_LLM:
        # Without LLM, use stricter keyword-based filtering
        consumer_signals = ['b2c', 'consumer', 'marketplace', 'p2p', 'social']
        consumer_count = sum(1 for sig in consumer_signals if sig in search_text)
        
        enterprise_signals = ['enterprise', 'b2b', 'saas', 'platform', 'api', 'infrastructure', 
                             'automation', 'analytics', 'security', 'compliance']
        enterprise_count = sum(1 for sig in enterprise_signals if sig in search_text)
        
        # Must have enterprise signals or very few consumer signals
        if enterprise_count >= 2 or consumer_count == 0:
            return True, "Enterprise indicators present"
        elif consumer_count >= 2 and enterprise_count == 0:
            return False, "Strong consumer-only indicators"
        
        return True, "Neutral - needs LLM assessment"
    
    # Use NVIDIA NIM for intelligent assessment
    try:
        assessment_prompt = f"""You are an expert analyst evaluating B2B technology vendors for AXA, a global insurance corporation with 140,000+ employees.

STARTUP TO EVALUATE:
Company: {company_name}
Industry: {industry}
Business Model: {business_types}
Description: {description[:600]}
Website: {website}
Topics: {', '.join(topics[:5]) if topics else 'N/A'}

EVALUATION CRITERIA - Can this startup be an AXA vendor/provider?

✅ VIABLE if the startup:
• Provides B2B software, APIs, or enterprise services
• Offers solutions for: insurance operations, risk assessment, claims processing, fraud detection
• Enables: process automation, data analytics, AI/ML infrastructure, security, compliance
• Delivers: developer tools, IT infrastructure, employee productivity, customer service platforms
• Has: proven enterprise deployment, APIs for integration, B2B licensing model
• Serves: insurance companies, financial services, large enterprises, regulated industries

❌ NOT VIABLE if the startup:
• Pure B2C consumer app with no B2B offering
• Consumer marketplace, social network, dating app, food delivery
• Gaming, entertainment, lifestyle consumer products
• No clear path to enterprise adoption (mobile-only consumer apps)
• Focused solely on individual consumers, not businesses
• Geographic/market mismatch (e.g., China-only, consumer retail only)

IMPORTANT NUANCES:
• Healthtech can be viable IF it offers employer/payer solutions (not just direct-to-consumer wellness)
• Fintech can be viable IF it provides B2B APIs/infrastructure (not just consumer banking apps)
• Marketplace models can be viable IF they have B2B SaaS components
• Developer tools, AI platforms, data services are almost always viable

PROVIDE YOUR ASSESSMENT:
1. DECISION: VIABLE or NOT_VIABLE
2. CONFIDENCE: 0-100 (be decisive: >80 for clear cases)
3. REASON: One clear sentence explaining why

Format exactly as:
DECISION: [VIABLE or NOT_VIABLE]
CONFIDENCE: [number]
REASON: [explanation]"""
        
        model = get_nvidia_nim_model() if is_nvidia_nim_configured() else None
        response = llm_completion_sync(
            [{"role": "user", "content": assessment_prompt}],
            model=model,
            max_tokens=300,
            temperature=0.3  # Lower temperature for more consistent evaluation
        )
        
        # Extract and parse response
        if response and hasattr(response, 'choices'):
            message = response.choices[0].message
            content = message.content if message.content else ""
            
            # DeepSeek-R1 may put reasoning separate
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                reasoning = message.reasoning_content
                # Use reasoning if content is empty
                if not content:
                    content = reasoning
            
            if not content:
                logger.warning(f"Empty LLM response for {company_name} - defaulting to NOT VIABLE")
                return False, "LLM returned empty response - conservative exclusion"
        else:
            logger.warning(f"Invalid LLM response structure for {company_name}")
            return False, "LLM error - conservative exclusion"
        
        # Parse structured response
        lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
        decision = None
        confidence = 0
        reason = "LLM assessment"
        
        for line in lines:
            if 'DECISION:' in line.upper():
                decision_text = line.split(':', 1)[1].strip().upper()
                decision = 'VIABLE' in decision_text and 'NOT' not in decision_text
            elif 'CONFIDENCE:' in line.upper():
                try:
                    conf_str = line.split(':', 1)[1].strip()
                    # Extract just the number
                    confidence = int(''.join(filter(str.isdigit, conf_str)))
                except Exception as e:
                    logger.debug(f"Failed to parse confidence: {e}")
                    confidence = 50
            elif 'REASON:' in line.upper():
                reason = line.split(':', 1)[1].strip()
        
        # Validation and decision logic
        if decision is None:
            # Try to infer from content
            content_lower = content.lower()
            if 'not viable' in content_lower or 'not_viable' in content_lower:
                decision = False
                confidence = 75
            elif 'viable' in content_lower:
                decision = True
                confidence = 70
            else:
                # No clear decision - be conservative
                logger.warning(f"Could not parse decision for {company_name}, defaulting to NOT VIABLE")
                return False, f"LLM unclear - excluded for safety. Response: {content[:100]}"
        
        # Apply confidence thresholds
        if decision and confidence >= 70:
            return True, reason
        elif not decision and confidence >= 70:
            return False, reason
        elif not decision and confidence >= 50:
            # Moderately confident NOT viable - exclude
            return False, f"{reason} (moderate confidence exclusion)"
        elif decision and confidence < 50:
            # Low confidence viable - be conservative, exclude
            return False, f"Low confidence match - {reason}"
        else:
            # Ambiguous - default to exclusion for quality
            return False, f"Uncertain assessment (conf={confidence}) - {reason}"
        
    except Exception as e:
        logger.warning(f"LLM provider assessment failed for {company_name}: {e}")
        # On error, be conservative - exclude
        return False, f"LLM assessment error - excluded for quality control"


def should_exclude(startup: Dict, use_llm: bool = False) -> bool:
    """Check if startup should be excluded from AXA provider consideration
    
    Args:
        startup: Startup data
        use_llm: Whether to use LLM for provider assessment (recommended)
    
    Returns:
        True if startup should be excluded, False otherwise
    """
    search_text = get_search_text(startup).lower()
    company_name = startup.get('company_name', '').lower()
    
    # Hard exclusions - obvious consumer/B2C companies
    critical_exclusions = [
        # Consumer apps
        'b2c app', 'consumer app only', 'mobile app for consumers',
        # Social & Dating
        'dating app', 'dating platform', 'matchmaking service',
        'social network', 'social media app', 'influencer platform',
        # Food & Delivery
        'food delivery app', 'restaurant delivery', 'meal kit delivery',
        'grocery delivery app', 'food ordering app',
        # Entertainment & Gaming
        'mobile game', 'gaming app', 'video game', 'esports platform',
        'streaming service', 'music app', 'video platform',
        # E-commerce & Marketplaces (pure consumer)
        'consumer marketplace', 'online shopping app', 'retail app',
        'fashion marketplace', 'beauty products'
    ]
    
    for exclusion in critical_exclusions:
        if exclusion in search_text or exclusion in company_name:
            logger.debug(f"Hard exclusion: {startup.get('company_name')} - {exclusion}")
            return True
    
    # Use LLM for intelligent provider viability assessment
    if use_llm:
        can_be_provider, reason = can_be_axa_provider(startup, use_llm=True)
        if not can_be_provider:
            logger.debug(f"LLM exclusion: {startup.get('company_name')} - {reason}")
            return True
        return False
    else:
        # Without LLM, use more conservative keyword-based exclusion
        consumer_only_indicators = [
            'b2c', 'consumer', 'marketplace', 'retail', 'shopping',
            'gaming', 'entertainment', 'social network', 'dating'
        ]
        
        enterprise_indicators = [
            'b2b', 'enterprise', 'saas', 'platform', 'api',
            'infrastructure', 'developer', 'automation', 'analytics'
        ]
        
        consumer_count = sum(1 for ind in consumer_only_indicators if ind in search_text)
        enterprise_count = sum(1 for ind in enterprise_indicators if ind in search_text)
        
        # Exclude if strong consumer signals and no enterprise signals
        if consumer_count >= 3 and enterprise_count == 0:
            logger.debug(f"Keyword exclusion: {startup.get('company_name')} - Strong consumer indicators")
            return True
        
        # Don't exclude - let it through for manual review or LLM analysis later
        return False


# ============================================================================
# ENHANCED SCORING
# ============================================================================

def calculate_axa_score_enhanced(startup: Dict, use_llm: bool = False) -> Dict:
    """
    Calculate comprehensive AXA priority score with funding and size emphasis
    
    Scoring breakdown:
    - Rule matching: 0-35 points (base rule score)
    - Multi-rule bonus: 0-10 points
    - Funding: 0-40 points (NEW - prioritized)
    - Company size: 0-30 points (NEW - prioritized)
    - Maturity: 0-10 points
    
    Total: 0-125 points (normalized to 0-100)
    """
    
    # Check exclusions first
    can_be_provider, exclusion_reason = can_be_axa_provider(startup, use_llm=use_llm)
    if not can_be_provider or should_exclude(startup, use_llm=use_llm):
        return {
            'total_score': 0,
            'normalized_score': 0,
            'tier': 'Excluded',
            'matched_rules': [],
            'rule_scores': {},
            'breakdown': {'excluded': True, 'exclusion_reason': exclusion_reason or 'Does not meet AXA provider criteria'},
            'funding_amount': 0,
            'funding_stage': 'Undisclosed',
            'employee_count': 0,
            'size_category': 'Unknown'
        }
    
    # Parse funding and size
    funding_amount, funding_stage = parse_funding_amount(startup)
    employee_count, size_category = parse_employee_count(startup)
    
    # Check rule matches
    rule_matches = []
    rule_scores = {}
    max_rule_score = 0
    
    rules = {
        'Rule 1: Platform Enablers': (matches_rule_1, 35),
        'Rule 2: Service Providers': (matches_rule_2, 30),
        'Rule 3: Insurance Solutions': (matches_rule_3, 35),
        'Rule 4: Health Innovations': (matches_rule_4, 30),
        'Rule 5: Dev & Legacy': (matches_rule_5, 35)
    }
    
    for rule_name, (rule_func, base_score) in rules.items():
        matches, confidence, keywords = rule_func(startup, use_llm=use_llm)
        if matches:
            rule_matches.append(rule_name)
            score = int(base_score * (confidence / 100))
            rule_scores[rule_name] = {
                'score': score,
                'confidence': confidence,
                'keywords': keywords
            }
            max_rule_score = max(max_rule_score, score)
    
    # Multiple rule bonus
    multi_rule_bonus = 10 if len(rule_matches) > 1 else 0
    rule_total = max_rule_score + multi_rule_bonus
    
    # NEW: Funding and size scores (emphasized)
    funding_score = calculate_funding_score(startup)
    size_score = calculate_size_score(startup)
    maturity_score = calculate_maturity_score(startup)
    
    # Raw score before normalization
    raw_score = rule_total + funding_score + size_score + maturity_score
    
    # Normalize to 0-100
    # Maximum possible: 35 + 10 + 40 + 30 + 10 = 125
    normalized_score = min(100, int(raw_score * 100 / 125))
    
    # Determine tier based on funding + rule match combination
    if funding_amount >= 100 and len(rule_matches) >= 2:
        tier = 'Tier 1: Must Meet'
    elif funding_amount >= 50 or (funding_amount >= 10 and len(rule_matches) >= 2):
        tier = 'Tier 2: High Priority'
    elif normalized_score >= 60:
        tier = 'Tier 2: High Priority'
    elif normalized_score >= 40:
        tier = 'Tier 3: Medium Priority'
    elif normalized_score >= 20:
        tier = 'Tier 4: Low Priority'
    else:
        tier = 'Excluded'
    
    return {
        'total_score': normalized_score,
        'normalized_score': normalized_score,
        'tier': tier,
        'matched_rules': rule_matches,
        'rule_scores': rule_scores,
        'breakdown': {
            'rule_score': rule_total,
            'multi_rule_bonus': multi_rule_bonus,
            'funding': funding_score,
            'size': size_score,
            'maturity': maturity_score,
            'raw_total': raw_score
        },
        'funding': {
            'amount_millions': funding_amount,
            'stage': funding_stage
        },
        'company_size': {
            'employee_count': employee_count,
            'category': size_category
        }
    }


def filter_startups_enhanced(startups: List[Dict], min_score: int = 50, 
                            use_llm: bool = False,
                            use_mcp: bool = False,
                            specific_rule: Optional[int] = None,
                            batch_size: int = 5,
                            max_parallel_llm: int = 3) -> Tuple[List[Dict], Dict]:
    """Filter and score startups with enhanced criteria and batch LLM processing
    
    Args:
        startups: List of startup dictionaries
        min_score: Minimum score threshold
        use_llm: Enable NVIDIA NIM analysis
        use_mcp: Enable MCP enrichment
        specific_rule: Filter by specific rule
        batch_size: Number of startups to process before LLM batch
        max_parallel_llm: Max concurrent LLM requests
    """
    
    filtered = []
    excluded = {'score_too_low': 0, 'excluded_keywords': 0, 'no_rules': 0}
    
    # Initialize MCP if needed
    if use_mcp:
        init_mcp_tools()
    
    # Phase 1: Quick local scoring for all startups
    logger.info("Phase 1: Local scoring...")
    candidates = []
    
    for i, startup in enumerate(startups):
        if i % 500 == 0 and i > 0:
            logger.info(f"  Processed {i}/{len(startups)} startups")
        
        # MCP enrichment (optional)
        if use_mcp and MCP_TOOLS:
            try:
                enrichment = MCP_TOOLS._get_enrichment_data(startup.get('company_name', ''))
                if enrichment:
                    startup['mcp_enriched'] = enrichment
                    if enrichment.get('total_funding'):
                        try:
                            startup['totalFunding'] = float(enrichment['total_funding'])
                        except:
                            pass
            except Exception as e:
                logger.debug(f"MCP enrichment failed: {e}")
        
        # Quick local scoring (no LLM)
        scoring = calculate_axa_score_enhanced(startup, use_llm=False)
        
        # Apply basic filters
        if scoring['tier'] == 'Excluded':
            excluded['excluded_keywords'] += 1
            continue
        
        if scoring['total_score'] < min_score:
            excluded['score_too_low'] += 1
            continue
        
        if not scoring['matched_rules']:
            excluded['no_rules'] += 1
            continue
        
        if specific_rule:
            rule_name = f"Rule {specific_rule}"
            if not any(rule_name in matched for matched in scoring['matched_rules']):
                continue
        
        startup['axa_scoring'] = scoring
        candidates.append(startup)
    
    logger.info(f"  Candidates for detailed analysis: {len(candidates)}")
    
    # Phase 2: Batch LLM analysis for high-value candidates (if enabled)
    if use_llm and len(candidates) > 0:
        logger.info("Phase 2: LLM-enhanced validation...")
        filtered = batch_llm_validation(candidates, max_parallel=max_parallel_llm)
    else:
        filtered = candidates
    
    # Final sort by score, with funding as tiebreaker
    filtered.sort(key=lambda x: (
        x['axa_scoring']['total_score'],
        x['axa_scoring'].get('funding', {}).get('amount_millions', 0)
    ), reverse=True)
    
    return filtered, excluded


def batch_llm_validation(candidates: List[Dict], max_parallel: int = 3) -> List[Dict]:
    """Validate candidates using batch LLM processing
    
    Uses concurrent requests to speed up validation
    """
    
    if not HAS_LLM or not candidates:
        return candidates
    
    logger.info(f"  Validating {len(candidates)} candidates with LLM (max {max_parallel} parallel)...")
    
    def validate_startup(startup):
        """Re-score a startup using LLM for rule validation"""
        try:
            scoring = calculate_axa_score_enhanced(startup, use_llm=True)
            startup['axa_scoring'] = scoring
            return startup
        except Exception as e:
            logger.debug(f"LLM validation failed for {startup.get('company_name', 'Unknown')}: {e}")
            return startup
    
    start_time = time.time()
    validated = []
    
    # Use ThreadPoolExecutor for parallel LLM calls
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as executor:
        # Submit all tasks
        futures = {executor.submit(validate_startup, c): c for c in candidates}
        
        # Process as they complete
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            validated.append(future.result())
            completed += 1
            
            if completed % max(1, len(candidates) // 5) == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                remaining = (len(candidates) - completed) / rate if rate > 0 else 0
                logger.info(f"    {completed}/{len(candidates)} ({100*completed/len(candidates):.0f}%) - "
                           f"Rate: {rate:.1f}/sec, ETA: {remaining:.0f}s")
    
    elapsed = time.time() - start_time
    logger.info(f"  LLM validation complete ({elapsed:.1f}s, {len(candidates)/elapsed:.1f} startups/sec)")
    
    return validated


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Enhanced AXA startup filter using MCP and NVIDIA NIM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--input', default='docs/architecture/ddbb/slush_full_list.json',
                        help='Input database file')
    parser.add_argument('--output', '-o',
                        help='Output file')
    parser.add_argument('--min-score', type=int, default=50,
                        help='Minimum score threshold (default: 50)')
    parser.add_argument('--include-llm-analysis', action='store_true',
                        help='Use NVIDIA NIM for enhanced rule analysis (slower but higher quality)')
    parser.add_argument('--use-mcp', action='store_true',
                        help='Use MCP server for startup enrichment')
    parser.add_argument('--local-only', action='store_true',
                        help='Use only local analysis, skip MCP/LLM')
    parser.add_argument('--split-by-tier', action='store_true',
                        help='Split output into separate files by tier')
    parser.add_argument('--output-dir',
                        help='Output directory for tier split')
    parser.add_argument('--stats', action='store_true',
                        help='Show statistics')
    parser.add_argument('--csv', action='store_true',
                        help='Also export CSV summary')
    
    args = parser.parse_args()
    
    if not args.output and not args.output_dir:
        parser.error("Either --output or --output-dir must be specified")
    
    # Load startups
    base_path = Path(__file__).parent.parent
    input_file = base_path / args.input
    
    logger.info(f"Loading startups from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        startups = json.load(f)
    logger.info(f"Loaded {len(startups)} startups")
    
    # Check capabilities
    use_llm = args.include_llm_analysis and HAS_LLM and not args.local_only
    use_mcp = args.use_mcp and HAS_MCP and not args.local_only
    
    if use_llm:
        if is_nvidia_nim_configured():
            logger.info("✓ NVIDIA NIM configured - will use DeepSeek-R1")
        else:
            logger.info("⚠ NVIDIA NIM not configured - using fallback LLM provider")
    
    if use_mcp:
        logger.info("✓ MCP enabled - will enrich startup data from database")
    
    # Filter startups
    logger.info(f"Filtering with min_score={args.min_score}")
    if use_llm:
        logger.info("  + LLM-assisted rule analysis enabled")
    if use_mcp:
        logger.info("  + MCP enrichment enabled")
    
    filtered, excluded = filter_startups_enhanced(
        startups, 
        args.min_score, 
        use_llm=use_llm,
        use_mcp=use_mcp
    )
    
    logger.info(f"Filtered to {len(filtered)} startups ({100*len(filtered)/len(startups):.1f}%)")
    logger.info(f"  Excluded - Keywords: {excluded['excluded_keywords']}")
    logger.info(f"  Excluded - Score too low: {excluded['score_too_low']}")
    logger.info(f"  Excluded - No matching rules: {excluded['no_rules']}")
    
    # Statistics
    if args.stats:
        print("\n" + "="*80)
        print("AXA STARTUP FILTERING RESULTS (ENHANCED WITH MCP & NIM)")
        print("="*80)
        
        # Tier breakdown
        tier_counts = {}
        for s in filtered:
            tier = s['axa_scoring']['tier']
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        print(f"\n📊 TIER BREAKDOWN:")
        for tier in ['Tier 1: Must Meet', 'Tier 2: High Priority', 
                     'Tier 3: Medium Priority', 'Tier 4: Low Priority']:
            count = tier_counts.get(tier, 0)
            if count > 0:
                print(f"  {tier}: {count}")
        
        # Rule breakdown
        rule_counts = {}
        for s in filtered:
            for rule in s['axa_scoring']['matched_rules']:
                rule_counts[rule] = rule_counts.get(rule, 0) + 1
        
        print(f"\n📋 RULE MATCHES:")
        for rule, count in sorted(rule_counts.items()):
            print(f"  {rule}: {count}")
        
        # Funding distribution
        print(f"\n💰 FUNDING DISTRIBUTION:")
        funded_count = sum(1 for s in filtered if s['axa_scoring'].get('funding', {}).get('amount_millions', 0) > 0)
        avg_funding = sum(s['axa_scoring'].get('funding', {}).get('amount_millions', 0) for s in filtered) / len(filtered) if filtered else 0
        print(f"  Funded startups: {funded_count}/{len(filtered)} ({100*funded_count/len(filtered):.1f}%)")
        print(f"  Average funding: ${avg_funding:.1f}M")
        
        # Size distribution
        print(f"\n👥 COMPANY SIZE DISTRIBUTION:")
        size_10_plus = sum(1 for s in filtered if s['axa_scoring'].get('company_size', {}).get('employee_count', 0) >= 10)
        size_50_plus = sum(1 for s in filtered if s['axa_scoring'].get('company_size', {}).get('employee_count', 0) >= 50)
        print(f"  10+ employees: {size_10_plus}/{len(filtered)} ({100*size_10_plus/len(filtered):.1f}%)")
        print(f"  50+ employees: {size_50_plus}/{len(filtered)} ({100*size_50_plus/len(filtered):.1f}%)")
        
        # Top 10
        print(f"\n🏆 TOP 10 STARTUPS BY SCORE:")
        for i, s in enumerate(filtered[:10], 1):
            score = s['axa_scoring']['total_score']
            tier = s['axa_scoring']['tier']
            funding = s['axa_scoring'].get('funding', {}).get('amount_millions', 0)
            employees = s['axa_scoring'].get('company_size', {}).get('employee_count', 0)
            rules = ', '.join([r.split(':')[0] for r in s['axa_scoring'].get('matched_rules', [])])
            company_name = s.get('company_name', 'Unknown')
            
            funding_str = f"${funding:.0f}M" if funding > 0 else "Undisclosed"
            size_str = f"{employees} employees" if employees > 0 else "Size unknown"
            
            print(f"  {i}. {company_name}")
            print(f"     Score: {score}/100 | Funding: {funding_str} | Size: {size_str}")
            print(f"     Rules: {rules}")
        
        print("="*80 + "\n")
    
    # Output
    if args.split_by_tier:
        output_dir = base_path / (args.output_dir or 'downloads/axa_tiers_enhanced/')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        by_tier = {}
        for s in filtered:
            tier = s['axa_scoring']['tier']
            if tier not in by_tier:
                by_tier[tier] = []
            by_tier[tier].append(s)
        
        for tier, startups_in_tier in by_tier.items():
            tier_num = tier.split(':')[0].replace('Tier ', '').strip()
            filename = f"axa_tier{tier_num}_enhanced.json"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(startups_in_tier, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(startups_in_tier)} startups to {filename}")
    
    if args.output:
        output_path = base_path / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved {len(filtered)} startups to {args.output}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
