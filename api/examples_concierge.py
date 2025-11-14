"""
Example usage of the AI Concierge system

This demonstrates how to use the concierge in various scenarios.
"""

import asyncio
import requests
import json

BASE_URL = "http://localhost:8000"

# Example 1: Ask about specific startups
def example_startup_query():
    """Query information about startups"""
    print("\n" + "="*60)
    print("Example 1: Startup Query")
    print("="*60 + "\n")
    
    question = "Tell me about AI startups that have raised over $1M"
    
    response = requests.post(
        f"{BASE_URL}/concierge/ask",
        json={"question": question}
    )
    
    if response.status_code == 200:
        print(f"Question: {question}\n")
        print(f"Answer:\n{response.json()['answer']}")
    else:
        print(f"Error: {response.status_code}")

# Example 2: Get event information
def example_event_query():
    """Query about events"""
    print("\n" + "="*60)
    print("Example 2: Event Information")
    print("="*60 + "\n")
    
    question = "What are the main keynote sessions today?"
    
    response = requests.post(
        f"{BASE_URL}/concierge/ask",
        json={"question": question}
    )
    
    if response.status_code == 200:
        print(f"Question: {question}\n")
        print(f"Answer:\n{response.json()['answer']}")
    else:
        print(f"Error: {response.status_code}")

# Example 3: Get directions
def example_directions():
    """Get directions between locations"""
    print("\n" + "="*60)
    print("Example 3: Getting Directions")
    print("="*60 + "\n")
    
    request_data = {
        "origin": "Helsinki Central Station",
        "destination": "Messukeskus Helsinki",
        "mode": "walking"
    }
    
    response = requests.post(
        f"{BASE_URL}/concierge/directions",
        json=request_data
    )
    
    if response.status_code == 200:
        print(f"From: {request_data['origin']}")
        print(f"To: {request_data['destination']}")
        print(f"Mode: {request_data['mode']}\n")
        print(response.json()['answer'])
    else:
        print(f"Error: {response.status_code}")

# Example 4: Search for startups
def example_startup_search():
    """Search for startups by keyword"""
    print("\n" + "="*60)
    print("Example 4: Startup Search")
    print("="*60 + "\n")
    
    query = "fintech"
    
    response = requests.get(
        f"{BASE_URL}/concierge/search-startups",
        params={"query": query, "limit": 5}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Search query: '{query}'")
        print(f"Found {data['count']} startups\n")
        
        for startup in data['results']:
            print(f"• {startup['name']}")
            print(f"  {startup.get('shortDescription', 'No description')}")
            print(f"  Funding: ${startup.get('totalFunding', '0')}M")
            print()
    else:
        print(f"Error: {response.status_code}")

# Example 5: Get detailed startup info
def example_startup_details():
    """Get detailed information about a specific startup"""
    print("\n" + "="*60)
    print("Example 5: Detailed Startup Information")
    print("="*60 + "\n")
    
    startup_name = "759 Studio"
    
    response = requests.post(
        f"{BASE_URL}/concierge/startup-details",
        json={"startup_name": startup_name}
    )
    
    if response.status_code == 200:
        print(response.json()['answer'])
    else:
        print(f"Error: {response.status_code}")

# Example 6: Complex question with context
def example_complex_query():
    """Ask a complex question with user context"""
    print("\n" + "="*60)
    print("Example 6: Complex Query with Context")
    print("="*60 + "\n")
    
    question = "I'm an investor interested in sustainable tech. Which startups should I meet?"
    
    user_context = {
        "role": "investor",
        "interests": ["sustainability", "cleantech", "green energy"],
        "investment_stage": ["seed", "series-a"],
        "location": "Helsinki"
    }
    
    response = requests.post(
        f"{BASE_URL}/concierge/ask",
        json={
            "question": question,
            "user_context": user_context
        }
    )
    
    if response.status_code == 200:
        print(f"Question: {question}\n")
        print(f"User Context: {json.dumps(user_context, indent=2)}\n")
        print(f"Answer:\n{response.json()['answer']}")
    else:
        print(f"Error: {response.status_code}")

# Example 7: Meeting and schedule queries
def example_meeting_query():
    """Query about meetings and schedules"""
    print("\n" + "="*60)
    print("Example 7: Meeting Information")
    print("="*60 + "\n")
    
    question = "What meetings are scheduled for today and who will be attending?"
    
    response = requests.post(
        f"{BASE_URL}/concierge/ask",
        json={"question": question}
    )
    
    if response.status_code == 200:
        print(f"Question: {question}\n")
        print(f"Answer:\n{response.json()['answer']}")
    else:
        print(f"Error: {response.status_code}")

# Example 8: Category-based search
def example_category_search():
    """Search startups by category"""
    print("\n" + "="*60)
    print("Example 8: Category Search")
    print("="*60 + "\n")
    
    category = "Artificial Intelligence"
    
    response = requests.get(
        f"{BASE_URL}/concierge/startup-categories",
        params={"category": category, "limit": 10}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Category: {data['category']}")
        print(f"Found {data['count']} startups\n")
        
        for i, startup in enumerate(data['results'], 1):
            print(f"{i}. {startup['name']}")
            print(f"   {startup.get('shortDescription', 'No description')[:100]}...")
            print()
    else:
        print(f"Error: {response.status_code}")

# Example 9: JavaScript/TypeScript usage example
def example_javascript_usage():
    """Show how to use from JavaScript/TypeScript"""
    print("\n" + "="*60)
    print("Example 9: JavaScript/TypeScript Usage")
    print("="*60 + "\n")
    
    js_code = '''
// Example 1: Ask the concierge a question
async function askConcierge(question) {
  const response = await fetch('http://localhost:8000/concierge/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      user_context: {
        location: 'Helsinki',
        role: 'attendee'
      }
    })
  });
  
  const data = await response.json();
  return data.answer;
}

// Example 2: Search for startups
async function searchStartups(query) {
  const response = await fetch(
    `http://localhost:8000/concierge/search-startups?query=${query}&limit=10`
  );
  
  const data = await response.json();
  return data.results;
}

// Example 3: Get directions
async function getDirections(origin, destination, mode = 'walking') {
  const response = await fetch('http://localhost:8000/concierge/directions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ origin, destination, mode })
  });
  
  const data = await response.json();
  return data.answer;
}

// Usage
const answer = await askConcierge("What AI startups are at the event?");
const startups = await searchStartups("fintech");
const directions = await getDirections("Hotel", "Messukeskus", "walking");
'''
    
    print(js_code)

def main():
    """Run all examples"""
    print("="*60)
    print("AI CONCIERGE USAGE EXAMPLES")
    print("="*60)
    
    examples = [
        example_startup_query,
        example_event_query,
        example_directions,
        example_startup_search,
        example_startup_details,
        example_complex_query,
        example_meeting_query,
        example_category_search,
        example_javascript_usage
    ]
    
    for example in examples:
        try:
            example()
            input("\nPress Enter to continue to next example...")
        except requests.exceptions.ConnectionError:
            print("\n✗ Cannot connect to API. Please start it with: uvicorn main:app --reload")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
