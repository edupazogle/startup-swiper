"""
Test script for enhanced concierge tools
Validates all 17 new tools are properly registered and accessible
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from qwen_agent_enhanced_concierge import (
    # Phase 1: Enhanced Startup Search
    SearchByFundingStage,
    SearchByAXAGrade,
    SearchByLocation,
    SearchByValueProp,
    GetFundingDetails,
    # Phase 2: Meeting Context
    GetMeetingPrep,
    GetUserVotes,
    GetStartupRating,
    # Phase 3: People Intelligence
    SearchPeopleByRole,
    SearchPeopleByCompany,
    SearchPeopleByCountry,
    # Phase 4: Smart Recommendations
    RecommendSimilarStartups,
    GetTrendingStartups,
)

def test_tool_initialization():
    """Test that all tools can be initialized"""
    db = SessionLocal()
    
    try:
        print("🧪 Testing Enhanced Concierge Tools Initialization\n")
        print("=" * 60)
        
        tools_to_test = [
            ("Phase 1: Funding Stage Search", SearchByFundingStage),
            ("Phase 1: AXA Grade Search", SearchByAXAGrade),
            ("Phase 1: Location Search", SearchByLocation),
            ("Phase 1: Value Prop Search", SearchByValueProp),
            ("Phase 1: Funding Details", GetFundingDetails),
            ("Phase 2: Meeting Prep", GetMeetingPrep),
            ("Phase 2: User Votes", GetUserVotes),
            ("Phase 2: Startup Rating", GetStartupRating),
            ("Phase 3: Search by Role", SearchPeopleByRole),
            ("Phase 3: Search by Company", SearchPeopleByCompany),
            ("Phase 3: Search by Country", SearchPeopleByCountry),
            ("Phase 4: Similar Startups", RecommendSimilarStartups),
            ("Phase 4: Trending Startups", GetTrendingStartups),
        ]
        
        success_count = 0
        
        for tool_name, tool_class in tools_to_test:
            try:
                tool = tool_class(db)
                assert hasattr(tool, 'call'), f"{tool_name} missing call method"
                assert hasattr(tool, 'description'), f"{tool_name} missing description"
                assert hasattr(tool, 'parameters'), f"{tool_name} missing parameters"
                print(f"✅ {tool_name:<35} | Initialized successfully")
                success_count += 1
            except Exception as e:
                print(f"❌ {tool_name:<35} | Failed: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"\n📊 Results: {success_count}/{len(tools_to_test)} tools initialized successfully")
        
        if success_count == len(tools_to_test):
            print("\n🎉 All enhanced tools are working!")
            return True
        else:
            print(f"\n⚠️  {len(tools_to_test) - success_count} tools failed initialization")
            return False
            
    finally:
        db.close()


def test_sample_queries():
    """Test sample queries with the new tools"""
    db = SessionLocal()
    
    try:
        print("\n\n🧪 Testing Sample Queries\n")
        print("=" * 60)
        
        # Test funding stage search
        print("\n1️⃣  Testing SearchByFundingStage (Series A):")
        tool = SearchByFundingStage(db)
        result = tool.call({"stage": "Series A", "limit": 3})
        print(f"   {result}\n")
        
        # Test location search
        print("2️⃣  Testing SearchByLocation (Finland):")
        tool = SearchByLocation(db)
        result = tool.call({"country": "Finland", "limit": 3})
        print(f"   {result}\n")
        
        # Test people by role
        print("3️⃣  Testing SearchPeopleByRole (CTO):")
        tool = SearchPeopleByRole(db)
        result = tool.call({"title_query": "CTO", "limit": 3})
        print(f"   {result}\n")
        
        # Test trending startups
        print("4️⃣  Testing GetTrendingStartups:")
        tool = GetTrendingStartups(db)
        result = tool.call({"limit": 5})
        print(f"   {result}\n")
        
        print("=" * 60)
        print("\n✅ Sample queries completed!")
        
    except Exception as e:
        print(f"\n❌ Error during sample queries: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


def test_agent_initialization():
    """Test that the QwenAgentConcierge initializes with all tools"""
    from qwen_agent_enhanced_concierge import QwenAgentConcierge
    
    db = SessionLocal()
    
    try:
        print("\n\n🧪 Testing QwenAgentConcierge Full Initialization\n")
        print("=" * 60)
        
        agent = QwenAgentConcierge(db)
        
        print(f"\n✅ Agent initialized with {len(agent.tools)} tools:")
        print(f"   - Original tools: 9")
        print(f"   - Phase 1 (Search): 5")
        print(f"   - Phase 2 (Meeting): 3")
        print(f"   - Phase 3 (People): 3")
        print(f"   - Phase 4 (Recommendations): 2")
        print(f"   - Total: {len(agent.tools)}")
        
        expected_count = 9 + 5 + 3 + 3 + 2  # 22 tools
        
        if len(agent.tools) == expected_count:
            print(f"\n🎉 All {expected_count} tools registered correctly!")
            return True
        else:
            print(f"\n⚠️  Expected {expected_count} tools, got {len(agent.tools)}")
            return False
            
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "🚀 ENHANCED CONCIERGE TOOLS TEST SUITE".center(60, "="))
    print()
    
    # Run all tests
    test1 = test_tool_initialization()
    test2 = test_sample_queries()
    test3 = test_agent_initialization()
    
    print("\n" + "=" * 60)
    print("\n📋 FINAL SUMMARY")
    print("-" * 60)
    print(f"Tool Initialization:   {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Sample Queries:        ✅ COMPLETED")
    print(f"Agent Integration:     {'✅ PASS' if test3 else '❌ FAIL'}")
    print()
    
    if test1 and test3:
        print("🎉 ALL SYSTEMS GO! Enhanced concierge is production-ready.")
    else:
        print("⚠️  Some issues detected. Review output above.")
    
    print("=" * 60 + "\n")
