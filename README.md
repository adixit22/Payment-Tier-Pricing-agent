# Two-Track Pricing Agent

![tests](https://img.shields.io/badge/tests-17%20passing-brightgreen)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

An AI agent built on the [Claude Agent SDK](https://docs.anthropic.com) that understands a two-track B2B SaaS pricing architecture and can quote prospects, project revenue, and answer sales-enablement questions in real time.

> All product names, tier names, and prices in this repository are illustrative. This is a portfolio project demonstrating agent design patterns, not a real pricing schedule.

## The problem

Imagine a B2B SaaS platform with two independently purchasable product tracks plus a bundle discount when both are purchased together. That structure creates three real pains:

- **Sales** reps spend call time doing pricing math in their heads.
- **Finance** manually models revenue projections in brittle spreadsheets.
- **New hires** have to memorize a dense pricing doc before their first pitch.

The Two-Track Pricing Agent solves all three from a single natural-language interface.

## Architecture

```
User question
    │
    ▼
Claude (LLM)  ◄──►  Tools  ◄──►  Pricing data (source of truth)
    │
    ▼
Readable answer with numbers grounded in tool output
```

The agent exposes five deterministic tools:

| Tool | Purpose |
|---|---|
| `quote_package` | Line-item quote, applies 20% bundle discount when both tracks are selected. |
| `project_revenue` | Multi-cohort revenue projection with per-cohort ARPA and blended ARPA. |
| `recommend_tier` | Rules-based tier fit from annual hires, campaigns, and ATS needs. |
| `lookup_tier_detail` | Full feature record for a single tier. |
| `list_all_bundles` | Canonical bundle catalog with list, discounted, and savings values. |

**Design principle: math lives in code, judgment lives in the model.** The LLM never invents a number. It only decides which tool to call and how to present the result.

For a visual walkthrough, open [`docs/ARCHITECTURE.html`](docs/ARCHITECTURE.html) in a browser.

## Pricing model (illustrative)

**Track 1: Hiring**

| Tier | Annual | Seats | Active posts |
|---|---|---|---|
| Starter | $999 | 1 | 1 |
| Pro | $3,999 | 5 | 3 |
| Elite | $11,999 | 10 | 5 |
| Enterprise | $25k+ | Unlimited | Unlimited |

**Track 2: Creator**

| Tier | Annual | Seats | Campaigns/mo |
|---|---|---|---|
| Creator Starter | $2,999 | 3 | 3 |
| Creator Pro | $7,999 | 7 | Unlimited |
| Enterprise | $20k+ | Unlimited | Unlimited |

**All-Access bundle (20% off both tracks)**

| Combination | List | All-Access | Savings |
|---|---|---|---|
| Starter + Creator Starter | $3,998 | $3,198 | $800 |
| Pro + Creator Starter | $6,998 | $5,598 | $1,400 |
| Pro + Creator Pro | $11,998 | $9,598 | $2,400 |
| **Elite + Creator Pro (flagship)** | **$19,998** | **$15,998** | **$4,000** |
| Elite + Creator Starter | $14,998 | $11,998 | $3,000 |

## Quickstart

```bash
git clone <your-repo-url>
cd two-track-pricing-agent

pip install -r requirements.txt
python test_tools.py          # verify pricing math, no API key needed
python demo_offline.py        # see tools in action without calling the LLM

export ANTHROPIC_API_KEY=sk-ant-...
python agent.py               # interactive REPL
python agent.py "Quote Elite + Creator Pro for a prospect"
```

## Example prompts

- "Quote the flagship All-Access package."
- "What would revenue look like if we closed 100 Starter, 40 Pro, and 20 Elite deals this year?"
- "A mid-size brand wants to hire 12 people and run 6 creator campaigns. What should they buy?"
- "Walk me through the difference between Pro and Elite on the Hiring track."

## Example output

```
$ python agent.py "Quote the flagship bundle"

Flagship All-Access package (Elite + Creator Pro):
  • Hiring: Elite              $11,999
  • Creator: Creator Pro        $7,999
  • All-Access bundle discount (20% off)   -$4,000
  --------------------------------------------------
  Annual total                 $15,998   (saves $4,000 vs list)
```

## Repository layout

```
two-track-pricing-agent/
├── agent.py                # Claude agent loop
├── tools.py                # 5 deterministic pricing tools
├── pricing_data.py         # Single source of truth for prices
├── test_tools.py           # 17 offline unit tests
├── demo_offline.py         # Scripted demo (no API key)
├── requirements.txt
├── .github/workflows/      # CI: runs tests on every push
└── docs/
    ├── ARCHITECTURE.html   # Visual architecture diagram
    └── BUILD_GUIDE.docx    # Step-by-step beginner-friendly build guide
```

## Extending the agent

Every new capability follows the same three-step pattern:

1. Add a function to `tools.py`.
2. Add its schema to `TOOL_SCHEMAS`.
3. Add unit tests to `test_tools.py`.

Good candidate extensions: churn-adjusted multi-year ARR, CRM integration for automatic prospect lookup, discount-approval workflow, scenario-based finance modeling.

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgments

Built by Ashutosh Dixit (AKD) — Product & Project Manager, MBA (Ivey Business School, 2026). Inspired by the real pricing challenges faced by early-stage B2B SaaS teams.
