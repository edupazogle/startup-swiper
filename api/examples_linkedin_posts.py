#!/usr/bin/env python
"""
Example usage of the LinkedIn Post Generator
Demonstrates how to use the AI Concierge to generate professional LinkedIn posts
"""

import asyncio
import sys
sys.path.insert(0, '.')

from database import SessionLocal
from ai_concierge import create_concierge


async def example_insurance_ai():
    """Example 1: AI in Insurance Industry"""
    print("\n" + "="*80)
    print("EXAMPLE 1: AI Transformation in Enterprise Insurance")
    print("="*80)
    
    db = SessionLocal()
    concierge = create_concierge(db)
    
    post = await concierge.generate_linkedin_post(
        topic="The rise of AI in enterprise insurance",
        key_points=[
            "AI is transforming claims processing",
            "Automation reduces costs by 40%",
            "Better customer experience through chatbots"
        ],
        people_companies_to_tag=["@AXA", "@InsurTech Leaders"],
        call_to_action="What are your thoughts on AI adoption in insurance?",
        link="https://example.com/ai-insurance-report"
    )
    
    print(post)
    return post


async def example_web3_fund():
    """Example 2: Web3 Investment Fund Announcement"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Web3 Investment Fund Announcement")
    print("="*80)
    
    db = SessionLocal()
    concierge = create_concierge(db)
    
    post = await concierge.generate_linkedin_post(
        topic="Launching our $100M Web3 Infrastructure Fund",
        key_points=[
            "Focusing on Layer 2 scaling solutions",
            "Supporting European blockchain startups",
            "Bringing institutional capital to the ecosystem"
        ],
        people_companies_to_tag=["@Polygon", "@Arbitrum", "@Blockchain Europe"],
        call_to_action="Building the future of Web3? Let's connect.",
        link="https://example.com/web3-fund"
    )
    
    print(post)
    return post


async def example_conference():
    """Example 3: Conference Takeaways"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Conference Takeaways - Slush 2025")
    print("="*80)
    
    db = SessionLocal()
    concierge = create_concierge(db)
    
    post = await concierge.generate_linkedin_post(
        topic="Key insights from Slush 2025 - The future is AI-powered startups",
        key_points=[
            "AI infrastructure plays are outpacing applications",
            "Founders are prioritizing profitability over growth",
            "Talent and execution matter more than ideas"
        ],
        people_companies_to_tag=["@SlushHQ"],
        call_to_action="What was your biggest learning at Slush 2025?"
    )
    
    print(post)
    return post


async def example_blockchain_analysis():
    """Example 4: Blockchain Technology Analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Blockchain Regulatory Landscape Analysis")
    print("="*80)
    
    db = SessionLocal()
    concierge = create_concierge(db)
    
    post = await concierge.generate_linkedin_post(
        topic="EU AI Act implications for blockchain startups",
        key_points=[
            "Compliance costs are 3-5x higher than expected",
            "Startups must plan for regulatory compliance early",
            "Opportunities in compliance-as-a-service"
        ],
        people_companies_to_tag=["@EU_Commission", "@TechPolicy Leaders"],
        call_to_action="How is regulatory uncertainty affecting your blockchain strategy?",
        link="https://example.com/ai-act-analysis"
    )
    
    print(post)
    return post


async def example_tech_market_trends():
    """Example 5: Tech Market Trends"""
    print("\n" + "="*80)
    print("EXAMPLE 5: 2025 Tech Market Trends - What VCs Should Watch")
    print("="*80)
    
    db = SessionLocal()
    concierge = create_concierge(db)
    
    post = await concierge.generate_linkedin_post(
        topic="Five tech trends shaping venture capital in 2025",
        key_points=[
            "Vertical SaaS consolidation is happening rapidly",
            "AI agents are replacing traditional software",
            "Energy consumption is becoming a VC concern",
            "Talent retention is harder than hiring"
        ],
        people_companies_to_tag=["@VCCommunity"],
        call_to_action="Which trend will define 2025 for your portfolio?",
        link="https://example.com/vc-trends-2025"
    )
    
    print(post)
    return post


async def run_all_examples():
    """Run all LinkedIn post generation examples"""
    print("\n" + "🚀"*40)
    print("LINKEDIN POST GENERATOR - EXAMPLE SUITE")
    print("🚀"*40)
    
    examples = [
        example_insurance_ai(),
        example_web3_fund(),
        example_conference(),
        example_blockchain_analysis(),
        example_tech_market_trends()
    ]
    
    posts = []
    for i, example_coro in enumerate(examples, 1):
        print(f"\n⏳ Generating post {i}/5...")
        post = await example_coro
        posts.append(post)
    
    print("\n" + "="*80)
    print(f"✅ GENERATION COMPLETE - {len(posts)} posts generated successfully")
    print("="*80)
    
    return posts


if __name__ == "__main__":
    # Run all examples
    posts = asyncio.run(run_all_examples())
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total posts generated: {len(posts)}")
    print("\nEach post includes:")
    print("✅ Compelling hook with emojis")
    print("✅ Personal context and relevance")
    print("✅ Key points formatted as bullets")
    print("✅ Supporting data and statistics")
    print("✅ Relevant company/person tags")
    print("✅ Clear call to action")
    print("✅ Relevant hashtags")
    print("\nPosts are ready to copy-paste to LinkedIn! 🎉")
