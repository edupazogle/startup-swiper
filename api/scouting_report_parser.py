"""
Scouting Report Parser and Database Storage

This module parses CB Insights scouting reports and stores the extracted
data in the database for easy querying and analysis.
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models_startup import ScoutingReport


class ScoutingReportParser:
    """Parse CB Insights scouting reports and extract structured data"""
    
    def __init__(self, markdown_content: str):
        """Initialize parser with markdown report content"""
        self.content = markdown_content
        self.sections = self._parse_sections()
    
    def _parse_sections(self) -> Dict[str, str]:
        """Parse markdown into sections"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in self.content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.replace('## ', '').strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def get_company_name(self) -> str:
        """Extract company name from title"""
        match = re.search(r'^# (.+?) Company Report', self.content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Unknown"
    
    def get_company_founded_year(self) -> Optional[int]:
        """Extract founding year"""
        company_overview = self.sections.get('Company Overview', '')
        match = re.search(r'\*\*Founded\*\*:\s*(\d{4})', company_overview)
        if match:
            return int(match.group(1))
        return None
    
    def get_headquarters(self) -> Optional[str]:
        """Extract headquarters"""
        company_overview = self.sections.get('Company Overview', '')
        match = re.search(r'\*\*Headquarters\*\*:\s*(.+?)(?:\n|$|\[)', company_overview)
        if match:
            return match.group(1).strip()
        return None
    
    def get_company_description(self) -> Optional[str]:
        """Extract company description from overview"""
        # Get description from the first paragraph before "## Key Takeaways"
        match = re.search(r'^(.*?)(?=##)', self.content, re.DOTALL)
        if match:
            # Remove title and clean up
            text = match.group(1).replace('# ', '').strip()
            lines = [line.strip() for line in text.split('\n') if line.strip() and not line.startswith('*')]
            if lines:
                return lines[-1]  # Usually the last line before sections
        return None
    
    def get_revenue_latest(self) -> Optional[float]:
        """Extract latest revenue in millions"""
        financials = self.sections.get('Financials', '')
        match = re.search(r'2024:\s*\$?([\d.]+)M', financials)
        if match:
            return float(match.group(1))
        return None
    
    def get_net_income_latest(self) -> Optional[float]:
        """Extract latest net income/loss in millions"""
        financials = self.sections.get('Financials', '')
        
        # Look for "Profit" or "net loss" entries
        # Pattern: "2024: -$7.1M net loss"
        match = re.search(r'2024:\s*-\$?([\d.]+)M\s+net loss', financials)
        if match:
            return -float(match.group(1))  # Negative for loss
        
        # Also try "Profit" entry with -$ prefix
        match = re.search(r'\*\*Profit\*\*:\s*2024:\s*-\$?([\d.]+)M', financials)
        if match:
            return -float(match.group(1))
        
        # Generic profit pattern
        match = re.search(r'\*\*Profit\*\*:\s*[+-]?\$?([\d.]+)M', financials)
        if match:
            return float(match.group(1))
        
        return None
    
    def get_employee_count(self) -> Optional[int]:
        """Extract employee count"""
        key_takeaways = self.sections.get('Key Takeaways', '')
        match = re.search(r'(\d+)\s+employees', key_takeaways)
        if match:
            return int(match.group(1))
        return None
    
    def get_employee_yoy_change(self) -> Optional[float]:
        """Extract employee count change percentage"""
        key_takeaways = self.sections.get('Key Takeaways', '')
        match = re.search(r'(\d+)%\s+year-over-year', key_takeaways)
        if match:
            return -float(match.group(1))  # Negative for decline
        return None
    
    def get_total_funding(self) -> Optional[float]:
        """Extract total funding in millions from scouting report"""
        financials = self.sections.get('Financials', '')
        
        # Try different patterns
        patterns = [
            r'Total Funding:\s*\$?([\d.]+)M',
            r'\*\*Total Funding\*\*:\s*\$?([\d.]+)M',
            r'Total Funding.*?\$?([\d.]+)M'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, financials, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
        match = re.search(r'raised\s+\$?([\d.]+)M', financials)
        if match:
            return float(match.group(1))
        
        return None
    
    def get_commercial_maturity(self) -> Optional[int]:
        """Extract commercial maturity score (1-5)"""
        outlook = self.sections.get('Outlook', '')
        match = re.search(r'(\d)/5', outlook)
        if match:
            return int(match.group(1))
        return None
    
    def get_core_products(self) -> List[str]:
        """Extract core products/services"""
        business_model = self.sections.get('Business Model', '')
        
        products = []
        
        # Look for specific products mentioned
        product_patterns = [
            r'Emailbot', r'Documentbot', r'Chatbot', r'InsuranceGPT',
            r'digital employees'
        ]
        
        for pattern in product_patterns:
            if re.search(pattern, business_model, re.IGNORECASE):
                # Extract more context if available
                match = re.search(
                    rf'{pattern}(?:s?)(?:[:,]?)([^.]*)',
                    business_model,
                    re.IGNORECASE
                )
                if match:
                    desc = match.group(1).strip()
                    if desc:
                        products.append(f"{pattern}: {desc[:100]}")
                    else:
                        products.append(pattern)
        
        return products
    
    def get_target_markets(self) -> List[str]:
        """Extract target markets"""
        business_model = self.sections.get('Business Model', '')
        
        markets = []
        
        # Look for market mentions
        market_patterns = [
            'financial services', 'insurance companies', 'banks',
            'pension providers', 'public sector organizations',
            'Nordic financial institutions', 'US insurance market'
        ]
        
        for market in market_patterns:
            if market.lower() in business_model.lower():
                markets.append(market)
        
        return markets
    
    def get_key_partnerships(self) -> List[str]:
        """Extract key partnerships"""
        partnerships = []
        
        # Look in multiple sections
        for section_name in ['Key Takeaways', 'Business Model', 'Market Position']:
            section = self.sections.get(section_name, '')
            
            # Look for partnership patterns
            partners = [
                'Storebrand', 'Stillwater Insurance Group',
                'TD SYNNEX', 'Tech Data', 'Inin Group'
            ]
            
            for partner in partners:
                if partner in section:
                    partnerships.append(partner)
        
        return list(set(partnerships))  # Remove duplicates
    
    def get_major_customers(self) -> List[str]:
        """Extract major customers"""
        customers = []
        
        for section_name in ['Key Takeaways', 'Business Model', 'Highlights']:
            section = self.sections.get(section_name, '')
            
            customer_names = [
                'Storebrand', 'Stillwater Insurance Group',
                'enterprise insurance client', 'C-level executive'
            ]
            
            for customer in customer_names:
                if customer in section and customer not in customers:
                    customers.append(customer)
        
        return customers
    
    def get_key_competitors(self) -> List[Dict[str, str]]:
        """Extract key competitors"""
        competitors = []
        
        key_competitors = self.sections.get('Key Competitors', '')
        
        # Parse competitor entries
        for line in key_competitors.split('\n'):
            if line.startswith('- **'):
                match = re.search(r'\*\*(.+?)\*\*:\s*(.+?)(?=\[|$)', line)
                if match:
                    name = match.group(1)
                    description = match.group(2).strip()
                    competitors.append({
                        'name': name,
                        'description': description
                    })
        
        return competitors
    
    def get_opportunities(self) -> List[str]:
        """Extract opportunities"""
        opportunities = []
        
        opps_section = self.sections.get('Opportunities', '')
        
        # Split by bullet points
        for item in opps_section.split('\n- ')[1:]:  # Skip first empty
            # Take first 200 chars as summary
            summary = item.split('[')[0].strip()[:200]
            if summary:
                opportunities.append(summary)
        
        return opportunities
    
    def get_threats(self) -> List[str]:
        """Extract threats"""
        threats = []
        
        threats_section = self.sections.get('Threats', '')
        
        # Split by bullet points
        for item in threats_section.split('\n- ')[1:]:  # Skip first empty
            # Take first 200 chars as summary
            summary = item.split('[')[0].strip()[:200]
            if summary:
                threats.append(summary)
        
        return threats
    
    def get_recent_news(self) -> List[Dict[str, str]]:
        """Extract recent news items"""
        news = []
        
        news_section = self.sections.get('In the News', '')
        
        # Parse news entries (format: **Date**: Description)
        for line in news_section.split('\n'):
            if line.startswith('- **'):
                match = re.search(r'\*\*([^*]+)\*\*:\s*(.+?)(?=\[|$)', line)
                if match:
                    date = match.group(1)
                    description = match.group(2).strip()
                    news.append({
                        'date': date,
                        'description': description[:300]  # Limit length
                    })
        
        return news
    
    def get_founders(self) -> List[str]:
        """Extract founder names"""
        founders = []
        
        key_takeaways = self.sections.get('Key Takeaways', '')
        
        # Look for founder names mentioned
        founder_patterns = [
            'Bør Myrstad', 'Erik Leung'
        ]
        
        for founder in founder_patterns:
            if founder in key_takeaways:
                founders.append(founder)
        
        return founders
    
    def get_ceo(self) -> Optional[str]:
        """Extract CEO name"""
        key_takeaways = self.sections.get('Key Takeaways', '')
        
        match = re.search(r'CEO\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', key_takeaways)
        if match:
            return match.group(1)
        
        # Also check for "taking over as CEO" pattern
        match = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+taking over as CEO', key_takeaways)
        if match:
            return match.group(1)
        
        return None
    
    def extract_all(self) -> Dict[str, Any]:
        """Extract all data into a structured dictionary"""
        return {
            'company_name': self.get_company_name(),
            'company_founded_year': self.get_company_founded_year(),
            'company_headquarters': self.get_headquarters(),
            'company_description': self.get_company_description(),
            'revenue_latest': self.get_revenue_latest(),
            'net_income_latest': self.get_net_income_latest(),
            'employee_count': self.get_employee_count(),
            'employee_count_change_yoy': self.get_employee_yoy_change(),
            'total_funding': self.get_total_funding(),
            'commercial_maturity': self.get_commercial_maturity(),
            'core_products': self.get_core_products(),
            'target_markets': self.get_target_markets(),
            'key_partnerships': self.get_key_partnerships(),
            'major_customers': self.get_major_customers(),
            'key_competitors': self.get_key_competitors(),
            'opportunities': self.get_opportunities(),
            'threats': self.get_threats(),
            'recent_news': self.get_recent_news(),
            'founders': self.get_founders(),
            'ceo_name': self.get_ceo(),
        }


def store_scouting_report(
    db: Session,
    company_name: str,
    cb_insights_org_id: int,
    markdown_content: str,
    json_content: Dict[str, Any],
    markdown_file_path: str,
    json_file_path: str,
    startup_id: Optional[int] = None
) -> ScoutingReport:
    """
    Parse scouting report and store in database
    
    Args:
        db: Database session
        company_name: Company name
        cb_insights_org_id: CB Insights organization ID
        markdown_content: Full markdown report content
        json_content: Full JSON report content
        markdown_file_path: Path where markdown is saved
        json_file_path: Path where JSON is saved
        startup_id: Optional reference to startups table
    
    Returns:
        ScoutingReport object
    """
    # Parse the markdown content
    parser = ScoutingReportParser(markdown_content)
    extracted_data = parser.extract_all()
    
    # Create scouting report record
    report = ScoutingReport(
        startup_id=startup_id,
        company_name=company_name,
        cb_insights_org_id=cb_insights_org_id,
        company_founded_year=extracted_data['company_founded_year'],
        company_headquarters=extracted_data['company_headquarters'],
        company_description=extracted_data['company_description'],
        revenue_latest=extracted_data['revenue_latest'],
        revenue_currency='USD',
        net_income_latest=extracted_data['net_income_latest'],
        employee_count=extracted_data['employee_count'],
        employee_count_change_yoy=extracted_data['employee_count_change_yoy'],
        commercial_maturity=extracted_data['commercial_maturity'],
        core_products=extracted_data['core_products'],
        target_markets=extracted_data['target_markets'],
        key_partnerships=extracted_data['key_partnerships'],
        major_customers=extracted_data['major_customers'],
        key_competitors=extracted_data['key_competitors'],
        opportunities=extracted_data['opportunities'],
        threats=extracted_data['threats'],
        recent_news=extracted_data['recent_news'],
        founders=extracted_data['founders'],
        ceo_name=extracted_data['ceo_name'],
        report_markdown=markdown_content,
        report_json_raw=json_content,
        markdown_file_path=markdown_file_path,
        json_file_path=json_file_path,
        generated_at=datetime.utcnow()
    )
    
    # Add to database
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report
