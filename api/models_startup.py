from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, Float
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
    
    # Investment & funding
    prominent_investors = Column(String)
    currentInvestmentStage = Column(String)
    totalFunding = Column(Float)
    originalTotalFunding = Column(Float)
    originalTotalFundingCurrency = Column(String)
    lastFundingDate = Column(DateTime)
    lastFunding = Column(Float)
    originalLastFunding = Column(Float)
    originalLastFundingCurrency = Column(String)
    fundingIsUndisclosed = Column(Boolean, default=False)
    
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
    
    # Timestamps
    dateCreated = Column(DateTime, default=datetime.utcnow)
    dateFounded = Column(DateTime)
    lastModifiedDate = Column(DateTime)
    lastModifiedById = Column(Integer)
    lastPitchbookSync = Column(DateTime)
