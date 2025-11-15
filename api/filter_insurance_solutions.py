#!/usr/bin/env python3
"""
Insurance Solutions Startup Filter
Finds startups in: Contact Center AI, Underwriting, Claims, Insurance Tech, Agentic Coding
"""

import json
import logging
import argparse
from typing import Dict, List, Optional
from datetime import datetime
import os
from pathlib import Path

# LLM Integration
from litellm import completion

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class InsuranceSolutionFilter:
    """Filter startups by insurance solution categories"""
    
    CATEGORY_KEYWORDS = {
        'contact_center_ai': {
            'primary': [
                'contact center', 'call center', 'customer service', 'conversational ai',
                'voice ai', 'speech analytics', 'virtual agent', 'chatbot',
                'customer support', 'voice bot', 'call analytics',
                'sentiment analysis', 'speech recognition', 'customer interaction'
            ],
            'secondary': [
                'omnichannel', 'customer engagement', 'live chat', 'messaging',
                'customer experience', 'cx', 'support automation', 'service desk',
                'help desk', 'agent assist', 'conversation intelligence'
            ],
            'weight': 1.2
        },
        'underwriting_ai': {
            'primary': [
                'underwriting', 'risk assessment', 'risk scoring', 'risk modeling',
                'insurance pricing', 'actuarial', 'policy pricing', 'risk analytics',
                'fraud detection', 'risk prediction', 'policy automation',
                'insurance decisioning', 'risk intelligence', 'credit risk'
            ],
            'secondary': [
                'insurance data', 'policy management', 'insurance analytics',
                'predictive modeling', 'credit scoring', 'risk management',
                'kyc', 'aml', 'compliance', 'identity verification'
            ],
            'weight': 1.8
        },
        'claims_processing': {
            'primary': [
                'claims', 'claims processing', 'claims management', 'claims automation',
                'claims adjudication', 'claims analytics', 'first notice of loss',
                'fnol', 'claims handling', 'loss adjustment',
                'damage assessment', 'claims fraud', 'stp'
            ],
            'secondary': [
                'insurance workflow', 'document processing', 'ocr',
                'insurance automation', 'policy servicing', 'incident management',
                'loss prevention', 'repair estimation'
            ],
            'weight': 1.8
        },
        'insurtech_platform': {
            'primary': [
                'insurtech', 'insurance platform', 'insurance software', 'insurance saas',
                'digital insurance', 'insurance api', 'insurance infrastructure',
                'insurance technology', 'insurance core system', 'policy administration',
                'insurance distribution', 'insurance marketplace', 'embedded insurance'
            ],
            'secondary': [
                'insurance broker', 'insurance agent', 'insurance portal',
                'insurance comparison', 'insurance quote'
            ],
            'weight': 1.3
        },
        'agentic_coding': {
            'primary': [
                'ai coding', 'code generation', 'coding assistant',
                'code completion', 'pair programming', 'autonomous coding',
                'code agent', 'software development ai', 'copilot',
                'automated coding', 'code synthesis',
                'code intelligence', 'code automation', 'ai code'
            ],
            'secondary': [
                'developer tools', 'ide', 'code review', 'code quality',
                'code analysis', 'software engineering', 'devops ai',
                'test generation', 'code refactoring', 'debugging assistant'
            ],
            'weight': 1.0
        },
        'document_intelligence': {
            'primary': [
                'document ai', 'document processing', 'document extraction',
                'ocr', 'intelligent document processing', 'idp', 'document automation',
                'document understanding', 'form extraction', 'document classification'
            ],
            'secondary': [
                'data extraction', 'document management', 'scanning', 'digitization'
            ],
            'weight': 1.0
        }
    }
    
    INDUSTRY_SIGNALS = [
        'insurance', 'insurtech', 'financial services', 'fintech',
        'healthcare', 'healthtech', 'banking', 'risk management'
    ]
    
    TIERS = {
        4: {'min': 60, 'label': 'Core Insurance Solution'},
        3: {'min': 45, 'label': 'Strong Insurance Fit'},
        2: {'min': 30, 'label': 'Relevant Insurance Tech'},
        1: {'min': 15, 'label': 'Potential Insurance Application'}
    }
    
    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        if use_llm:
            api_key = os.getenv('NVIDIA_API_KEY')
            if not api_key:
                raise ValueError("NVIDIA_API_KEY not set")
            os.environ['NVIDIA_API_KEY'] = api_key
    
    def score_startup(self, startup: Dict) -> Dict:
        """Calculate insurance solution score"""
        
        score_data = {
            'total_score': 0,
            'category_scores': {},
            'matched_keywords': {},
            'categories': [],
            'tier': None,
            'tier_label': None,
            'reasoning': []
        }
        
        # Prepare text for analysis
        text_fields = [
            startup.get('company_name', ''),
            startup.get('short_description', ''),
            startup.get('long_description', ''),
            ' '.join(startup.get('industries', [])),
            ' '.join(startup.get('tags', []))
        ]
        combined_text = ' '.join(text_fields).lower()
        
        # Score each category
        for category, config in self.CATEGORY_KEYWORDS.items():
            cat_score = 0
            matched = []
            
            # Primary keywords
            for kw in config['primary']:
                if kw.lower() in combined_text:
                    cat_score += 8 * config['weight']
                    matched.append(kw)
            
            # Secondary keywords
            for kw in config['secondary']:
                if kw.lower() in combined_text:
                    cat_score += 2.5 * config['weight']
                    matched.append(kw)
            
            if cat_score > 0:
                score_data['category_scores'][category] = round(cat_score, 1)
                score_data['matched_keywords'][category] = matched[:3]
                score_data['categories'].append(category)
            
            score_data['total_score'] += cat_score
        
        # Industry bonus
        for industry_signal in self.INDUSTRY_SIGNALS:
            if industry_signal in combined_text:
                score_data['total_score'] += 5
                score_data['reasoning'].append(f"Industry match: {industry_signal}")
        
        # Technology signals
        tech_signals = ['ai', 'machine learning', 'artificial intelligence', 'automation', 'nlp', 'computer vision']
        tech_count = sum(1 for sig in tech_signals if sig in combined_text)
        if tech_count >= 2:
            score_data['total_score'] += 10
            score_data['reasoning'].append(f"Strong AI/ML signals ({tech_count} found)")
        
        # Round total score
        score_data['total_score'] = round(score_data['total_score'], 1)
        
        # Assign tier
        for tier_num, tier_info in sorted(self.TIERS.items(), reverse=True):
            if score_data['total_score'] >= tier_info['min']:
                score_data['tier'] = tier_num
                score_data['tier_label'] = tier_info['label']
                break
        
        return score_data
    
    def llm_validate(self, startup: Dict, score_data: Dict) -> Optional[Dict]:
        """Validate with LLM for high-scoring startups"""
        
        if score_data['total_score'] < 40:
            return None
        
        try:
            prompt = f"""Analyze this startup for insurance industry solutions:

Company: {startup.get('company_name')}
Description: {startup.get('short_description', '')} {startup.get('long_description', '')}
Industries: {', '.join(startup.get('industries', []))}
Categories Found: {', '.join(score_data['categories'])}

Evaluate if this startup provides solutions for:
1. Contact Center AI / Customer Service
2. Underwriting / Risk Assessment
3. Claims Processing / Management
4. InsurTech Platform / Infrastructure
5. Agentic Coding / Developer Tools

Respond in JSON format:
{{
    "is_relevant": true/false,
    "primary_category": "category name",
    "relevance_score": 1-100,
    "key_capabilities": ["cap1", "cap2"],
    "insurance_fit": "brief explanation",
    "axa_value": "specific value for AXA"
}}"""
            
            response = completion(
                model="nvidia/llama-3.1-nemotron-70b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            llm_result = json.loads(content)
            
            if llm_result.get('is_relevant'):
                return llm_result
            
        except Exception as e:
            logger.warning(f"LLM validation failed for {startup.get('company_name')}: {e}")
        
        return None
    
    def filter_startups(self, startups: List[Dict], min_score: float = 25) -> List[Dict]:
        """Filter and score all startups"""
        
        results = []
        stats = {
            'total': len(startups),
            'with_signals': 0,
            'passed_filter': 0,
            'llm_validated': 0,
            'by_category': {},
            'by_tier': {}
        }
        
        logger.info(f"Filtering {len(startups)} startups for insurance solutions...")
        
        for idx, startup in enumerate(startups):
            if idx > 0 and idx % 500 == 0:
                logger.info(f"  Processed {idx}/{len(startups)} startups ({stats['passed_filter']} matches so far)")
            
            score_data = self.score_startup(startup)
            
            if score_data['total_score'] > 0:
                stats['with_signals'] += 1
            
            if score_data['total_score'] >= min_score:
                # LLM validation for high scores
                llm_validation = None
                if self.use_llm and score_data['total_score'] >= 40:
                    llm_validation = self.llm_validate(startup, score_data)
                    if llm_validation:
                        stats['llm_validated'] += 1
                        # Boost score with LLM confidence
                        score_data['total_score'] = min(100, score_data['total_score'] + llm_validation['relevance_score'] * 0.2)
                        score_data['llm_validation'] = llm_validation
                
                startup['insurance_scoring'] = score_data
                results.append(startup)
                stats['passed_filter'] += 1
                
                # Track categories
                for cat in score_data['categories']:
                    stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1
                
                # Track tier
                if score_data['tier']:
                    stats['by_tier'][score_data['tier']] = stats['by_tier'].get(score_data['tier'], 0) + 1
        
        # Sort by score
        results.sort(key=lambda x: x['insurance_scoring']['total_score'], reverse=True)
        
        logger.info(f"✓ Filtered to {len(results)} insurance solution startups")
        
        return results, stats


def print_statistics(stats: Dict, results: List[Dict]):
    """Print detailed statistics"""
    
    print("\n" + "="*80)
    print("INSURANCE SOLUTIONS FILTERING RESULTS")
    print("="*80)
    
    print(f"\n📊 OVERVIEW:")
    print(f"  Total startups: {stats['total']}")
    print(f"  With insurance signals: {stats['with_signals']} ({stats['with_signals']/stats['total']*100:.1f}%)")
    print(f"  Passed filter: {stats['passed_filter']} ({stats['passed_filter']/stats['total']*100:.1f}%)")
    if stats.get('llm_validated'):
        print(f"  LLM validated: {stats['llm_validated']}")
    print(f"  Excluded (no signals): {stats['total'] - stats['with_signals']}")
    print(f"  Excluded (low score): {stats['with_signals'] - stats['passed_filter']}")
    
    if stats['by_tier']:
        print(f"\n🎯 TIER DISTRIBUTION:")
        for tier in sorted(stats['by_tier'].keys(), reverse=True):
            tier_info = InsuranceSolutionFilter.TIERS[tier]
            print(f"  Tier {tier}: {tier_info['label']}: {stats['by_tier'][tier]}")
    
    if stats['by_category']:
        print(f"\n🏢 CATEGORY DISTRIBUTION:")
        for cat, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
    
    print(f"\n🏆 TOP 20 INSURANCE SOLUTION STARTUPS:")
    for idx, startup in enumerate(results[:20], 1):
        scoring = startup['insurance_scoring']
        name = startup['company_name']
        score = scoring['total_score']
        funding = startup.get('total_funding', 'Undisclosed')
        employees = startup.get('employee_count', 'Size unknown')
        categories = ', '.join(scoring['categories'][:3])
        
        print(f"  {idx}. {name}")
        print(f"     Score: {score}/100 | ${funding} | {employees} emp")
        print(f"     Categories: {categories}")
        
        if scoring.get('llm_validation'):
            llm_val = scoring['llm_validation']
            print(f"     LLM: {llm_val.get('insurance_fit', '')[:60]}")
    
    print("="*80)


def main():
    parser = argparse.ArgumentParser(description='Filter startups by insurance solutions')
    parser.add_argument('--input', required=True, help='Input JSON file')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--min-score', type=float, default=25, help='Minimum score (default: 25)')
    parser.add_argument('--use-llm', action='store_true', help='Use LLM validation')
    parser.add_argument('--stats', action='store_true', help='Print detailed statistics')
    
    args = parser.parse_args()
    
    # Load startups
    logger.info(f"Loading startups from {args.input}...")
    with open(args.input, 'r') as f:
        startups = json.load(f)
    
    # Filter
    filter_engine = InsuranceSolutionFilter(use_llm=args.use_llm)
    results, stats = filter_engine.filter_startups(startups, min_score=args.min_score)
    
    # Save results
    logger.info(f"Saving {len(results)} startups to {args.output}...")
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print stats
    if args.stats:
        print_statistics(stats, results)
    
    logger.info("✓ Done!")


if __name__ == '__main__':
    main()
