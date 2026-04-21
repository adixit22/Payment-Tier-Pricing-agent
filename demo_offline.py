"""
demo_offline.py
----------------
Scripted demo that shows the TOOL LAYER in action WITHOUT calling Claude.
Useful for demoing the agent's capabilities when an API key isn't handy.
"""

from tools import quote_package, project_revenue, recommend_tier, list_all_bundles


def show(label, data):
    print(f"\n=== {label} ===")
    if isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    elif isinstance(data, list):
        for item in data:
            print(f"  - {item}")
    else:
        print(f"  {data}")


def main():
    print("Two-Track Pricing Agent, Offline Demo")
    print("=" * 60)

    print("\nSCENARIO 1: A growing startup wants a quote for Hiring Pro only.")
    show("Quote", quote_package(hiring_tier="pro"))

    print("\nSCENARIO 2: A mid-market company asks about the flagship package.")
    show("Quote", quote_package(hiring_tier="elite", creator_tier="creator_pro"))

    print("\nSCENARIO 3: Tiny nonprofit on Starter, but needs 3 extra job posts.")
    show("Quote", quote_package(hiring_tier="starter", extra_job_posts=3))

    print("\nSCENARIO 4: Year-1 projection across a realistic customer mix.")
    mix = [
        {"count": 120, "hiring_tier": "starter"},
        {"count": 55,  "hiring_tier": "pro"},
        {"count": 20,  "hiring_tier": "elite"},
        {"count": 8,   "hiring_tier": "elite", "creator_tier": "creator_pro"},
        {"count": 15,  "creator_tier": "creator_starter"},
    ]
    show("Projection", project_revenue(mix))

    print("\nSCENARIO 5: Prospect profile, 12 hires/yr, 4 campaigns/yr.")
    show("Recommendation", recommend_tier(annual_hires=12, annual_campaigns=4))

    print("\nSCENARIO 6: Full bundle catalog.")
    show("All-Access Bundles", list_all_bundles())


if __name__ == "__main__":
    main()
