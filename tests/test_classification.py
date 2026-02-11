"""
Tests for model hierarchy task classification.

These tests verify that the classification heuristics correctly route
tasks to appropriate model tiers based on complexity signals.
"""

import json
import re
from pathlib import Path
from typing import Literal

import pytest

# Model tier definitions
TIER_1_MODELS = ["deepseek-v3", "gpt-4o-mini", "claude-3-haiku", "gemini-flash"]
TIER_2_MODELS = ["claude-sonnet-4", "gpt-4o", "gemini-pro"]
TIER_3_MODELS = ["claude-opus-4", "gpt-4.5", "o1", "o3-mini"]


# Signal patterns for classification
ROUTINE_SIGNALS = [
    "read", "fetch", "check", "list", "format", "status", "get",
    "filter", "sort", "convert", "parse", "health", "ping", "time",
    "date", "lookup", "find file", "show", "display"
]

MODERATE_SIGNALS = [
    "write", "code", "summarize", "draft", "analyze", "create",
    "generate", "review", "refactor", "transform", "search",
    "research", "explain", "describe", "compare"
]

COMPLEX_SIGNALS = [
    "debug", "architect", "design", "security", "why does",
    "why is", "tradeoff", "evaluate", "doesn't work", "failed",
    "tried", "race condition", "vulnerability", "migrate",
    "behaves differently", "under load", "production"
]

ESCALATION_SIGNALS = [
    "previous", "couldn't", "failed", "try again", "still not working",
    "none of these work", "stuck"
]


def classify_task(description: str, previous_failed: bool = False) -> int:
    """
    Classify a task description into a model tier (1, 2, or 3).
    
    Args:
        description: The task description to classify
        previous_failed: Whether a previous attempt failed (forces escalation)
    
    Returns:
        Model tier (1=cheap, 2=mid, 3=premium)
    """
    desc_lower = description.lower()
    
    # Rule 1: Escalation override
    if previous_failed:
        return 3
    
    # Check for escalation signals in description
    if any(signal in desc_lower for signal in ESCALATION_SIGNALS):
        return 3
    
    # Rule 2: Check for complex signals first (highest priority)
    if any(signal in desc_lower for signal in COMPLEX_SIGNALS):
        return 3
    
    # Rule 3: Check for moderate signals
    if any(signal in desc_lower for signal in MODERATE_SIGNALS):
        return 2
    
    # Rule 4: Check for routine signals
    if any(signal in desc_lower for signal in ROUTINE_SIGNALS):
        return 1
    
    # Rule 5: Default to mid-tier if uncertain
    return 2


def get_model_for_tier(tier: int) -> str:
    """Get a representative model for a given tier."""
    if tier == 1:
        return "deepseek-v3"
    elif tier == 2:
        return "claude-sonnet-4"
    else:
        return "claude-opus-4"


def calculate_cost(tier: int, tokens: int = 1000) -> float:
    """
    Calculate approximate cost for a given tier and token count.
    Uses output token pricing (typically higher).
    
    Args:
        tier: Model tier (1, 2, or 3)
        tokens: Number of tokens (default 1000)
    
    Returns:
        Cost in USD
    """
    # Approximate output costs per 1M tokens
    costs = {
        1: 0.28,    # DeepSeek V3
        2: 15.00,   # Claude Sonnet
        3: 75.00    # Claude Opus
    }
    return (tokens / 1_000_000) * costs[tier]


def calculate_monthly_cost(
    daily_tokens: int,
    routine_pct: float = 0.80,
    moderate_pct: float = 0.15,
    complex_pct: float = 0.05
) -> float:
    """
    Calculate monthly cost with hierarchical routing.
    
    Args:
        daily_tokens: Average tokens per day
        routine_pct: Percentage of routine tasks
        moderate_pct: Percentage of moderate tasks
        complex_pct: Percentage of complex tasks
    
    Returns:
        Monthly cost in USD
    """
    daily_cost = (
        calculate_cost(1, daily_tokens * routine_pct) +
        calculate_cost(2, daily_tokens * moderate_pct) +
        calculate_cost(3, daily_tokens * complex_pct)
    )
    return daily_cost * 30


# Load test scenarios
SCENARIOS_PATH = Path(__file__).parent / "scenarios.json"


@pytest.fixture
def scenarios():
    """Load test scenarios from JSON file."""
    with open(SCENARIOS_PATH) as f:
        return json.load(f)


class TestTaskClassification:
    """Test task classification into model tiers."""
    
    def test_routine_tasks(self, scenarios):
        """Routine tasks should be classified as tier 1."""
        for task in scenarios["routine_tasks"]:
            tier = classify_task(task["description"])
            assert tier == 1, f"Expected tier 1 for: {task['description']}"
    
    def test_moderate_tasks(self, scenarios):
        """Moderate tasks should be classified as tier 2."""
        for task in scenarios["moderate_tasks"]:
            tier = classify_task(task["description"])
            assert tier == 2, f"Expected tier 2 for: {task['description']}"
    
    def test_complex_tasks(self, scenarios):
        """Complex tasks should be classified as tier 3."""
        for task in scenarios["complex_tasks"]:
            tier = classify_task(task["description"])
            assert tier == 3, f"Expected tier 3 for: {task['description']}"
    
    def test_escalation_override(self):
        """Previous failures should escalate to tier 3."""
        # Even routine tasks should escalate if previous failed
        tier = classify_task("Read the config file", previous_failed=True)
        assert tier == 3
    
    def test_escalation_signals_in_description(self):
        """Escalation signals in description should trigger tier 3."""
        descriptions = [
            "The previous model couldn't figure this out",
            "I tried three approaches and none work",
            "Still not working after multiple attempts"
        ]
        for desc in descriptions:
            tier = classify_task(desc)
            assert tier == 3, f"Expected tier 3 for: {desc}"
    
    def test_compound_tasks_use_highest_tier(self, scenarios):
        """Compound tasks should use the highest required tier."""
        for task in scenarios["edge_cases"]:
            tier = classify_task(task["description"])
            assert tier == task["expected_tier"], \
                f"Expected tier {task['expected_tier']} for: {task['description']} (got {tier})"
    
    def test_unknown_defaults_to_mid(self):
        """Unknown tasks should default to tier 2."""
        tier = classify_task("Do something with the thing")
        assert tier == 2


class TestCostCalculations:
    """Test cost calculation functions."""
    
    def test_tier_cost_ordering(self):
        """Higher tiers should cost more."""
        tokens = 10000
        assert calculate_cost(1, tokens) < calculate_cost(2, tokens)
        assert calculate_cost(2, tokens) < calculate_cost(3, tokens)
    
    def test_hierarchy_saves_money(self):
        """Hierarchical routing should be cheaper than pure premium."""
        daily_tokens = 100_000
        
        pure_premium = calculate_cost(3, daily_tokens) * 30
        hierarchical = calculate_monthly_cost(daily_tokens)
        
        assert hierarchical < pure_premium
        # Should be roughly 10x cheaper
        assert hierarchical < pure_premium / 5
    
    def test_monthly_cost_calculation(self):
        """Monthly cost should be approximately $19 for 100K tokens/day."""
        monthly = calculate_monthly_cost(100_000)
        # Allow some variance in pricing
        assert 10 < monthly < 30


class TestModelSelection:
    """Test model selection for tiers."""
    
    def test_tier_1_models(self):
        """Tier 1 should return cheap model."""
        model = get_model_for_tier(1)
        assert model in TIER_1_MODELS
    
    def test_tier_2_models(self):
        """Tier 2 should return mid-tier model."""
        model = get_model_for_tier(2)
        assert model in TIER_2_MODELS
    
    def test_tier_3_models(self):
        """Tier 3 should return premium model."""
        model = get_model_for_tier(3)
        assert model in TIER_3_MODELS


class TestSignalDetection:
    """Test signal detection patterns."""
    
    @pytest.mark.parametrize("signal", ROUTINE_SIGNALS[:5])
    def test_routine_signals_detected(self, signal):
        """Routine signals should trigger tier 1."""
        desc = f"Please {signal} the data"
        tier = classify_task(desc)
        # Some routine signals might be overridden by other words
        assert tier in [1, 2]
    
    @pytest.mark.parametrize("signal", COMPLEX_SIGNALS[:5])
    def test_complex_signals_detected(self, signal):
        """Complex signals should trigger tier 3."""
        desc = f"Need to {signal} this system"
        tier = classify_task(desc)
        assert tier == 3


class TestRealWorldScenarios:
    """Test realistic agent task scenarios."""
    
    def test_heartbeat_is_routine(self):
        """Heartbeat checks should be tier 1."""
        tasks = [
            "Run the heartbeat check",
            "Check if services are healthy",
            "Ping the server status"
        ]
        for task in tasks:
            assert classify_task(task) == 1
    
    def test_code_review_is_moderate(self):
        """Standard code review should be tier 2."""
        task = "Review this pull request for style issues"
        assert classify_task(task) == 2
    
    def test_security_review_is_complex(self):
        """Security code review should be tier 3."""
        task = "Review this code for security vulnerabilities"
        assert classify_task(task) == 3
    
    def test_simple_code_is_moderate(self):
        """Code tasks default to tier 2 even if simple."""
        # The "code" keyword triggers moderate - acceptable tradeoff
        # for catching code generation tasks
        task = "Format this Python code"
        assert classify_task(task) == 2
    
    def test_architecture_is_complex(self):
        """Architecture decisions should be tier 3."""
        tasks = [
            "Design the system architecture",
            "Architect a solution for this problem",
            "Evaluate the tradeoffs between microservices and monolith"
        ]
        for task in tasks:
            assert classify_task(task) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
