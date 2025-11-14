"""
Startup Prioritization Engine for AXA Team
Balances business priorities with personalization and discovery
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import random


class StartupPrioritizer:
    """
    Intelligent prioritization engine for startup recommendations
    """

    # Priority categories (higher score = higher priority)
    CATEGORY_WEIGHTS = {
        # Tier 1: Core Agentic Platforms (highest priority)
        "agentic_platform_enabler": 100,
        "ai_platform": 95,
        "llm_infrastructure": 90,

        # Tier 2: Agentic Solutions for AXA Use Cases
        "agentic_marketing": 85,
        "agentic_claims": 85,
        "agentic_hr": 85,
        "agentic_customer_service": 85,
        "agentic_underwriting": 85,
        "agentic_fraud_detection": 85,
        "agentic_analytics": 80,

        # Tier 3: Development & Integration
        "agentic_development": 75,
        "agentic_testing": 75,
        "legacy_modernization": 75,
        "legacy_integration": 75,
        "code_migration": 70,
        "devops_automation": 70,

        # Tier 4: Insurance-Specific
        "insurance_tech": 65,
        "insurtech": 65,
        "risk_management": 60,
        "compliance_automation": 60,

        # General categories (lower priority)
        "ai_ml": 50,
        "automation": 45,
        "saas": 40,
        "enterprise": 35,
    }

    # Keywords for automatic categorization
    CATEGORY_KEYWORDS = {
        "agentic_platform_enabler": [
            "agentic platform", "ai agents", "autonomous agents", "multi-agent",
            "agent framework", "agent orchestration", "langchain", "autogen"
        ],
        "agentic_marketing": [
            "marketing automation", "content generation", "campaign automation",
            "personalization engine", "marketing ai"
        ],
        "agentic_claims": [
            "claims automation", "claims processing", "claims ai", "automated claims"
        ],
        "agentic_hr": [
            "hr automation", "recruitment ai", "talent automation", "hr tech"
        ],
        "agentic_customer_service": [
            "customer service ai", "support automation", "chatbot", "virtual assistant"
        ],
        "agentic_development": [
            "code generation", "ai coding", "developer tools", "code assistant",
            "copilot", "code completion"
        ],
        "agentic_testing": [
            "test automation", "qa automation", "automated testing", "test generation"
        ],
        "legacy_modernization": [
            "legacy modernization", "mainframe", "cobol", "system migration"
        ],
        "legacy_integration": [
            "legacy integration", "api integration", "system integration"
        ],
        "insurance_tech": [
            "insurance", "insurtech", "policy", "underwriting", "actuarial"
        ],
    }

    # Stage diversity weights (to ensure variety)
    STAGE_WEIGHTS = {
        "Seed": 1.0,
        "Series A": 1.0,
        "Series B": 1.0,
        "Series C": 0.9,
        "Series D+": 0.8,
        "Pre-Seed": 1.1,
        "Growth": 0.8,
    }

    def __init__(self):
        self.user_preferences = {}  # user_id -> preferences

    def categorize_startup(self, startup: Dict[str, Any]) -> List[str]:
        """
        Automatically categorize a startup based on its description and metadata
        """
        categories = []

        # Combine all text fields for analysis
        text_fields = [
            startup.get("description", ""),
            startup.get("company", ""),
            " ".join(startup.get("categories", [])),
            " ".join(startup.get("technologies", [])),
            " ".join(startup.get("topics", [])),
        ]
        combined_text = " ".join(text_fields).lower()

        # Check against keywords
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    categories.append(category)
                    break

        # If no specific category found, use general categories
        if not categories:
            if "ai" in combined_text or "ml" in combined_text:
                categories.append("ai_ml")
            if "automation" in combined_text:
                categories.append("automation")
            if "saas" in combined_text or "software" in combined_text:
                categories.append("saas")

        return categories or ["general"]

    def calculate_base_score(self, startup: Dict[str, Any]) -> float:
        """
        Calculate base priority score based on categories
        """
        categories = self.categorize_startup(startup)

        # Get highest category weight
        max_score = 0
        for category in categories:
            score = self.CATEGORY_WEIGHTS.get(category, 30)
            max_score = max(max_score, score)

        return max_score

    def calculate_stage_score(self, startup: Dict[str, Any]) -> float:
        """
        Calculate score modifier based on startup stage
        """
        stage = startup.get("stage", "Unknown")
        return self.STAGE_WEIGHTS.get(stage, 1.0)

    def calculate_freshness_score(self, startup: Dict[str, Any],
                                   user_votes: List[Dict[str, Any]]) -> float:
        """
        Boost startups the user hasn't seen yet
        """
        startup_id = startup.get("id")
        voted_ids = {vote.get("startupId") for vote in user_votes}

        # Strong boost for unseen startups
        return 1.5 if startup_id not in voted_ids else 1.0

    def calculate_personalization_score(self, startup: Dict[str, Any],
                                        user_votes: List[Dict[str, Any]]) -> float:
        """
        Calculate personalization based on user's voting history
        """
        if not user_votes:
            return 1.0  # No personalization yet

        # Analyze user preferences
        liked_categories = set()
        liked_stages = set()
        liked_techs = set()

        for vote in user_votes:
            if vote.get("interested"):
                # Would need to fetch startup details from vote.startupId
                # For now, simplified version
                pass

        # Match startup against preferences
        score_modifier = 1.0

        # Boost if matches user preferences
        startup_categories = self.categorize_startup(startup)
        if any(cat in liked_categories for cat in startup_categories):
            score_modifier += 0.3

        if startup.get("stage") in liked_stages:
            score_modifier += 0.2

        return score_modifier

    def calculate_diversity_penalty(self, startup: Dict[str, Any],
                                    recently_shown: List[Dict[str, Any]]) -> float:
        """
        Penalize startups too similar to recently shown ones
        """
        if not recently_shown:
            return 1.0

        penalty = 1.0
        startup_categories = set(self.categorize_startup(startup))
        startup_stage = startup.get("stage")

        for recent in recently_shown[-5:]:  # Check last 5
            recent_categories = set(self.categorize_startup(recent))
            recent_stage = recent.get("stage")

            # Penalize if too similar
            category_overlap = len(startup_categories & recent_categories)
            if category_overlap > 0:
                penalty *= 0.9

            if startup_stage == recent_stage:
                penalty *= 0.95

        return penalty

    def calculate_final_score(self, startup: Dict[str, Any],
                             user_votes: List[Dict[str, Any]],
                             recently_shown: List[Dict[str, Any]],
                             position: int) -> float:
        """
        Calculate final priority score combining all factors
        """
        # Base score from category
        base_score = self.calculate_base_score(startup)

        # Stage diversity
        stage_score = self.calculate_stage_score(startup)

        # Freshness (haven't seen yet)
        freshness_score = self.calculate_freshness_score(startup, user_votes)

        # Personalization
        personalization_score = self.calculate_personalization_score(startup, user_votes)

        # Diversity penalty
        diversity_penalty = self.calculate_diversity_penalty(startup, recently_shown)

        # Add randomness for exploration (10% of score)
        exploration_factor = random.uniform(0.9, 1.1)

        # Combine all factors
        final_score = (
            base_score *
            stage_score *
            freshness_score *
            personalization_score *
            diversity_penalty *
            exploration_factor
        )

        # First 10 startups: ensure variety
        if position < 10:
            # Boost diversity for initial batch
            final_score *= (1.0 + (position * 0.05))  # Small boost for variety

        return final_score

    def prioritize_startups(self,
                           all_startups: List[Dict[str, Any]],
                           user_votes: List[Dict[str, Any]] = None,
                           limit: int = 50) -> List[Dict[str, Any]]:
        """
        Main prioritization function
        Returns startups sorted by priority
        """
        user_votes = user_votes or []
        recently_shown = []
        scored_startups = []

        # Score each startup
        for idx, startup in enumerate(all_startups):
            score = self.calculate_final_score(
                startup,
                user_votes,
                recently_shown,
                idx
            )

            scored_startups.append({
                "startup": startup,
                "score": score,
                "categories": self.categorize_startup(startup),
                "position": idx
            })

        # Sort by score (descending)
        scored_startups.sort(key=lambda x: x["score"], reverse=True)

        # Apply final diversity pass for top 10
        top_startups = self._ensure_top10_diversity(scored_startups[:20])
        remaining = scored_startups[20:]

        # Combine and return
        final_list = top_startups + remaining

        # Return only the startup objects
        return [item["startup"] for item in final_list[:limit]]

    def _ensure_top10_diversity(self, candidates: List[Dict]) -> List[Dict]:
        """
        Ensure first 10 startups have good category and stage diversity
        """
        selected = []
        seen_categories = set()
        seen_stages = set()

        # First pass: select highly scored with diversity
        for candidate in candidates:
            if len(selected) >= 10:
                break

            categories = set(candidate["categories"])
            stage = candidate["startup"].get("stage")

            # Check if adds diversity
            adds_category_diversity = not categories.issubset(seen_categories)
            adds_stage_diversity = stage not in seen_stages

            # High score or adds diversity
            if len(selected) < 3 or adds_category_diversity or adds_stage_diversity:
                selected.append(candidate)
                seen_categories.update(categories)
                seen_stages.add(stage)

        # Fill remaining slots if needed
        for candidate in candidates:
            if len(selected) >= 10:
                break
            if candidate not in selected:
                selected.append(candidate)

        return selected

    def get_startup_insights(self, startup: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get insights about a startup's categorization and priority
        """
        categories = self.categorize_startup(startup)
        base_score = self.calculate_base_score(startup)

        return {
            "categories": categories,
            "base_score": base_score,
            "priority_tier": self._get_priority_tier(base_score),
            "stage": startup.get("stage"),
        }

    def _get_priority_tier(self, score: float) -> str:
        """
        Get human-readable priority tier
        """
        if score >= 85:
            return "Top Priority (Agentic Solutions)"
        elif score >= 70:
            return "High Priority (Development & Integration)"
        elif score >= 60:
            return "Medium Priority (Insurance Tech)"
        else:
            return "Standard Priority"


# Global instance
prioritizer = StartupPrioritizer()
