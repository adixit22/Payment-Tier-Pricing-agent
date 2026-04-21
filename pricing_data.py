"""
pricing_data.py
----------------
Structured pricing for a fictional two-track B2B SaaS platform used in this
portfolio project. All prices are illustrative and do not reflect any real
product.

The platform offers two independently purchasable tracks:
  - Hiring: for recruiters and HR managers posting jobs.
  - Creator: for marketing managers running creator campaigns.
Bundling both tracks triggers a 20% All-Access discount.
"""

HIRING_TIERS = {
    "starter": {
        "name": "Starter",
        "annual_price": 999,
        "monthly_price": 99,
        "admin_seats": 1,
        "active_job_postings": 1,
        "extra_post_price": 199,
        "outreach_messages_per_month": 0,
        "best_for": "Startups and small teams making 1 to 3 hires/yr",
    },
    "pro": {
        "name": "Pro",
        "annual_price": 3999,
        "monthly_price": 399,
        "admin_seats": 5,
        "active_job_postings": 3,
        "extra_post_price": 149,
        "outreach_messages_per_month": 40,
        "best_for": "Growing companies hiring 5 to 15 roles/yr",
    },
    "elite": {
        "name": "Elite",
        "annual_price": 11999,
        "monthly_price": 1199,
        "admin_seats": 10,
        "active_job_postings": 5,
        "extra_post_price": 99,
        "outreach_messages_per_month": 120,
        "best_for": "High-volume hiring with full network access",
    },
    "enterprise": {
        "name": "Enterprise",
        "annual_price": 25000,  # Custom / $25k+ floor
        "monthly_price": None,
        "admin_seats": None,
        "active_job_postings": None,
        "extra_post_price": 0,
        "outreach_messages_per_month": None,
        "best_for": "Large orgs, ATS integrations, custom workflows",
    },
}

CREATOR_TIERS = {
    "creator_starter": {
        "name": "Creator Starter",
        "annual_price": 2999,
        "monthly_price": 299,
        "admin_seats": 3,
        "campaigns_per_month": 3,
        "creator_outreach_per_month": 20,
        "best_for": "Brands testing creator partnerships (1 to 2 campaigns/yr)",
    },
    "creator_pro": {
        "name": "Creator Pro",
        "annual_price": 7999,
        "monthly_price": 799,
        "admin_seats": 7,
        "campaigns_per_month": None,  # Unlimited
        "creator_outreach_per_month": 120,
        "best_for": "Brands running ongoing creator programs at scale",
    },
    "enterprise": {
        "name": "Enterprise",
        "annual_price": 20000,  # Custom / $20k+ floor
        "monthly_price": None,
        "admin_seats": None,
        "campaigns_per_month": None,
        "creator_outreach_per_month": None,
        "best_for": "Agencies and large brands needing managed campaigns",
    },
}

ALL_ACCESS_DISCOUNT = 0.20  # 20% off when both tracks are purchased

# Canonical All-Access bundle catalog
ALL_ACCESS_BUNDLES = [
    {"combination": "Starter + Creator Starter", "list_price": 3998,  "all_access": 3198,  "savings": 800},
    {"combination": "Pro + Creator Starter",     "list_price": 6998,  "all_access": 5598,  "savings": 1400},
    {"combination": "Pro + Creator Pro",         "list_price": 11998, "all_access": 9598,  "savings": 2400},
    {"combination": "Elite + Creator Pro",       "list_price": 19998, "all_access": 15998, "savings": 4000, "flagship": True},
    {"combination": "Elite + Creator Starter",   "list_price": 14998, "all_access": 11998, "savings": 3000},
]


def get_hiring_tier(tier_key: str) -> dict:
    return HIRING_TIERS[tier_key.lower()]


def get_creator_tier(tier_key: str) -> dict:
    return CREATOR_TIERS[tier_key.lower()]
