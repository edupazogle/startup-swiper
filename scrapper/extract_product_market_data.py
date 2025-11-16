#!/usr/bin/env python3
"""
Extract Structured Product, Market & Competition Data from Startup Descriptions

Extracts:
- Product/Service Description
- Target Market (Current)
- Future Markets
- Technologies Used
- Competitive Landscape
- Unique Value Proposition
"""

import sqlite3
import json
import logging
from typing import Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataExtractor:
    """Extracts structured data from startup descriptions using pattern matching and NLP"""
    
    def __init__(self):
        self.db_path = 'startup_swiper.db'
    
    def extract_from_descriptions(self, startup_id: int, company_name: str, 
                                 company_desc: str, full_desc: str, 
                                 scraped_desc: str = None) -> Dict:
        """
        Extract structured data from multiple description fields
        
        Args:
            startup_id: ID in database
            company_name: Company name
            company_desc: Company's own description (99.9% complete)
            full_desc: Full description from CSV (95.4% complete)
            scraped_desc: Newly scraped from Slush (being added)
        
        Returns:
            Dictionary with extracted fields
        """
        
        # Combine all available descriptions
        all_text = f"{company_name}. {company_desc or ''} {full_desc or ''} {scraped_desc or ''}".lower()
        
        extracted = {
            'id': startup_id,
            'company_name': company_name,
            'extraction_date': datetime.now().isoformat(),
            'product_description': self._extract_product(company_desc, full_desc),
            'current_market': self._extract_current_market(all_text),
            'future_market': self._extract_future_market(all_text),
            'technologies': self._extract_technologies(all_text),
            'competitors': self._extract_competitors(all_text),
            'unique_value': self._extract_value_prop(all_text),
            'business_model': self._extract_business_model(all_text),
        }
        
        return extracted
    
    def _extract_product(self, company_desc: str, full_desc: str) -> Optional[str]:
        """Extract product/service description"""
        # Prefer the more detailed description
        if full_desc and len(full_desc) > len(company_desc or ''):
            return full_desc[:500]
        return company_desc[:500] if company_desc else None
    
    def _extract_current_market(self, text: str) -> Optional[Dict]:
        """Extract current target market information"""
        market = {
            'segments': [],
            'geographies': [],
            'customer_types': []
        }
        
        # Market segments
        segment_keywords = {
            'enterprise': ['enterprise', 'b2b', 'business', 'corporate', 'companies'],
            'consumer': ['consumer', 'b2c', 'individual', 'user', 'customer'],
            'saas': ['saas', 'software as a service', 'cloud'],
            'healthcare': ['healthcare', 'medical', 'clinical', 'patient', 'hospital'],
            'fintech': ['fintech', 'financial', 'payment', 'banking', 'crypto'],
            'ecommerce': ['ecommerce', 'retail', 'shopping', 'marketplace'],
            'education': ['education', 'edtech', 'learning', 'student', 'school'],
            'ai': ['ai', 'machine learning', 'ml', 'automation', 'analytics'],
            'iot': ['iot', 'internet of things', 'sensor', 'connected'],
            'gaming': ['game', 'gaming', 'player', 'entertainment'],
        }
        
        for segment, keywords in segment_keywords.items():
            if any(kw in text for kw in keywords):
                market['segments'].append(segment)
        
        # Geographies
        geo_keywords = {
            'global': ['global', 'worldwide', 'international', 'all countries'],
            'north_america': ['north america', 'usa', 'canada', 'us', 'america'],
            'europe': ['europe', 'european', 'eu', 'uk', 'germany', 'france'],
            'asia': ['asia', 'asian', 'china', 'india', 'japan', 'southeast'],
        }
        
        for geo, keywords in geo_keywords.items():
            if any(kw in text for kw in keywords):
                market['geographies'].append(geo)
        
        # Customer types
        customer_keywords = {
            'startups': ['startup', 'sme', 'small business'],
            'enterprises': ['enterprise', 'large enterprise', 'corporation'],
            'developers': ['developer', 'programmer', 'engineer', 'technical'],
            'non_technical': ['non-technical', 'business user', 'manager'],
        }
        
        for ctype, keywords in customer_keywords.items():
            if any(kw in text for kw in keywords):
                market['customer_types'].append(ctype)
        
        return market if any([len(v) > 0 for v in market.values()]) else None
    
    def _extract_future_market(self, text: str) -> Optional[Dict]:
        """Extract information about expansion plans"""
        future = {
            'expansion_plans': [],
            'new_geographies': [],
            'new_segments': []
        }
        
        # Look for expansion keywords
        if any(word in text for word in ['expand', 'plan to', 'will', 'upcoming', 'roadmap', 'future']):
            future['expansion_plans'].append('planned')
        
        if any(word in text for word in ['asia', 'europe', 'africa', 'middle east']) and 'expand' in text:
            future['new_geographies'].append('emerging_markets')
        
        return future if any([len(v) > 0 for v in future.values()]) else None
    
    def _extract_technologies(self, text: str) -> Optional[list]:
        """Extract technology stack"""
        tech_keywords = [
            'ai', 'machine learning', 'ml', 'deep learning', 'nlp', 'computer vision',
            'blockchain', 'crypto', 'web3', 'defi',
            'iot', 'edge computing', 'sensor',
            'ar', 'vr', 'metaverse', 'xr',
            'cloud', 'aws', 'azure', 'gcp',
            'mobile', 'ios', 'android', 'react', 'flutter',
            'python', 'javascript', 'node.js', 'java', 'golang',
            'kubernetes', 'docker', 'devops',
            'database', 'postgresql', 'mongodb', 'redis',
            'saas', 'api', 'rest', 'graphql',
            '5g', 'quantum', 'wasm'
        ]
        
        found_tech = [tech for tech in tech_keywords if tech in text]
        return list(set(found_tech)) if found_tech else None
    
    def _extract_competitors(self, text: str) -> Optional[Dict]:
        """Extract competitive information"""
        competitors = {
            'mentioned_competitors': [],
            'competitive_advantages': [],
            'market_position': None
        }
        
        # Known competitor names (this is a starting list)
        known_competitors = {
            'stripe': ['stripe'],
            'aws': ['aws', 'amazon web services'],
            'google': ['google cloud', 'gcp'],
            'microsoft': ['azure', 'microsoft'],
            'salesforce': ['salesforce'],
            'slack': ['slack'],
            'notion': ['notion'],
            'figma': ['figma'],
            'github': ['github'],
            'gitlab': ['gitlab'],
            'jira': ['jira'],
            'datadog': ['datadog'],
            'databricks': ['databricks'],
            'hugging face': ['hugging face'],
            'openai': ['openai', 'chatgpt'],
            'anthropic': ['claude', 'anthropic'],
        }
        
        for competitor, names in known_competitors.items():
            if any(name in text for name in names):
                competitors['mentioned_competitors'].append(competitor)
        
        # Competitive advantages
        advantage_keywords = {
            'superior_performance': ['faster', 'speed', 'low latency', 'high performance'],
            'cost_effective': ['cheaper', 'cost', 'affordable', 'budget'],
            'ease_of_use': ['simple', 'easy', 'user-friendly', 'intuitive', 'no-code'],
            'innovation': ['innovative', 'breakthrough', 'patent', 'proprietary'],
            'security': ['secure', 'encryption', 'privacy', 'compliance'],
            'integration': ['integrate', 'api', 'plugin', 'seamless'],
            'customization': ['customize', 'flexible', 'scalable', 'modular'],
        }
        
        for advantage, keywords in advantage_keywords.items():
            if any(kw in text for kw in keywords):
                competitors['competitive_advantages'].append(advantage)
        
        # Market position
        if 'market leader' in text or 'leading' in text:
            competitors['market_position'] = 'leader'
        elif 'alternative' in text or 'replacement' in text:
            competitors['market_position'] = 'challenger'
        elif 'niche' in text:
            competitors['market_position'] = 'niche'
        
        return competitors if any([len(v) > 0 if isinstance(v, list) else v for v in competitors.values()]) else None
    
    def _extract_value_prop(self, text: str) -> Optional[str]:
        """Extract unique value proposition"""
        # Look for distinctive language
        value_phrases = [
            'unlike', 'unlike other', 'different from',
            'the only', 'first to',
            'patented', 'proprietary',
            'revolutionary', 'breakthrough',
            'unique', 'distinctive'
        ]
        
        if any(phrase in text for phrase in value_phrases):
            return 'distinctive'
        return None
    
    def _extract_business_model(self, text: str) -> Optional[str]:
        """Extract business model"""
        models = {
            'saas': ['saas', 'subscription', 'monthly fee', 'per user'],
            'marketplace': ['marketplace', 'commission', 'transaction fee'],
            'freemium': ['free plan', 'freemium', 'premium tier'],
            'licensing': ['license', 'license fee', 'licensed'],
            'open_source': ['open source', 'github', 'apache', 'mit'],
            'consulting': ['consulting', 'services', 'implementation'],
            'hardware': ['hardware', 'device', 'sensor'],
            'data': ['data', 'analytics', 'insights'],
        }
        
        for model, keywords in models.items():
            if any(kw in text for kw in keywords):
                return model
        
        return None
    
    def run(self, limit: int = 100):
        """
        Extract data from all startups in database
        
        Args:
            limit: Number of startups to process
        """
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        logger.info("="*70)
        logger.info("STRUCTURED DATA EXTRACTION")
        logger.info("="*70)
        logger.info(f"Extracting product/market/competition data from {limit} startups...")
        
        # Get startups with descriptions
        cursor.execute(f"""
            SELECT id, company_name, company_description, description, scraped_description
            FROM startups
            WHERE company_description IS NOT NULL OR description IS NOT NULL
            LIMIT {limit}
        """)
        
        startups = cursor.fetchall()
        logger.info(f"Found {len(startups)} startups with descriptions\n")
        
        extracted_count = 0
        
        for startup_id, company_name, company_desc, full_desc, scraped_desc in startups:
            try:
                # Extract structured data
                extracted = self.extract_from_descriptions(
                    startup_id, company_name, 
                    company_desc, full_desc, scraped_desc
                )
                
                # Save to database
                cursor.execute("""
                    UPDATE startups 
                    SET extracted_product = ?,
                        extracted_market = ?,
                        extracted_technologies = ?,
                        extracted_competitors = ?,
                        extracted_at = ?
                    WHERE id = ?
                """, (
                    extracted['product_description'],
                    json.dumps(extracted['current_market']),
                    json.dumps(extracted['technologies']),
                    json.dumps(extracted['competitors']),
                    extracted['extraction_date'],
                    startup_id
                ))
                
                extracted_count += 1
                
                # Log sample
                if extracted_count <= 3:
                    logger.info(f"\n[{startup_id}] {company_name}")
                    logger.info(f"  Product: {extracted['product_description'][:100]}...")
                    logger.info(f"  Market: {extracted['current_market']}")
                    logger.info(f"  Tech: {extracted['technologies']}")
                    logger.info(f"  Competitors: {extracted['competitors']}")
                
                # Commit every 50 records
                if extracted_count % 50 == 0:
                    conn.commit()
                    logger.info(f"✅ Processed {extracted_count} startups...")
                
            except Exception as e:
                logger.error(f"Error processing {company_name}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info("\n" + "="*70)
        logger.info(f"✅ EXTRACTION COMPLETE")
        logger.info("="*70)
        logger.info(f"Successfully extracted: {extracted_count}/{len(startups)}")
        logger.info(f"Fields: product, market, technologies, competitors, value prop, business model")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract structured startup data')
    parser.add_argument('--limit', type=int, default=100, help='Number of startups to process')
    
    args = parser.parse_args()
    
    extractor = DataExtractor()
    extractor.run(limit=args.limit)


if __name__ == '__main__':
    main()
