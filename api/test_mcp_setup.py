#!/usr/bin/env python3
"""
Test script for AI Concierge MCP + NVIDIA NIM integration

Run this to verify the setup is working correctly
"""

import asyncio
import sys
from pathlib import Path

# Add API directory to path
api_dir = Path(__file__).parent
sys.path.insert(0, str(api_dir))


async def test_litellm_config():
    """Test LiteLLM and NVIDIA NIM configuration"""
    print("\n" + "="*60)
    print("TEST 1: LiteLLM & NVIDIA NIM Configuration")
    print("="*60)
    
    try:
        from llm_config import (
            is_nvidia_nim_configured,
            get_nvidia_nim_model,
            NVIDIA_NIM_CONFIG
        )
        
        print("\n✓ LiteLLM module imported successfully")
        
        if is_nvidia_nim_configured():
            print("✓ NVIDIA NIM is configured")
            print(f"  - Model: {get_nvidia_nim_model()}")
            print(f"  - Base URL: {NVIDIA_NIM_CONFIG['base_url']}")
            return True
        else:
            print("✗ NVIDIA NIM not configured")
            print("  - Set NVIDIA_API_KEY in .env file")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_database_connection():
    """Test database connection"""
    print("\n" + "="*60)
    print("TEST 2: Database Connection")
    print("="*60)
    
    try:
        from database import SessionLocal
        from models_startup import Startup
        
        print("\n✓ Database modules imported")
        
        db = SessionLocal()
        startup_count = db.query(Startup).count()
        db.close()
        
        if startup_count > 0:
            print(f"✓ Database connection successful")
            print(f"  - Startups in database: {startup_count}")
            return True
        else:
            print("⚠️  Database connected but no startups found")
            print("  - Run: python create_startup_database.py")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  - Check database configuration")
        return False


async def test_mcp_client():
    """Test MCP client tools"""
    print("\n" + "="*60)
    print("TEST 3: MCP Client & Tools")
    print("="*60)
    
    try:
        from mcp_client import StartupDatabaseMCPTools
        
        print("\n✓ MCP client module imported")
        
        tools = StartupDatabaseMCPTools()
        tool_defs = tools.get_tools_for_llm()
        
        print(f"✓ MCP tools initialized")
        print(f"  - Available tools: {len(tool_defs)}")
        
        for tool in tool_defs:
            func_name = tool['function']['name']
            print(f"    • {func_name}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_ai_concierge():
    """Test AI Concierge with MCP"""
    print("\n" + "="*60)
    print("TEST 4: AI Concierge with MCP")
    print("="*60)
    
    try:
        from ai_concierge import create_mcp_concierge
        from database import SessionLocal
        
        print("\n✓ AI Concierge modules imported")
        
        db = SessionLocal()
        concierge = create_mcp_concierge(db)
        
        print("✓ MCP-Enhanced Concierge created")
        
        tools = concierge.get_tool_definitions()
        print(f"✓ Tool definitions retrieved: {len(tools)} tools")
        
        db.close()
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_simple_search():
    """Test a simple startup search"""
    print("\n" + "="*60)
    print("TEST 5: Simple Startup Search")
    print("="*60)
    
    try:
        from ai_concierge import create_mcp_concierge
        from database import SessionLocal
        
        print("\n✓ Starting test search...")
        
        db = SessionLocal()
        concierge = create_mcp_concierge(db)
        
        # Test searching for a startup
        result = await concierge.conversational_startup_search(
            query="AI",
            search_type="industry"
        )
        
        if result and "Found" in result:
            print("✓ Search successful")
            print(f"\nSample result:\n{result[:300]}...")
            db.close()
            return True
        else:
            print("⚠️  Search completed but no results")
            print(f"Result: {result}")
            db.close()
            return True  # Still pass since search works
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_llm_call():
    """Test LLM call with NVIDIA NIM"""
    print("\n" + "="*60)
    print("TEST 6: LLM Call (NVIDIA NIM)")
    print("="*60)
    
    try:
        from llm_config import is_nvidia_nim_configured, simple_llm_call
        
        if not is_nvidia_nim_configured():
            print("\n⚠️  NVIDIA NIM not configured (skipping)")
            print("  - Set NVIDIA_API_KEY in .env to test")
            return True
        
        print("\n✓ Testing LLM call with NVIDIA NIM...")
        
        response = simple_llm_call(
            prompt="What is 2+2?",
            system_message="You are a helpful assistant. Answer concisely."
        )
        
        if response:
            print("✓ LLM call successful")
            print(f"\nResponse:\n{response[:200]}...")
            return True
        else:
            print("✗ LLM returned empty response")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  - Verify NVIDIA_API_KEY and internet connection")
        return False


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "AI CONCIERGE MCP SETUP TEST" + " "*17 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("LiteLLM Config", test_litellm_config),
        ("Database", test_database_connection),
        ("MCP Client", test_mcp_client),
        ("AI Concierge", test_ai_concierge),
        ("Startup Search", test_simple_search),
        ("LLM Call", test_llm_call),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "🎉 "*10)
        print("ALL TESTS PASSED!")
        print("Setup is complete and working correctly.")
        print("🎉 "*10)
        return 0
    elif passed >= total - 1:
        print("\n⚠️  PARTIAL SUCCESS")
        print("Most tests passed. Check the failures above.")
        return 1
    else:
        print("\n❌ SETUP INCOMPLETE")
        print("Please fix the failing tests before using the system.")
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
