"""
tools.py
---------
Deterministic tool implementations the Claude agent can call.

Design principle: math lives in code, judgment lives in the model. The LLM
decides WHEN to call a tool; these functions decide WHAT the number is.
"""

from typing import Optional
from pricing_data import (
    HIRING_TIERS,
    CREATOR_TIERS,
    ALL_ACCESS_DISCOUNT,
    ALL_ACCESS_BUNDLES,
    get_hiring_tier,
    get_creator_tier,
)


# ---------------------------------------------------------------------------
# Tool 1: Quote a package for a single company
# ---------------------------------------------------------------------------
def quote_package(
    hiring_tier: Optional[str] = None,
    creator_tier: Optional[str] = None,
    extra_job_posts: int = 0,
) -> dict:
    """Return a line-item quote. Applies the 20% All-Access discount when
    both a Hiring tier and a Creator tier are provided. A la carte extras
    are NOT discounted."""
    lines = []
    subtotal = 0

    if hiring_tier:
        h = get_hiring_tier(hiring_tier)
        lines.append({"item": f"Hiring: {h['name']}", "amount": h["annual_price"]})
        subtotal += h["annual_price"]

        if extra_job_posts and h["extra_post_price"]:
            extras = extra_job_posts * h["extra_post_price"]
            lines.append({
                "item": f"Extra job posts ({extra_job_posts} x ${h['extra_post_price']})",
                "amount": extras,
            })

    if creator_tier:
        c = get_creator_tier(creator_tier)
        lines.append({"item": f"Creator: {c['name']}", "amount": c["annual_price"]})
        subtotal += c["annual_price"]

    discount = 0
    bundle_applied = False
    if hiring_tier and creator_tier:
        discount = round(subtotal * ALL_ACCESS_DISCOUNT)
        lines.append({
            "item": "All-Access bundle discount (20% off)",
            "amount": -discount,
        })
        bundle_applied = True

    extras_total = sum(l["amount"] for l in lines if "Extra job posts" in l["item"])
    total = subtotal - discount + extras_total

    return {
        "line_items": lines,
        "subscription_subtotal": subtotal,
        "bundle_discount": discount,
        "bundle_applied": bundle_applied,
        "extras_total": extras_total,
        "annual_total": total,
    }


# ---------------------------------------------------------------------------
# Tool 2: Revenue projection across a customer mix
# ---------------------------------------------------------------------------
def project_revenue(customer_mix: list) -> dict:
    """Project annual revenue given a list of customer cohorts."""
    cohort_results = []
    total_revenue = 0
    total_customers = 0

    for cohort in customer_mix:
        count = int(cohort.get("count", 0))
        hiring = cohort.get("hiring_tier")
        creator = cohort.get("creator_tier")
        extras = int(cohort.get("extra_job_posts_per_customer", 0))

        per_customer = quote_package(hiring, creator, extras)["annual_total"]
        cohort_revenue = per_customer * count

        cohort_results.append({
            "description": _describe_cohort(hiring, creator, extras),
            "count": count,
            "arpa": per_customer,
            "cohort_revenue": cohort_revenue,
        })
        total_revenue += cohort_revenue
        total_customers += count

    blended_arpa = round(total_revenue / total_customers) if total_customers else 0

    return {
        "cohorts": cohort_results,
        "total_customers": total_customers,
        "total_annual_revenue": total_revenue,
        "blended_arpa": blended_arpa,
    }


def _describe_cohort(hiring, creator, extras):
    parts = []
    if hiring:
        parts.append(f"Hiring:{HIRING_TIERS[hiring]['name']}")
    if creator:
        parts.append(f"Creator:{CREATOR_TIERS[creator]['name']}")
    if hiring and creator:
        parts.append("All-Access")
    if extras:
        parts.append(f"+{extras} extra posts")
    return " / ".join(parts) if parts else "Empty cohort"


# ---------------------------------------------------------------------------
# Tool 3: Recommend a tier based on company profile
# ---------------------------------------------------------------------------
def recommend_tier(
    annual_hires: int = 0,
    annual_campaigns: int = 0,
    needs_ats_integration: bool = False,
    needs_managed_campaigns: bool = False,
) -> dict:
    """Deterministic rules-based tier recommendation."""
    if needs_ats_integration or annual_hires > 50:
        hiring_rec = "enterprise"
    elif annual_hires >= 10:
        hiring_rec = "elite"
    elif annual_hires >= 4:
        hiring_rec = "pro"
    elif annual_hires >= 1:
        hiring_rec = "starter"
    else:
        hiring_rec = None

    if needs_managed_campaigns or annual_campaigns > 20:
        creator_rec = "enterprise"
    elif annual_campaigns >= 3:
        creator_rec = "creator_pro"
    elif annual_campaigns >= 1:
        creator_rec = "creator_starter"
    else:
        creator_rec = None

    rationale = []
    if hiring_rec:
        rationale.append(
            f"For {annual_hires} hires/yr, {HIRING_TIERS[hiring_rec]['name']} is the right fit: "
            f"{HIRING_TIERS[hiring_rec]['best_for']}."
        )
    if creator_rec:
        rationale.append(
            f"For {annual_campaigns} campaigns/yr, {CREATOR_TIERS[creator_rec]['name']} is the right fit: "
            f"{CREATOR_TIERS[creator_rec]['best_for']}."
        )

    return {
        "hiring_tier": hiring_rec,
        "creator_tier": creator_rec,
        "rationale": " ".join(rationale) if rationale else "No tier fits this profile.",
    }


# ---------------------------------------------------------------------------
# Tool 4: Sales-enablement lookup
# ---------------------------------------------------------------------------
def lookup_tier_detail(track: str, tier: str) -> dict:
    track = track.lower()
    if track == "hiring":
        return HIRING_TIERS.get(tier.lower(), {"error": f"Unknown hiring tier: {tier}"})
    if track in ("creator", "campaigns"):
        return CREATOR_TIERS.get(tier.lower(), {"error": f"Unknown creator tier: {tier}"})
    return {"error": f"Unknown track: {track}"}


def list_all_bundles() -> list:
    return ALL_ACCESS_BUNDLES


# ---------------------------------------------------------------------------
# Tool schemas in Anthropic tool-use format
# ---------------------------------------------------------------------------
TOOL_SCHEMAS = [
    {
        "name": "quote_package",
        "description": (
            "Generate a line-item annual price quote for a prospect. "
            "If both a hiring tier and a creator tier are provided, the 20% "
            "All-Access bundle discount is applied automatically."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "hiring_tier": {
                    "type": "string",
                    "enum": ["starter", "pro", "elite", "enterprise"],
                    "description": "Hiring track tier key, or omit if not needed.",
                },
                "creator_tier": {
                    "type": "string",
                    "enum": ["creator_starter", "creator_pro", "enterprise"],
                    "description": "Creator track tier key, or omit if not needed.",
                },
                "extra_job_posts": {
                    "type": "integer",
                    "description": "A la carte extra job posts beyond the tier allowance.",
                    "default": 0,
                },
            },
        },
    },
    {
        "name": "project_revenue",
        "description": (
            "Run a revenue projection across a mix of customer cohorts. Use when "
            "the user asks 'what if we had X customers on Pro and Y on Elite?' "
            "style questions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_mix": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "count": {"type": "integer"},
                            "hiring_tier": {"type": "string"},
                            "creator_tier": {"type": "string"},
                            "extra_job_posts_per_customer": {"type": "integer"},
                        },
                        "required": ["count"],
                    },
                }
            },
            "required": ["customer_mix"],
        },
    },
    {
        "name": "recommend_tier",
        "description": "Recommend Hiring and/or Creator tiers for a company profile.",
        "input_schema": {
            "type": "object",
            "properties": {
                "annual_hires": {"type": "integer", "default": 0},
                "annual_campaigns": {"type": "integer", "default": 0},
                "needs_ats_integration": {"type": "boolean", "default": False},
                "needs_managed_campaigns": {"type": "boolean", "default": False},
            },
        },
    },
    {
        "name": "lookup_tier_detail",
        "description": "Return the full feature/price record for a specific tier.",
        "input_schema": {
            "type": "object",
            "properties": {
                "track": {"type": "string", "enum": ["hiring", "creator"]},
                "tier": {"type": "string"},
            },
            "required": ["track", "tier"],
        },
    },
    {
        "name": "list_all_bundles",
        "description": "Return every predefined All-Access bundle combination.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


TOOL_REGISTRY = {
    "quote_package": quote_package,
    "project_revenue": project_revenue,
    "recommend_tier": recommend_tier,
    "lookup_tier_detail": lookup_tier_detail,
    "list_all_bundles": list_all_bundles,
}
