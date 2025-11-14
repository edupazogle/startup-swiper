#!/usr/bin/env python3
"""
AXA Startup Selection Agent
----------------------------
Intelligent agent that uses MCP (Model Context Protocol) server to:
1. Query the startup database
2. Apply AXA's 5 strategic rules
3. Score and rank startups
4. Select top candidates
5. Generate selection reports

The agent combines:
- Database access via SQLAlchemy
- Keyword-based rule matching
- ML-based relevance scoring
- Interactive selection process
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sqlite3
import logging

sys.path.insert(0, str(Path(__file__).parent))
from models_startup import Startup
from sqlalchemy import create_engine, func, or_, and_
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class AxaSelectionAgent:
    """Intelligent agent for AXA startup selection"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Load rule definitions from filter script
        self.rules = self._load_rules()
        
    def _load_rules(self) -> Dict:
        """Load AXA rule definitions"""
        return {
            'rule_1': {
                'name': 'Agentic Platform Enablers',
                'description': 'For internal platform building',
                'weight': 40,
                'keywords': {
                    'primary': [
                        'observability', 'monitoring', 'tracing', 'agent orchestration',
                        'llm ops', 'mlops', 'ai ops', 'agent framework', 'multi-agent',
                        'vector database', 'embedding', 'rag', 'workflow automation',
                        'agent builder', 'model deployment', 'ai platform', 'agent testing'
                    ],
                    'secondary': [
                        'langchain', 'llm', 'agent', 'orchestration', 'infrastructure',
                        'platform', 'framework', 'sdk', 'api management', 'agent mesh'
                    ]
                }
            },
            'rule_2': {
                'name': 'Agentic Service Providers',
                'description': 'Non-insurance enterprise solutions',
                'weight': 35,
                'keywords': {
                    'primary': [
                        'marketing automation', 'sales ai', 'customer support automation',
                        'recruiting ai', 'hr automation', 'finance automation',
                        'contract intelligence', 'data analytics ai', 'conversational ai'
                    ],
                    'secondary': [
                        'automation', 'ai agent', 'intelligent assistant', 'chatbot',
                        'virtual assistant', 'rpa', 'process automation', 'workflow'
                    ]
                }
            },
            'rule_3': {
                'name': 'Insurance-Specific Solutions',
                'description': 'Claims, underwriting, policy management',
                'weight': 35,
                'keywords': {
                    'primary': [
                        'insurance', 'insurtech', 'claims', 'underwriting', 'policy',
                        'actuarial', 'reinsurance', 'fraud detection insurance',
                        'insurance platform', 'claims automation', 'underwriting automation'
                    ],
                    'secondary': [
                        'claim', 'policyholder', 'premium', 'coverage', 'fnol',
                        'loss adjusting', 'insurance distribution', 'carrier'
                    ]
                }
            },
            'rule_4': {
                'name': 'Health Innovations',
                'description': 'Insurance-applicable health solutions',
                'weight': 30,
                'keywords': {
                    'primary': [
                        'health analytics', 'medical ai', 'telemedicine', 'digital health',
                        'healthtech', 'wellness platform', 'remote monitoring',
                        'preventive health', 'population health', 'digital therapeutics'
                    ],
                    'secondary': [
                        'health', 'healthcare', 'medical', 'wellness', 'wearable',
                        'telehealth', 'patient', 'clinical', 'health insurance'
                    ]
                }
            },
            'rule_5': {
                'name': 'Development & Legacy Modernization',
                'description': 'Code, QA, migration tools',
                'weight': 35,
                'keywords': {
                    'primary': [
                        'code generation', 'ai coding', 'test automation', 'qa automation',
                        'legacy modernization', 'cobol migration', 'mainframe modernization',
                        'code migration', 'devops automation', 'ci/cd', 'automated testing'
                    ],
                    'secondary': [
                        'developer', 'software development', 'programming', 'code',
                        'testing', 'quality assurance', 'legacy', 'migration',
                        'copilot', 'code assistant'
                    ]
                }
            }
        }
    
    def query_startups(self, 
                      countries: Optional[List[str]] = None,
                      industries: Optional[List[str]] = None,
                      enriched_only: bool = True,
                      min_score: int = 0) -> List[Startup]:
        """Query startups from database with filters"""
        
        query = self.session.query(Startup)
        
        if enriched_only:
            query = query.filter(Startup.is_enriched == True)
        
        if countries:
            query = query.filter(Startup.company_country.in_(countries))
        
        if industries:
            query = query.filter(Startup.primary_industry.in_(industries))
        
        return query.all()
    
    def match_rule(self, startup: Startup, rule_id: str) -> Tuple[bool, int, List[str]]:
        """Check if startup matches a specific rule"""
        rule = self.rules[rule_id]
        
        # Build search text
        search_text = f"{startup.company_description or ''} {startup.shortDescription or ''}".lower()
        
        # Count matches
        primary_matches = sum(1 for kw in rule['keywords']['primary'] if kw.lower() in search_text)
        secondary_matches = sum(1 for kw in rule['keywords']['secondary'] if kw.lower() in search_text)
        
        # Determine if matches
        matches = primary_matches >= 1 or secondary_matches >= 2
        
        # Calculate confidence
        confidence = min(100, (primary_matches * 30) + (secondary_matches * 10))
        
        # Get matched keywords
        matched_kw = [kw for kw in rule['keywords']['primary'] if kw.lower() in search_text][:5]
        
        return matches, confidence, matched_kw
    
    def score_startup(self, startup: Startup) -> Dict:
        """Score a startup against all AXA rules"""
        
        rule_scores = {}
        matched_rules = []
        max_rule_score = 0
        
        # Check each rule
        for rule_id, rule in self.rules.items():
            matches, confidence, keywords = self.match_rule(startup, rule_id)
            if matches:
                score = int(rule['weight'] * (confidence / 100))
                rule_scores[rule['name']] = {
                    'score': score,
                    'confidence': confidence,
                    'keywords': keywords
                }
                matched_rules.append(rule['name'])
                max_rule_score = max(max_rule_score, score)
        
        # Multi-rule bonus
        multi_rule_bonus = 10 if len(matched_rules) > 1 else 0
        
        # Additional factors
        traction_score = self._score_traction(startup)
        innovation_score = self._score_innovation(startup)
        stage_score = self._score_stage(startup)
        geo_score = self._score_geography(startup)
        data_quality_score = 5 if startup.is_enriched else 2
        
        total_score = (max_rule_score + multi_rule_bonus + traction_score + 
                      innovation_score + stage_score + geo_score + data_quality_score)
        
        # Determine tier
        if total_score >= 80:
            tier = 'Tier 1: Must Meet'
        elif total_score >= 60:
            tier = 'Tier 2: High Priority'
        elif total_score >= 40:
            tier = 'Tier 3: Medium Priority'
        else:
            tier = 'Tier 4: Low Priority'
        
        return {
            'total_score': total_score,
            'tier': tier,
            'matched_rules': matched_rules,
            'rule_scores': rule_scores,
            'breakdown': {
                'max_rule_score': max_rule_score,
                'multi_rule_bonus': multi_rule_bonus,
                'traction': traction_score,
                'innovation': innovation_score,
                'stage': stage_score,
                'geography': geo_score,
                'data_quality': data_quality_score
            }
        }
    
    def _score_traction(self, startup: Startup) -> int:
        """Score based on corporate traction indicators"""
        text = f"{startup.company_description or ''} {startup.shortDescription or ''}".lower()
        indicators = ['fortune 500', 'enterprise', 'global companies', 'trusted by']
        count = sum(1 for ind in indicators if ind in text)
        
        if count >= 3: return 25
        elif count >= 2: return 20
        elif count >= 1: return 15
        else: return 5
    
    def _score_innovation(self, startup: Startup) -> int:
        """Score based on innovation indicators"""
        text = f"{startup.company_description or ''} {startup.shortDescription or ''}".lower()
        keywords = ['ai', 'automation', 'machine learning', 'innovative', 'patent']
        count = sum(1 for kw in keywords if kw in text)
        
        if count >= 4: return 15
        elif count >= 2: return 10
        elif count >= 1: return 5
        else: return 2
    
    def _score_stage(self, startup: Startup) -> int:
        """Score based on company maturity"""
        maturity = str(startup.maturity or '').lower()
        if 'scaleup' in maturity: return 10
        elif 'startup' in maturity: return 8
        else: return 5
    
    def _score_geography(self, startup: Startup) -> int:
        """Score based on geographic location"""
        country = str(startup.company_country or '').upper()
        eu_countries = ['FI', 'DE', 'FR', 'GB', 'SE', 'NL', 'BE', 'CH', 'NO', 'DK', 'IE']
        if country in eu_countries: return 5
        elif country in ['US', 'CA']: return 2
        else: return 0
    
    def select_top_startups(self, 
                           min_tier: int = 2,
                           top_n: Optional[int] = None,
                           by_rule: Optional[str] = None) -> List[Tuple[Startup, Dict]]:
        """Select top startups based on criteria"""
        
        logger.info("🔍 Querying database...")
        startups = self.query_startups(enriched_only=True)
        logger.info(f"Found {len(startups)} enriched startups")
        
        logger.info("📊 Scoring startups...")
        scored_startups = []
        for startup in startups:
            score_data = self.score_startup(startup)
            
            # Apply filters
            tier_num = int(score_data['tier'].split(':')[0].replace('Tier ', ''))
            if tier_num > min_tier:
                continue
            
            if by_rule and by_rule not in score_data['matched_rules']:
                continue
            
            scored_startups.append((startup, score_data))
        
        # Sort by score
        scored_startups.sort(key=lambda x: x[1]['total_score'], reverse=True)
        
        # Limit if requested
        if top_n:
            scored_startups = scored_startups[:top_n]
        
        logger.info(f"✓ Selected {len(scored_startups)} startups")
        return scored_startups
    
    def generate_report(self, selections: List[Tuple[Startup, Dict]], 
                       output_path: str):
        """Generate selection report"""
        
        report_data = {
            'generated_at': datetime.utcnow().isoformat(),
            'total_selected': len(selections),
            'selections': []
        }
        
        for startup, score_data in selections:
            # Get enrichment data
            enrichment = {}
            if startup.enrichment:
                if isinstance(startup.enrichment, str):
                    enrichment = json.loads(startup.enrichment)
                else:
                    enrichment = startup.enrichment
            
            report_data['selections'].append({
                'startup': {
                    'id': startup.id,
                    'name': startup.company_name,
                    'country': startup.company_country,
                    'city': startup.company_city,
                    'industry': startup.primary_industry,
                    'website': startup.website,
                    'description': startup.shortDescription or startup.company_description,
                    'employees': startup.employees,
                    'funding': startup.totalFunding,
                    'maturity': startup.maturity,
                    'logo_url': startup.logoUrl,
                },
                'scoring': score_data,
                'contact': {
                    'emails': enrichment.get('emails', []),
                    'phones': enrichment.get('phone_numbers', []),
                    'social_media': enrichment.get('social_media', {}),
                },
                'tech_stack': enrichment.get('tech_stack', [])
            })
        
        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Report saved to {output_path}")
        
        return report_data
    
    def print_summary(self, selections: List[Tuple[Startup, Dict]]):
        """Print selection summary"""
        
        print("\n" + "="*80)
        print("🎯 AXA STARTUP SELECTION SUMMARY")
        print("="*80)
        
        # Tier breakdown
        tier_counts = {}
        for _, score in selections:
            tier = score['tier']
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        print(f"\n📊 TIER BREAKDOWN:")
        for tier in ['Tier 1: Must Meet', 'Tier 2: High Priority', 'Tier 3: Medium Priority']:
            count = tier_counts.get(tier, 0)
            if count > 0:
                print(f"  {tier:30} {count:4} startups")
        
        # Rule breakdown
        rule_counts = {}
        for _, score in selections:
            for rule in score['matched_rules']:
                rule_counts[rule] = rule_counts.get(rule, 0) + 1
        
        print(f"\n📋 RULE MATCHES:")
        for rule in sorted(rule_counts.keys()):
            count = rule_counts[rule]
            print(f"  {rule:40} {count:4} startups")
        
        # Top 10
        print(f"\n🏆 TOP 10 SELECTED STARTUPS:")
        for i, (startup, score) in enumerate(selections[:10], 1):
            rules = ', '.join([r.split(':')[0].replace('Rule ', 'R') for r in score['matched_rules']])
            print(f"  {i:2}. {startup.company_name:30} "
                  f"Score: {score['total_score']:3} | "
                  f"{score['tier']:25} | "
                  f"Rules: {rules}")
        
        print("\n" + "="*80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='AXA Startup Selection Agent'
    )
    parser.add_argument('--db', default='startup_swiper.db',
                       help='Database path')
    parser.add_argument('--min-tier', type=int, default=2,
                       help='Minimum tier (1=Must Meet, 2=High Priority, 3=Medium)')
    parser.add_argument('--top-n', type=int,
                       help='Limit to top N startups')
    parser.add_argument('--rule', 
                       choices=['rule_1', 'rule_2', 'rule_3', 'rule_4', 'rule_5'],
                       help='Filter by specific rule')
    parser.add_argument('--output', '-o', default='axa_selection_report.json',
                       help='Output report path')
    parser.add_argument('--summary', action='store_true',
                       help='Print summary to console')
    
    args = parser.parse_args()
    
    # Initialize agent
    base_path = Path(__file__).parent.parent
    db_path = base_path / args.db
    
    logger.info("🤖 Starting AXA Selection Agent...")
    agent = AxaSelectionAgent(str(db_path))
    
    # Select startups
    rule_name = None
    if args.rule:
        rule_name = agent.rules[args.rule]['name']
        logger.info(f"Filtering by: {rule_name}")
    
    selections = agent.select_top_startups(
        min_tier=args.min_tier,
        top_n=args.top_n,
        by_rule=rule_name
    )
    
    # Generate report
    output_path = base_path / args.output
    report = agent.generate_report(selections, str(output_path))
    
    # Print summary
    if args.summary or not args.output:
        agent.print_summary(selections)
    
    logger.info(f"\n✅ Selection complete! {len(selections)} startups selected")
    logger.info(f"📄 Report: {output_path}")


if __name__ == '__main__':
    main()
