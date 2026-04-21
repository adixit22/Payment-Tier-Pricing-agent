"""
test_tools.py
--------------
Offline tests that validate the pricing math WITHOUT calling the LLM.
Fast, deterministic, no API key required.

    python test_tools.py
"""

from tools import (
    quote_package,
    project_revenue,
    recommend_tier,
    lookup_tier_detail,
    list_all_bundles,
)


def assert_close(actual, expected, label):
    assert actual == expected, f"FAIL [{label}]: expected {expected}, got {actual}"
    print(f"  OK   {label}: {actual}")


def test_quote_single_hiring():
    print("\n[test] Single-tier hiring quote (Pro)")
    q = quote_package(hiring_tier="pro")
    assert_close(q["annual_total"], 3999, "Pro alone")
    assert_close(q["bundle_applied"], False, "No bundle discount on single tier")


def test_quote_bundle_flagship():
    print("\n[test] Flagship bundle (Elite + Creator Pro)")
    q = quote_package(hiring_tier="elite", creator_tier="creator_pro")
    # $11,999 + $7,999 = $19,998 list -> 20% off = $4,000 -> $15,998 final
    assert_close(q["subscription_subtotal"], 19998, "Flagship list price")
    assert_close(q["bundle_discount"], 4000, "Flagship discount")
    assert_close(q["annual_total"], 15998, "Flagship All-Access price")


def test_quote_pro_plus_creator_starter():
    print("\n[test] Pro + Creator Starter bundle")
    q = quote_package(hiring_tier="pro", creator_tier="creator_starter")
    assert_close(q["annual_total"], 5598, "Pro + Creator Starter bundle")
    assert_close(q["bundle_discount"], 1400, "Bundle discount")


def test_quote_with_extras():
    print("\n[test] Starter with 2 extra job posts")
    q = quote_package(hiring_tier="starter", extra_job_posts=2)
    # 999 + 2 * 199 = 1,397
    assert_close(q["annual_total"], 1397, "Starter + 2 extras")


def test_project_revenue():
    print("\n[test] Revenue projection")
    mix = [
        {"count": 100, "hiring_tier": "starter"},                              # 100 * 999 = 99,900
        {"count": 40,  "hiring_tier": "pro"},                                  # 40 * 3,999 = 159,960
        {"count": 15,  "hiring_tier": "elite"},                                # 15 * 11,999 = 179,985
        {"count": 5,   "hiring_tier": "elite", "creator_tier": "creator_pro"},# 5 * 15,998 = 79,990
    ]
    p = project_revenue(mix)
    expected = 99_900 + 159_960 + 179_985 + 79_990
    assert_close(p["total_annual_revenue"], expected, "Revenue projection total")
    assert_close(p["total_customers"], 160, "Customer count")


def test_recommendations():
    print("\n[test] Tier recommendations")
    assert_close(recommend_tier(annual_hires=2)["hiring_tier"], "starter", "2 hires -> Starter")
    assert_close(recommend_tier(annual_hires=8)["hiring_tier"], "pro", "8 hires -> Pro")
    assert_close(recommend_tier(annual_hires=25)["hiring_tier"], "elite", "25 hires -> Elite")
    assert_close(
        recommend_tier(annual_hires=100, needs_ats_integration=True)["hiring_tier"],
        "enterprise",
        "ATS integration -> Enterprise",
    )
    assert_close(recommend_tier(annual_campaigns=2)["creator_tier"], "creator_starter", "2 campaigns -> Creator Starter")
    assert_close(recommend_tier(annual_campaigns=10)["creator_tier"], "creator_pro", "10 campaigns -> Creator Pro")


def test_lookup():
    print("\n[test] Tier lookup")
    d = lookup_tier_detail("hiring", "elite")
    assert_close(d["annual_price"], 11999, "Elite annual price lookup")
    assert_close(d["admin_seats"], 10, "Elite admin seats")


def test_bundles():
    print("\n[test] Bundles list")
    bundles = list_all_bundles()
    assert_close(len(bundles), 5, "5 canonical bundles listed")
    flagship = [b for b in bundles if b.get("flagship")]
    assert_close(len(flagship), 1, "Exactly one flagship bundle")
    assert_close(flagship[0]["combination"], "Elite + Creator Pro", "Flagship is Elite + Creator Pro")


if __name__ == "__main__":
    test_quote_single_hiring()
    test_quote_bundle_flagship()
    test_quote_pro_plus_creator_starter()
    test_quote_with_extras()
    test_project_revenue()
    test_recommendations()
    test_lookup()
    test_bundles()
    print("\nAll tests passed.")
