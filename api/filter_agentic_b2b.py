#!/usr/bin/env python3
"""
Agentic AI B2B Solutions Filter - Find all enterprise agentic AI solutions

This script identifies startups that provide agentic AI solutions for enterprises,
including autonomous agents, multi-agent systems, AI workflows, and agent-based automation.

Usage:
    source .venv/bin/activate
    python3 api/filter_agentic_b2b.py --output downloads/agentic_b2b_solutions.json --stats
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Try to import LLM tools
try:
    from api.llm_config import llm_completion_sync, is_nvidia_nim_configured, get_nvidia_nim_model
    HAS_LLM = True
except ImportError:
    try:
        from llm_config import llm_completion_sync, is_nvidia_nim_configured, get_nvidia_nim_model
        HAS_LLM = True
    except ImportError:
        HAS_LLM = False
        logger.warning("LLM config not available - using keyword-only filtering")


# ============================================================================
# AGENTIC AI KEYWORD DEFINITIONS
# ============================================================================

AGENTIC_AI_KEYWORDS = {
    # Core agentic AI concepts
    'core_agentic': [
        'agentic ai', 'agentic', 'autonomous agent', 'ai agent', 'agent-based',
        'multi-agent', 'agent system', 'agent platform', 'agent framework',
        'agent orchestration', 'agent mesh', 'agent swarm', 'agent network',
        'cognitive agent', 'intelligent agent', 'agent automation'
    ],
    
    # Agentic workflows & orchestration
    'workflow': [
        'agentic workflow', 'autonomous workflow', 'ai workflow', 'agent workflow',
        'workflow automation', 'workflow orchestration', 'intelligent workflow',
        'automated workflow', 'adaptive workflow', 'dynamic workflow'
    ],
    
    # AI automation & process
    'automation': [
        'ai automation', 'intelligent automation', 'cognitive automation',
        'process automation ai', 'business process ai', 'hyperautomation',
        'autonomous automation', 'self-driving automation'
    ],
    
    # Agent infrastructure & platforms
    'infrastructure': [
        'agent infrastructure', 'ai ops', 'llm ops', 'agent builder',
        'agent platform', 'agent deployment', 'agent monitoring',
        'agent orchestration platform', 'agent framework', 'agent sdk'
    ],
    
    # Enterprise AI applications
    'enterprise_solutions': [
        'enterprise ai', 'enterprise automation', 'b2b ai', 'business ai',
        'enterprise intelligence', 'enterprise agent', 'corporate ai'
    ],
    
    # Specific agentic use cases
    'use_cases': [
        'ai customer service', 'ai support agent', 'ai sales agent',
        'ai research agent', 'ai analyst', 'ai assistant enterprise',
        'ai copilot', 'ai employee', 'digital worker', 'virtual agent',
        'conversational ai enterprise', 'ai receptionist', 'ai scheduler',
        'ai data analyst', 'ai coding assistant', 'ai security agent'
    ],
    
    # Technology indicators
    'technology': [
        'llm', 'large language model', 'generative ai', 'gen ai',
        'rag', 'retrieval augmented generation', 'vector database',
        'embedding', 'nlp', 'natural language processing',
        'machine learning platform', 'deep learning', 'neural network'
    ],
    
    # Insurance & financial specific agentic
    'domain_specific': [
        'ai underwriting', 'ai claims', 'claims automation ai',
        'underwriting automation', 'insurance ai', 'insurtech ai',
        'contact center ai', 'call center ai', 'customer support ai',
        'fraud detection ai', 'risk assessment ai', 'compliance ai',
        'regulatory ai', 'kyc ai', 'aml ai'
    ]
}

B2B_INDICATORS = [
    'b2b', 'enterprise', 'saas', 'platform', 'api', 'sdk',
    'infrastructure', 'for business', 'for companies', 'for organizations',
    'corporate', 'workplace', 'professional', 'business solution',
    'enterprise grade', 'enterprise-grade', 'fortune 500'
]

EXCLUSION_KEYWORDS = [
    'b2c only', 'consumer app', 'consumer only', 'mobile game', 'gaming app',
    'dating app', 'food delivery', 'restaurant app', 'social media app',
    'influencer platform', 'creator platform', 'content creator'
]


# ============================================================================
# SCORING & MATCHING
# ============================================================================

def text_search(text: str, keywords: List[str]) -> Tuple[int, List[str]]:
    """Search for keywords in text, return count and matched keywords"""
    if not text:
        return 0, []
    
    text_lower = text.lower()
    matched = []
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            matched.append(keyword)
    
    return len(matched), matched


def get_search_text(startup: Dict) -> str:
    """Extract all searchable text from startup"""
    parts = [
        startup.get('company_name', ''),
        startup.get('company_description', ''),
        startup.get('shortDescription', ''),
        startup.get('primary_industry', ''),
        ' '.join(startup.get('topics', []) or []),
        ' '.join(startup.get('industries', []) or [])
    ]
    return ' '.join(filter(None, parts))


def is_agentic_b2b_solution(startup: Dict, use_llm: bool = False) -> Tuple[bool, int, Dict]:
    """
    Determine if startup is an agentic AI B2B solution
    
    Returns:
        (is_agentic, confidence_score, match_details)
    """
    search_text = get_search_text(startup)
    
    # Quick exclusions
    for exclusion in EXCLUSION_KEYWORDS:
        if exclusion in search_text.lower():
            return False, 0, {'reason': f'Excluded: {exclusion}'}
    
    # Score each category
    scores = {}
    all_matched_keywords = []
    
    for category, keywords in AGENTIC_AI_KEYWORDS.items():
        count, matched = text_search(search_text, keywords)
        scores[category] = count
        all_matched_keywords.extend(matched)
    
    # B2B check
    b2b_count, b2b_matched = text_search(search_text, B2B_INDICATORS)
    scores['b2b_indicators'] = b2b_count
    
    # Scoring logic
    core_score = scores.get('core_agentic', 0) * 30
    workflow_score = scores.get('workflow', 0) * 25
    automation_score = scores.get('automation', 0) * 15
    infrastructure_score = scores.get('infrastructure', 0) * 20
    enterprise_score = scores.get('enterprise_solutions', 0) * 20
    use_case_score = scores.get('use_cases', 0) * 15
    tech_score = min(scores.get('technology', 0) * 5, 15)  # Cap at 15
    domain_score = scores.get('domain_specific', 0) * 25
    b2b_score = min(b2b_count * 10, 20)  # Cap at 20
    
    # Calculate base score
    base_score = (
        core_score + workflow_score + automation_score + 
        infrastructure_score + enterprise_score + use_case_score + 
        tech_score + domain_score + b2b_score
    )
    
    # Normalize to 0-100
    confidence = min(100, base_score)
    
    # Matching criteria - must meet at least ONE of these:
    is_match = (
        scores.get('core_agentic', 0) >= 1 or  # Has core agentic keywords
        scores.get('workflow', 0) >= 1 or       # Has workflow keywords
        (scores.get('automation', 0) >= 2 and scores.get('technology', 0) >= 1) or  # AI automation
        scores.get('domain_specific', 0) >= 1 or  # Domain-specific agentic
        (scores.get('use_cases', 0) >= 2 and b2b_count >= 1)  # Multiple use cases + B2B
    )
    
    # Boost if has B2B indicators
    if not is_match and b2b_count >= 2 and scores.get('technology', 0) >= 2:
        is_match = True
        confidence = max(confidence, 50)
    
    # LLM validation for edge cases
    if use_llm and HAS_LLM and is_match and confidence < 70:
        try:
            llm_result = validate_with_llm(startup)
            if llm_result:
                is_match = llm_result['is_agentic']
                confidence = max(confidence, llm_result['confidence'])
        except Exception as e:
            logger.debug(f"LLM validation failed: {e}")
    
    match_details = {
        'confidence': confidence,
        'matched_keywords': list(set(all_matched_keywords))[:10],
        'b2b_indicators': b2b_matched[:5],
        'category_scores': scores,
        'score_breakdown': {
            'core_agentic': core_score,
            'workflow': workflow_score,
            'automation': automation_score,
            'infrastructure': infrastructure_score,
            'enterprise': enterprise_score,
            'use_cases': use_case_score,
            'technology': tech_score,
            'domain_specific': domain_score,
            'b2b': b2b_score
        }
    }
    
    return is_match, confidence, match_details


def validate_with_llm(startup: Dict) -> Dict:
    """Use NVIDIA NIM to validate if startup is truly agentic B2B"""
    if not HAS_LLM:
        return None
    
    try:
        prompt = f"""You are an expert analyst evaluating agentic AI solutions for enterprises.

STARTUP TO EVALUATE:
Company: {startup.get('company_name', 'Unknown')}
Description: {startup.get('company_description', '')[:600]}
Industry: {startup.get('primary_industry', '')}
Topics: {', '.join(startup.get('topics', [])[:5])}
Website: {startup.get('website', '')}

DEFINITION OF AGENTIC AI:
- Autonomous AI agents that can perceive, reason, and act independently
- Multi-agent systems that collaborate to achieve goals
- AI workflows that adapt and make decisions without human intervention
- Intelligent automation using LLMs, reasoning, and tool use
- Agent-based platforms for orchestrating AI tasks

EVALUATION CRITERIA:
✅ IS AGENTIC if the startup provides:
• Autonomous AI agents for business tasks
• Multi-agent orchestration platforms
• Agentic workflow automation
• AI agents with reasoning & tool use (RAG, function calling)
• Agent-based customer service, sales, research, or operations
• Agent infrastructure (LLMOps, agent monitoring, agent frameworks)
• Contact center AI with autonomous agents
• AI underwriting/claims with agent-based decision making
• Agentic coding/development assistants

❌ NOT AGENTIC if:
• Simple chatbots without autonomy or reasoning
• Traditional ML/analytics without agent capabilities
• Static automation without AI decision-making
• Pure infrastructure without agent focus
• Consumer apps

B2B REQUIREMENT: Must serve enterprises, not consumers.

RESPOND WITH:
IS_AGENTIC: true/false
CONFIDENCE: 0-100
REASON: Brief explanation

Format exactly as:
IS_AGENTIC: [true/false]
CONFIDENCE: [number]
REASON: [explanation]"""
        
        model = get_nvidia_nim_model() if is_nvidia_nim_configured() else None
        response = llm_completion_sync(
            [{"role": "user", "content": prompt}],
            model=model,
            max_tokens=250,
            temperature=0.3
        )
        
        if not response or not hasattr(response, 'choices'):
            return None
        
        content = response.choices[0].message.content
        if hasattr(response.choices[0].message, 'reasoning_content'):
            reasoning = response.choices[0].message.reasoning_content
            if reasoning and not content:
                content = reasoning
        
        if not content:
            return None
        
        # Parse response
        lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
        is_agentic = False
        confidence = 50
        reason = ""
        
        for line in lines:
            if 'IS_AGENTIC:' in line.upper():
                is_agentic = 'true' in line.lower()
            elif 'CONFIDENCE:' in line.upper():
                try:
                    conf_str = line.split(':', 1)[1].strip()
                    confidence = int(''.join(filter(str.isdigit, conf_str)))
                except:
                    pass
            elif 'REASON:' in line.upper():
                reason = line.split(':', 1)[1].strip()
        
        return {
            'is_agentic': is_agentic,
            'confidence': confidence,
            'reason': reason
        }
        
    except Exception as e:
        logger.debug(f"LLM validation error: {e}")
        return None


def filter_agentic_b2b(startups: List[Dict], min_confidence: int = 40, 
                      use_llm: bool = False) -> List[Dict]:
    """Filter startups to find agentic B2B solutions"""
    
    filtered = []
    stats = {
        'total': len(startups),
        'matched': 0,
        'high_confidence': 0,
        'medium_confidence': 0,
        'low_confidence': 0
    }
    
    logger.info(f"Scanning {len(startups)} startups for agentic AI B2B solutions...")
    
    for i, startup in enumerate(startups):
        if i % 500 == 0 and i > 0:
            logger.info(f"  Processed {i}/{len(startups)} ({100*i/len(startups):.0f}%)")
        
        is_match, confidence, details = is_agentic_b2b_solution(startup, use_llm=use_llm)
        
        if is_match and confidence >= min_confidence:
            startup['agentic_analysis'] = details
            filtered.append(startup)
            stats['matched'] += 1
            
            if confidence >= 80:
                stats['high_confidence'] += 1
            elif confidence >= 60:
                stats['medium_confidence'] += 1
            else:
                stats['low_confidence'] += 1
    
    # Sort by confidence
    filtered.sort(key=lambda x: x['agentic_analysis']['confidence'], reverse=True)
    
    logger.info(f"\n✓ Found {stats['matched']} agentic B2B solutions")
    logger.info(f"  High confidence (80+): {stats['high_confidence']}")
    logger.info(f"  Medium confidence (60-79): {stats['medium_confidence']}")
    logger.info(f"  Low confidence (40-59): {stats['low_confidence']}")
    
    return filtered, stats


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Find all agentic AI solutions for enterprises (B2B)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--input', default='docs/architecture/ddbb/slush_full_list.json',
                       help='Input database file')
    parser.add_argument('--output', '-o', required=True,
                       help='Output JSON file')
    parser.add_argument('--min-confidence', type=int, default=40,
                       help='Minimum confidence score (default: 40)')
    parser.add_argument('--use-llm', action='store_true',
                       help='Use NVIDIA NIM for validation (slower but more accurate)')
    parser.add_argument('--stats', action='store_true',
                       help='Show detailed statistics')
    parser.add_argument('--csv', action='store_true',
                       help='Also export CSV summary')
    
    args = parser.parse_args()
    
    # Load database
    base_path = Path(__file__).parent.parent
    input_file = base_path / args.input
    
    logger.info(f"Loading database from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        startups = json.load(f)
    logger.info(f"Loaded {len(startups)} startups")
    
    # Check LLM
    if args.use_llm:
        if is_nvidia_nim_configured():
            logger.info("✓ NVIDIA NIM configured - using DeepSeek-R1 for validation")
        elif HAS_LLM:
            logger.info("⚠ Using fallback LLM (not NVIDIA NIM)")
        else:
            logger.warning("⚠ LLM not available - using keyword-only filtering")
            args.use_llm = False
    
    # Filter
    filtered, stats = filter_agentic_b2b(
        startups,
        min_confidence=args.min_confidence,
        use_llm=args.use_llm
    )
    
    # Statistics
    if args.stats:
        print("\n" + "="*80)
        print("AGENTIC AI B2B SOLUTIONS - ANALYSIS RESULTS")
        print("="*80)
        
        # Category breakdown
        category_counts = {}
        for s in filtered:
            for cat, score in s['agentic_analysis']['category_scores'].items():
                if score > 0:
                    category_counts[cat] = category_counts.get(cat, 0) + 1
        
        print(f"\n📊 CATEGORY BREAKDOWN:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count} startups")
        
        # Top keywords
        all_keywords = []
        for s in filtered:
            all_keywords.extend(s['agentic_analysis'].get('matched_keywords', []))
        
        keyword_freq = {}
        for kw in all_keywords:
            keyword_freq[kw] = keyword_freq.get(kw, 0) + 1
        
        print(f"\n🔑 TOP 15 MATCHED KEYWORDS:")
        for kw, count in sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"  {kw}: {count}")
        
        # Top 20 startups
        print(f"\n🏆 TOP 20 AGENTIC AI B2B STARTUPS:")
        for i, s in enumerate(filtered[:20], 1):
            name = s.get('company_name', 'Unknown')
            confidence = s['agentic_analysis']['confidence']
            keywords = ', '.join(s['agentic_analysis']['matched_keywords'][:3])
            
            print(f"  {i}. {name} (Confidence: {confidence}/100)")
            print(f"     Keywords: {keywords}")
        
        print("="*80 + "\n")
    
    # Save output
    output_path = base_path / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Saved {len(filtered)} startups to {args.output}")
    
    # CSV export
    if args.csv:
        import csv
        csv_path = output_path.with_suffix('.csv')
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Company Name', 'Confidence', 'Website', 'Industry',
                'Top Keywords', 'B2B Indicators', 'Description'
            ])
            
            for s in filtered:
                writer.writerow([
                    s.get('company_name', ''),
                    s['agentic_analysis']['confidence'],
                    s.get('website', ''),
                    s.get('primary_industry', ''),
                    ', '.join(s['agentic_analysis']['matched_keywords'][:3]),
                    ', '.join(s['agentic_analysis'].get('b2b_indicators', [])[:2]),
                    s.get('shortDescription', '')[:100]
                ])
        
        logger.info(f"✓ Saved CSV summary to {csv_path.name}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
