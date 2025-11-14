#!/usr/bin/env python3
"""
Enriched Data API Documentation and Usage Examples
"""

# Usage Examples for Enriched Data Endpoints

EXAMPLES = """
# ============================================
# ENRICHED DATA ENDPOINTS
# ============================================

## 1. Search Enriched Startups

GET /startups/enriched/search?query=AI&enrichment_type=tech_stack&limit=10

Response:
{
  "results": [
    {
      "id": "startup_123",
      "name": "TechVision AI",
      "website": "https://techvision.ai",
      "enrichment": {
        "emails": ["contact@techvision.ai"],
        "phone_numbers": ["+1-234-567-8900"],
        "social_media": {
          "linkedin": "https://linkedin.com/company/techvision",
          "twitter": "https://twitter.com/techvision",
          "github": "https://github.com/techvision"
        },
        "tech_stack": ["React", "Python", "PyTorch", "Kubernetes"],
        "key_pages": {
          "about": "https://techvision.ai/about",
          "team": "https://techvision.ai/team",
          "contact": "https://techvision.ai/contact"
        },
        "team_members": ["John Doe - CEO", "Jane Smith - CTO"]
      },
      "enriched_date": "2025-11-14T10:30:00Z"
    }
  ],
  "count": 1,
  "enrichment_type": "tech_stack",
  "query": "AI"
}


## 2. Get Specific Startup Enrichment

GET /startups/startup_123/enrichment

Response:
{
  "startup_id": "startup_123",
  "startup_name": "TechVision AI",
  "website": "https://techvision.ai",
  "enrichment": {
    "emails": ["contact@techvision.ai", "info@techvision.ai"],
    "phone_numbers": ["+1-234-567-8900"],
    "social_media": {
      "linkedin": "https://linkedin.com/company/techvision",
      "twitter": "https://twitter.com/techvision",
      "github": "https://github.com/techvision",
      "instagram": "https://instagram.com/techvision"
    },
    "tech_stack": [
      "React",
      "Python",
      "PyTorch",
      "Kubernetes",
      "Docker",
      "PostgreSQL"
    ],
    "key_pages": {
      "about": "https://techvision.ai/about",
      "team": "https://techvision.ai/team",
      "contact": "https://techvision.ai/contact",
      "blog": "https://techvision.ai/blog",
      "careers": "https://techvision.ai/careers",
      "products": "https://techvision.ai/products"
    },
    "team_members": [
      "John Doe - CEO & Co-founder",
      "Jane Smith - CTO & Co-founder",
      "Mike Johnson - VP Product",
      "Sarah Williams - Head of Sales"
    ],
    "enrichment_date": "2025-11-14T10:30:00Z",
    "sources_checked": [
      "website",
      "linkedin",
      "twitter",
      "github"
    ]
  },
  "last_enriched": "2025-11-14T10:30:00Z"
}


## 3. Get Enrichment Statistics

GET /startups/enrichment/stats

Response:
{
  "total_startups": 4374,
  "enriched_count": 1250,
  "enrichment_percentage": 28.6,
  "fields_available": {
    "with_emails": 1180,
    "with_phone": 890,
    "with_social": 1100,
    "with_tech_stack": 950,
    "with_team": 820
  }
}


## 4. Find Startups by Enriched Field

POST /startups/enrichment/by-name

Body:
{
  "field_name": "tech",
  "field_value": "React",
  "limit": 10
}

Response:
{
  "results": [
    {
      "id": "startup_123",
      "name": "TechVision AI",
      "website": "https://techvision.ai",
      "matched_field": "tech",
      "enrichment_date": "2025-11-14T10:30:00Z"
    },
    {
      "id": "startup_456",
      "name": "WebFlow Studio",
      "website": "https://webflow.studio",
      "matched_field": "tech",
      "enrichment_date": "2025-11-14T09:15:00Z"
    }
  ],
  "count": 2,
  "search_field": "tech",
  "search_value": "React"
}


## 5. Search by Email

POST /startups/enrichment/by-name

Body:
{
  "field_name": "email",
  "field_value": "@techvision.ai",
  "limit": 5
}


## 6. Search by Person Name

POST /startups/enrichment/by-name

Body:
{
  "field_name": "person",
  "field_value": "John Doe",
  "limit": 5
}


## 7. Search by Technology

POST /startups/enrichment/by-name

Body:
{
  "field_name": "tech",
  "field_value": "Kubernetes",
  "limit": 20
}

---

# ENRICHMENT FIELDS EXPLAINED

## emails
Array of contact email addresses extracted from the startup website
Example: ["contact@company.com", "info@company.com"]

## phone_numbers
Array of phone numbers found on website and contact pages
Example: ["+1-234-567-8900", "+44-20-7123-4567"]

## social_media
Object with social media profiles and URLs
Keys: linkedin, twitter, github, instagram, facebook, youtube
Example:
{
  "linkedin": "https://linkedin.com/company/...",
  "twitter": "https://twitter.com/...",
  "github": "https://github.com/..."
}

## tech_stack
Array of technologies found on website (from HTML, meta tags, scripts)
Example: ["React", "Node.js", "PostgreSQL", "Docker", "Kubernetes"]

## key_pages
Object with URLs to important pages
Keys: about, team, contact, blog, careers, products, pricing, docs
Example:
{
  "about": "https://company.com/about",
  "team": "https://company.com/team",
  "contact": "https://company.com/contact"
}

## team_members
Array of team member names extracted from team/about pages
Example: ["John Doe - CEO", "Jane Smith - CTO"]

## enrichment_date
ISO timestamp of when enrichment was performed
Example: "2025-11-14T10:30:00Z"

## sources_checked
Array of sources that were checked during enrichment
Example: ["website", "linkedin", "twitter", "github"]

---

# PYTHON CLIENT EXAMPLES

## Basic Search

```python
import requests

BASE_URL = "http://localhost:8000"

# Search for AI startups with tech stack enrichment
response = requests.get(
    f"{BASE_URL}/startups/enriched/search",
    params={
        "query": "AI",
        "enrichment_type": "tech_stack",
        "limit": 10
    }
)

for startup in response.json()["results"]:
    print(f"{startup['name']}")
    print(f"  Tech Stack: {startup['enrichment']['tech_stack']}")
    print(f"  Website: {startup['website']}")
```

## Get Startup Enrichment

```python
startup_id = "startup_123"
response = requests.get(
    f"{BASE_URL}/startups/{startup_id}/enrichment"
)

data = response.json()
startup = data['startup_name']
emails = data['enrichment']['emails']
social = data['enrichment']['social_media']

print(f"Startup: {startup}")
print(f"Contact Emails: {emails}")
print(f"LinkedIn: {social.get('linkedin', 'N/A')}")
```

## Find Startups by Technology

```python
response = requests.post(
    f"{BASE_URL}/startups/enrichment/by-name",
    json={
        "field_name": "tech",
        "field_value": "React",
        "limit": 20
    }
)

results = response.json()["results"]
print(f"Found {len(results)} startups using React")

for startup in results:
    print(f"  - {startup['name']} ({startup['website']})")
```

## Get Enrichment Statistics

```python
response = requests.get(f"{BASE_URL}/startups/enrichment/stats")
stats = response.json()

print(f"Total Startups: {stats['total_startups']}")
print(f"Enriched: {stats['enriched_count']} ({stats['enrichment_percentage']:.1f}%)")
print(f"With Emails: {stats['fields_available']['with_emails']}")
print(f"With Tech Stack: {stats['fields_available']['with_tech_stack']}")
```

---

# JAVASCRIPT/TYPESCRIPT CLIENT EXAMPLES

## React Component - Display Enrichment

```typescript
import { useState, useEffect } from 'react';

interface StartupEnrichment {
  emails: string[];
  phone_numbers: string[];
  social_media: Record<string, string>;
  tech_stack: string[];
  team_members: string[];
}

export function StartupEnrichmentCard({ startupId }: { startupId: string }) {
  const [enrichment, setEnrichment] = useState<StartupEnrichment | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/startups/${startupId}/enrichment`)
      .then(r => r.json())
      .then(data => setEnrichment(data.enrichment))
      .finally(() => setLoading(false));
  }, [startupId]);

  if (loading) return <div>Loading...</div>;
  if (!enrichment) return <div>No enrichment data</div>;

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3>Contact Information</h3>
      <div className="my-4">
        <h4 className="font-bold">Emails:</h4>
        {enrichment.emails.map(email => (
          <div key={email}>{email}</div>
        ))}
      </div>

      <div className="my-4">
        <h4 className="font-bold">Technology Stack:</h4>
        <div className="flex flex-wrap gap-2">
          {enrichment.tech_stack.map(tech => (
            <span key={tech} className="bg-blue-100 px-2 py-1 rounded">
              {tech}
            </span>
          ))}
        </div>
      </div>

      <div className="my-4">
        <h4 className="font-bold">Team Members:</h4>
        {enrichment.team_members.map(member => (
          <div key={member}>{member}</div>
        ))}
      </div>

      <div className="my-4">
        <h4 className="font-bold">Social Media:</h4>
        {Object.entries(enrichment.social_media).map(([platform, url]) => (
          <div key={platform}>
            <a href={url} target="_blank" rel="noopener noreferrer">
              {platform}: {url}
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Search Component

```typescript
import { useState } from 'react';

export function EnrichedStartupSearch() {
  const [query, setQuery] = useState('');
  const [enrichmentType, setEnrichmentType] = useState('');
  const [results, setResults] = useState([]);

  const search = async () => {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (enrichmentType) params.append('enrichment_type', enrichmentType);
    params.append('limit', '20');

    const response = await fetch(
      `/api/startups/enriched/search?${params}`
    );
    const data = await response.json();
    setResults(data.results);
  };

  return (
    <div className="p-4">
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Search startups..."
        className="w-full p-2 border rounded"
      />

      <select
        value={enrichmentType}
        onChange={e => setEnrichmentType(e.target.value)}
        className="w-full p-2 border rounded mt-2"
      >
        <option value="">All Fields</option>
        <option value="emails">With Emails</option>
        <option value="social">With Social Media</option>
        <option value="tech_stack">With Tech Stack</option>
        <option value="team">With Team Info</option>
      </select>

      <button
        onClick={search}
        className="w-full mt-2 p-2 bg-blue-500 text-white rounded"
      >
        Search
      </button>

      <div className="mt-4">
        {results.map(startup => (
          <div key={startup.id} className="p-3 border rounded mb-2">
            <h3 className="font-bold">{startup.name}</h3>
            <p className="text-sm text-gray-600">{startup.website}</p>
            {startup.enrichment.emails.length > 0 && (
              <div className="text-sm mt-2">
                <strong>Emails:</strong> {startup.enrichment.emails.join(', ')}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

# CURL EXAMPLES

## Search Enriched Startups

curl -X GET "http://localhost:8000/startups/enriched/search?query=AI&enrichment_type=tech_stack&limit=10"

## Get Startup Enrichment

curl -X GET "http://localhost:8000/startups/startup_123/enrichment"

## Get Statistics

curl -X GET "http://localhost:8000/startups/enrichment/stats"

## Find by Email

curl -X POST "http://localhost:8000/startups/enrichment/by-name" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "email",
    "field_value": "@company.com",
    "limit": 10
  }'

## Find by Technology

curl -X POST "http://localhost:8000/startups/enrichment/by-name" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "tech",
    "field_value": "React",
    "limit": 20
  }'

## Find by Person

curl -X POST "http://localhost:8000/startups/enrichment/by-name" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "person",
    "field_value": "John Doe",
    "limit": 10
  }'
"""

if __name__ == "__main__":
    print(EXAMPLES)
