#!/usr/bin/env python3
"""
Startup Data Enrichment Script
Scrapes additional information from company websites and online sources
"""

import json
import time
import re
import requests
from urllib.parse import urlparse, urljoin
from datetime import datetime
from typing import Dict, List, Optional
import logging

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing BeautifulSoup...")
    import subprocess
    subprocess.check_call(['pip3', 'install', 'beautifulsoup4', 'lxml'])
    from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class StartupEnricher:
    def __init__(self, timeout=10, delay=2):
        self.timeout = timeout
        self.delay = delay  # Delay between requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def fetch_url(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a URL"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {str(e)}")
            return None
    
    def extract_emails(self, soup: BeautifulSoup) -> List[str]:
        """Extract email addresses from page"""
        emails = set()
        text = soup.get_text()
        
        # Find emails with regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        found_emails = re.findall(email_pattern, text)
        
        # Also check mailto links
        for link in soup.find_all('a', href=True):
            if link['href'].startswith('mailto:'):
                email = link['href'].replace('mailto:', '').split('?')[0]
                found_emails.append(email)
        
        # Filter out common non-useful emails
        exclude = ['example.com', 'test.com', 'domain.com']
        for email in found_emails:
            if not any(ex in email.lower() for ex in exclude):
                emails.add(email)
        
        return list(emails)
    
    def extract_social_media(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Extract social media links"""
        social = {}
        
        patterns = {
            'linkedin': r'linkedin\.com/(company|in)/[\w-]+',
            'twitter': r'twitter\.com/[\w-]+',
            'facebook': r'facebook\.com/[\w.-]+',
            'instagram': r'instagram\.com/[\w.-]+',
            'youtube': r'youtube\.com/(c/|channel/|user/)[\w-]+',
            'github': r'github\.com/[\w-]+',
            'medium': r'medium\.com/@?[\w-]+',
        }
        
        # Check all links
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            for platform, pattern in patterns.items():
                if platform not in social and re.search(pattern, href):
                    # Get full URL
                    full_url = urljoin(base_url, link['href'])
                    social[platform] = full_url
        
        return social
    
    def extract_phone_numbers(self, soup: BeautifulSoup) -> List[str]:
        """Extract phone numbers"""
        phones = set()
        text = soup.get_text()
        
        # Various phone patterns
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',
        ]
        
        for pattern in patterns:
            found = re.findall(pattern, text)
            phones.update(found)
        
        # Clean and filter
        valid_phones = []
        for phone in phones:
            # Remove spaces and formatting
            clean = re.sub(r'[^\d+]', '', phone)
            if len(clean) >= 10:  # Minimum length for valid phone
                valid_phones.append(phone.strip())
        
        return valid_phones[:5]  # Limit to 5 most likely
    
    def extract_company_info(self, soup: BeautifulSoup) -> Dict:
        """Extract general company information"""
        info = {}
        
        # Try to find common sections
        about_keywords = ['about', 'company', 'who we are', 'our story']
        team_keywords = ['team', 'founders', 'leadership', 'people']
        contact_keywords = ['contact', 'reach us', 'get in touch']
        
        # Look for these sections
        for keyword in about_keywords:
            section = soup.find(['div', 'section'], class_=lambda x: x and keyword in x.lower())
            if section and 'about_text' not in info:
                info['about_text'] = section.get_text(strip=True)[:500]
                break
        
        # Extract meta descriptions
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            info['meta_description'] = meta_desc['content']
        
        # Extract title
        title = soup.find('title')
        if title:
            info['page_title'] = title.get_text(strip=True)
        
        return info
    
    def extract_tech_stack(self, soup: BeautifulSoup) -> List[str]:
        """Identify technologies used on the website"""
        tech_stack = set()
        
        # Check meta tags
        meta_generator = soup.find('meta', attrs={'name': 'generator'})
        if meta_generator:
            tech_stack.add(meta_generator.get('content', ''))
        
        # Check for common frameworks/libraries
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script['src'].lower()
            if 'react' in src:
                tech_stack.add('React')
            elif 'vue' in src:
                tech_stack.add('Vue.js')
            elif 'angular' in src:
                tech_stack.add('Angular')
            elif 'jquery' in src:
                tech_stack.add('jQuery')
            elif 'bootstrap' in src:
                tech_stack.add('Bootstrap')
        
        # Check for analytics/tracking
        if soup.find('script', string=lambda t: t and 'google-analytics' in t.lower()):
            tech_stack.add('Google Analytics')
        if soup.find('script', string=lambda t: t and 'gtag' in t.lower()):
            tech_stack.add('Google Tag Manager')
        
        return list(tech_stack)
    
    def find_key_pages(self, base_url: str, soup: BeautifulSoup) -> Dict[str, str]:
        """Find important pages like About, Team, Contact"""
        key_pages = {}
        
        keywords_map = {
            'about': ['about', 'company', 'who-we-are', 'our-story'],
            'team': ['team', 'people', 'founders', 'leadership'],
            'contact': ['contact', 'reach-us', 'get-in-touch'],
            'pricing': ['pricing', 'plans', 'subscribe'],
            'products': ['products', 'solutions', 'services'],
            'blog': ['blog', 'news', 'insights', 'articles'],
            'careers': ['careers', 'jobs', 'hiring', 'join-us']
        }
        
        # Check all links
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.get_text(strip=True).lower()
            
            for page_type, keywords in keywords_map.items():
                if page_type not in key_pages:
                    if any(kw in href or kw in text for kw in keywords):
                        full_url = urljoin(base_url, link['href'])
                        key_pages[page_type] = full_url
        
        return key_pages
    
    def enrich_startup(self, startup: Dict) -> Dict:
        """Enrich a single startup with web scraping"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Enriching: {startup['name']}")
        logger.info(f"{'='*80}")
        
        enriched_data = {
            'enrichment_date': datetime.now().isoformat(),
            'enrichment_success': False,
            'sources_checked': []
        }
        
        # Get website URL
        website = startup.get('website', '').strip()
        if not website:
            logger.warning("No website URL found")
            return enriched_data
        
        # Ensure URL has protocol
        if not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        
        enriched_data['website_url'] = website
        enriched_data['sources_checked'].append('company_website')
        
        # Fetch homepage
        soup = self.fetch_url(website)
        if not soup:
            logger.error("Could not fetch website")
            return enriched_data
        
        enriched_data['enrichment_success'] = True
        
        # Extract information
        logger.info("Extracting company information...")
        company_info = self.extract_company_info(soup)
        enriched_data.update(company_info)
        
        logger.info("Extracting contact information...")
        enriched_data['emails'] = self.extract_emails(soup)
        enriched_data['phone_numbers'] = self.extract_phone_numbers(soup)
        
        logger.info("Extracting social media links...")
        enriched_data['social_media'] = self.extract_social_media(soup, website)
        
        logger.info("Identifying technology stack...")
        enriched_data['tech_stack'] = self.extract_tech_stack(soup)
        
        logger.info("Finding key pages...")
        enriched_data['key_pages'] = self.find_key_pages(website, soup)
        
        # Try to visit key pages for more info
        if 'about' in enriched_data['key_pages']:
            time.sleep(self.delay)
            about_soup = self.fetch_url(enriched_data['key_pages']['about'])
            if about_soup:
                about_info = self.extract_company_info(about_soup)
                if 'about_text' in about_info and len(about_info['about_text']) > len(enriched_data.get('about_text', '')):
                    enriched_data['about_text'] = about_info['about_text']
        
        if 'team' in enriched_data['key_pages']:
            time.sleep(self.delay)
            team_soup = self.fetch_url(enriched_data['key_pages']['team'])
            if team_soup:
                # Try to extract team member names
                team_members = []
                for heading in team_soup.find_all(['h2', 'h3', 'h4']):
                    text = heading.get_text(strip=True)
                    if 2 <= len(text.split()) <= 4:  # Likely a name
                        team_members.append(text)
                if team_members:
                    enriched_data['team_members'] = team_members[:10]
        
        logger.info(f"\n✓ Enrichment complete for {startup['name']}")
        logger.info(f"  - Emails found: {len(enriched_data.get('emails', []))}")
        logger.info(f"  - Social media: {len(enriched_data.get('social_media', {}))}")
        logger.info(f"  - Key pages: {len(enriched_data.get('key_pages', {}))}")
        logger.info(f"  - Tech stack: {len(enriched_data.get('tech_stack', []))}")
        
        return enriched_data

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Enrich startup data from web sources")
    parser.add_argument("--input", default="docs/architecture/ddbb/slush2_extracted.json", 
                        help="Input JSON file")
    parser.add_argument("--output", default="docs/architecture/ddbb/slush2_enriched.json",
                        help="Output JSON file")
    parser.add_argument("--limit", type=int, default=None, 
                        help="Limit number of startups to process")
    parser.add_argument("--start", type=int, default=0,
                        help="Start from this index")
    parser.add_argument("--delay", type=float, default=2,
                        help="Delay between requests (seconds)")
    parser.add_argument("--company", type=str, default=None,
                        help="Process only this company name")
    
    args = parser.parse_args()
    
    logger.info("="*80)
    logger.info("STARTUP DATA ENRICHMENT SCRIPT")
    logger.info("="*80)
    
    # Load startups
    logger.info(f"\nLoading startups from: {args.input}")
    with open(args.input, 'r') as f:
        startups = json.load(f)
    
    logger.info(f"Loaded {len(startups)} startups")
    
    # Filter if company name specified
    if args.company:
        startups = [s for s in startups if args.company.lower() in s['name'].lower()]
        logger.info(f"Filtered to {len(startups)} startups matching '{args.company}'")
    
    # Apply limits
    if args.start > 0:
        startups = startups[args.start:]
        logger.info(f"Starting from index {args.start}")
    
    if args.limit:
        startups = startups[:args.limit]
        logger.info(f"Processing {len(startups)} startups")
    
    # Initialize enricher
    enricher = StartupEnricher(delay=args.delay)
    
    # Process each startup
    enriched_startups = []
    successful = 0
    failed = 0
    
    for i, startup in enumerate(startups, 1):
        logger.info(f"\n[{i}/{len(startups)}] Processing: {startup['name']}")
        
        try:
            enriched_data = enricher.enrich_startup(startup)
            
            # Merge enriched data into startup
            startup['enrichment'] = enriched_data
            
            if enriched_data['enrichment_success']:
                successful += 1
            else:
                failed += 1
            
            enriched_startups.append(startup)
            
            # Save progress periodically
            if i % 10 == 0:
                with open(args.output, 'w') as f:
                    json.dump(enriched_startups, f, indent=2, ensure_ascii=False)
                logger.info(f"Progress saved ({i} startups processed)")
            
            # Rate limiting
            if i < len(startups):
                time.sleep(args.delay)
                
        except KeyboardInterrupt:
            logger.warning("\nInterrupted by user")
            break
        except Exception as e:
            logger.error(f"Error processing {startup['name']}: {str(e)}")
            failed += 1
            enriched_startups.append(startup)
    
    # Save final results
    logger.info(f"\nSaving enriched data to: {args.output}")
    with open(args.output, 'w') as f:
        json.dump(enriched_startups, f, indent=2, ensure_ascii=False)
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("ENRICHMENT COMPLETE")
    logger.info("="*80)
    logger.info(f"Total processed: {len(enriched_startups)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success rate: {(successful/len(enriched_startups)*100):.1f}%")
    logger.info(f"\nOutput saved to: {args.output}")

if __name__ == "__main__":
    main()
