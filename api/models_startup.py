from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, Float, ForeignKey
from datetime import datetime
from models import Base  # Import the shared Base class

class Startup(Base):
    """Startup company data model with full enrichment"""
    __tablename__ = "startups"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)
    
    # Basic company info
    company_type = Column(String)  # startup, scaleup
    company_country = Column(String, index=True)
    company_city = Column(String)
    website = Column(String)
    company_linked_in = Column(String)
    company_description = Column(Text)
    founding_year = Column(Integer)
    
    # Industry & business model
    primary_industry = Column(String, index=True)
    secondary_industry = Column(JSON)  # Array of industries
    focus_industries = Column(JSON)
    business_types = Column(JSON)  # B2B, B2C, etc.
    
    # Categorization
    curated_collections_tags = Column(JSON)  # Special tags
    topics = Column(JSON)  # Topic tags
    tech = Column(JSON)  # Technology tags
    
    # Funding Information (from CB Insights API)
    total_funding = Column(Float)  # Total funding in millions USD (from CB Insights)
    total_equity_funding = Column(Float)  # Equity-only funding in millions USD (from CB Insights)
    funding_stage = Column(String)  # Current funding stage (seed, series a, etc.)
    last_funding_date = Column(DateTime)  # Date of most recent funding round (from CB Insights)
    last_funding_date_str = Column(String)  # ISO format date string
    funding_source = Column(String, default="CB Insights API v2")  # Data source identifier
    valuation = Column(Float)  # Latest valuation in millions USD (from CB Insights)
    latest_revenue_min = Column(Float)  # Latest min revenue in USD (from CB Insights)
    latest_revenue_max = Column(Float)  # Latest max revenue in USD (from CB Insights)
    revenue_date = Column(DateTime)  # Date of revenue data (from CB Insights)
    
    # Company details
    employees = Column(String)
    legalEntity = Column(String)
    shortDescription = Column(Text)
    description = Column(Text)
    technologyReadiness = Column(String)
    pricingModel = Column(String)
    maturity = Column(String)
    maturity_score = Column(Integer)
    
    # Location details
    billingCountry = Column(String)
    billingState = Column(String)
    billingCity = Column(String)
    billingStreet = Column(String)
    billingPostalCode = Column(String)
    
    # External IDs & references
    sfId = Column(String)
    pitchbookId = Column(String)
    mainContactId = Column(Integer)
    parentCompanyId = Column(Integer)
    profile_link = Column(String)
    
    # Assets
    logoUrl = Column(String)
    files = Column(JSON)  # Array of file objects
    
    # Platform data
    featuredLists = Column(JSON)  # Featured in lists
    opportunities = Column(JSON)
    leadOpportunities = Column(JSON)
    
    # Quality & validation
    isMissingValidation = Column(Boolean, default=False)
    isQualityChecked = Column(Boolean)
    qualityChecks = Column(JSON)
    lastQualityCheckDate = Column(DateTime)
    lastQualityCheckById = Column(Integer)
    lastQualityCheckBy = Column(String)
    
    # Enrichment data
    is_enriched = Column(Boolean, default=False, index=True)
    last_enriched_date = Column(DateTime)
    enrichment = Column(JSON)  # Full enrichment object with:
    # - enrichment_date
    # - enrichment_success
    # - sources_checked
    # - website_url
    # - page_title
    # - emails
    # - phone_numbers
    # - social_media (linkedin, twitter, facebook, instagram)
    # - tech_stack
    # - key_pages (about, team, products, contact, blog, careers)
    # - team_members
    
    # CB Insights ID (for accessing external data)
    cb_insights_id = Column(Integer, index=True)
    
    # Extracted Product Information (from web scraping)
    extracted_product = Column(Text)  # What the company sells/offers
    extracted_market = Column(Text)  # Target market/customers
    extracted_technologies = Column(Text)  # Technologies they use
    extracted_competitors = Column(Text)  # Competitors mentioned
    
    # AXA Evaluation Data
    axa_evaluation_date = Column(DateTime)  # When AXA evaluation was performed
    axa_overall_score = Column(Float)  # Overall AXA fit score (0-100)
    axa_priority_tier = Column(String, index=True)  # Tier 1: Critical, Tier 2: High, Tier 3: Monitor, Tier 4: Low
    axa_can_use_as_provider = Column(Boolean)  # Whether startup can be used as provider
    axa_business_leverage = Column(Text)  # How AXA can leverage this startup (use case description)
    axa_primary_topic = Column(String, index=True)  # Primary topic (AI - Software development, Workflow Automation, etc.)
    axa_use_cases = Column(JSON)  # Array of use cases (e.g., ["Workflow Automation"])
    axa_fit_summary = Column(Text)  # Summary of fit evaluation (Rule/Topic identifiers)
    axa_rule_scores = Column(JSON)  # Individual rule/criterion scores
    
    # Value Proposition (Generated)
    value_proposition = Column(Text)  # One-line clear value proposition
    core_product = Column(Text)  # What they sell
    target_customers = Column(Text)  # Who buys it
    problem_solved = Column(Text)  # Problem they address
    key_differentiator = Column(Text)  # What makes them unique
    business_model = Column(String)  # Revenue model (B2B SaaS, consulting, etc.)
    vp_competitors = Column(Text)  # Known competitors in the space
    vp_confidence = Column(String)  # high/medium/low
    vp_reasoning = Column(Text)  # Why this is their value proposition
    
    # Timestamps
    dateCreated = Column(DateTime, default=datetime.utcnow)
    dateFounded = Column(DateTime)
    lastModifiedDate = Column(DateTime)
    lastModifiedById = Column(Integer)
    lastPitchbookSync = Column(DateTime)


class ScoutingReport(Base):
    """CB Insights Scouting Report data model"""
    __tablename__ = "scouting_reports"
    
    # Primary key & relationship
    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, nullable=True, index=True)  # FK to startups table (optional)
    company_name = Column(String, nullable=False, index=True)
    cb_insights_org_id = Column(Integer, nullable=True, index=True)  # CB Insights organization ID
    
    # Report metadata
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    report_source = Column(String, default="cb_insights")  # Source: cb_insights, crunchbase, etc.
    
    # Company information (parsed from report)
    company_founded_year = Column(Integer)
    company_headquarters = Column(String)
    company_description = Column(Text)
    
    # Business metrics
    revenue_latest = Column(Float)  # Latest annual revenue
    revenue_currency = Column(String, default="USD")
    net_income_latest = Column(Float)  # Latest net income/loss
    employee_count = Column(Integer)  # Latest employee count
    employee_count_change_yoy = Column(Float)  # Year-over-year change percentage
    
    # CB Insights proprietary scores
    mosaic_score = Column(Float)  # 0-100 scale
    commercial_maturity = Column(Integer)  # 1-5 scale
    exit_probability = Column(Float)  # 0-100 scale
    
    # Business model & market
    core_products = Column(JSON)  # List of main products/services
    target_markets = Column(JSON)  # List of target markets/customers
    revenue_model = Column(String)  # How they monetize
    primary_industry = Column(String, index=True)
    secondary_industries = Column(JSON)  # List of secondary industries
    
    # Strategic information
    key_partnerships = Column(JSON)  # List of strategic partners
    major_customers = Column(JSON)  # List of known customers
    key_competitors = Column(JSON)  # Competitor information
    
    # Opportunity assessment
    opportunities = Column(JSON)  # List of growth opportunities
    market_size = Column(Float)  # TAM in millions
    market_growth_rate = Column(Float)  # CAGR percentage
    
    # Risk assessment
    threats = Column(JSON)  # List of identified threats
    challenges = Column(JSON)  # Operational challenges
    
    # Leadership & team
    founders = Column(JSON)  # Founder information
    ceo_name = Column(String)
    board_members = Column(JSON)  # Board member information
    
    # Recent news & events
    recent_news = Column(JSON)  # Recent news items
    notable_events = Column(JSON)  # Acquisitions, partnerships, etc.
    
    # Full report content
    report_markdown = Column(Text)  # Full markdown report
    report_json_raw = Column(JSON)  # Raw JSON from CB Insights
    
    # File references
    markdown_file_path = Column(String)  # Path to saved .md file
    json_file_path = Column(String)  # Path to saved .json file
    
    # Investment perspective
    investment_bull_case = Column(Text)  # Bull case summary
    investment_bear_case = Column(Text)  # Bear case summary
    investment_verdict = Column(String)  # Overall assessment
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FundingRound(Base):
    """Individual funding rounds for startups (from CB Insights API)"""
    __tablename__ = "funding_rounds"
    
    # Primary key and relationships
    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey('startups.id'), nullable=True, index=True)  # Link to startup
    
    # CB Insights identifiers
    deal_id = Column(Integer, unique=True, nullable=True, index=True)  # CB Insights deal ID
    cb_insights_org_id = Column(Integer, nullable=True, index=True)  # CB Insights org ID
    
    # Round details
    round_date = Column(DateTime, nullable=True, index=True)  # Date of funding round
    round_date_str = Column(String)  # ISO format date string (YYYY-MM-DD)
    round_name = Column(String)  # e.g., "Series A", "Series B - II"
    round_category = Column(String, index=True)  # e.g., "Series / VC", "Seed / Angel"
    simplified_round = Column(String, index=True)  # Simplified name (e.g., "Series A", "Series B")
    
    # Financial details
    amount_millions = Column(Float)  # Amount raised in millions USD
    valuation_millions = Column(Float)  # Post-money valuation in millions USD
    
    # Company metrics at time of funding
    revenue_min = Column(Float)  # Company revenue (minimum) in USD
    revenue_max = Column(Float)  # Company revenue (maximum) in USD
    revenue_multiple_min = Column(Float)  # Revenue multiple (minimum)
    revenue_multiple_max = Column(Float)  # Revenue multiple (maximum)
    revenue_period = Column(String)  # Time period for revenue (e.g., "FY 2024")
    
    # Investors and metadata
    investors = Column(JSON)  # Array of investor org objects with orgId, name, etc.
    investor_count = Column(Integer)  # Number of investors in this round
    
    # Deal characteristics
    is_exit = Column(Boolean, default=False)  # Whether this is an exit (IPO, acquisition, etc.)
    
    # Content and insights
    sources = Column(JSON)  # Array of URLs to news articles about the deal
    insights = Column(Text)  # AI-generated insights about the deal from CB Insights
    
    # Data source and timestamps
    data_source = Column(String, default="CB Insights API v2")  # Data source identifier
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

