"""
classification_config.py
========================
Central location for all HOT/NON-HOT classification rules.

To modify classification rules later, edit ONLY this file.
You do NOT need to touch run.py.

Sections
--------
THERAPEUTIC_AREAS       — scope used for therapeutic-area classification
HOT_CLASSIFICATION_PROMPT — the full LLM prompt for HOT/NON-HOT + news type
RELEVANCE_PROMPT_ADDENDUM — optional extra context added to the existing AI relevance prompt
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1.  THERAPEUTIC AREA SCOPE
#     Used for both relevance filtering and TA tagging on each article.
# ─────────────────────────────────────────────────────────────────────────────
THERAPEUTIC_AREAS = [
    "Autoimmunity Diagnostics",
    "Allergy Diagnostics",
    "Allergy Therapeutics",
]

# ─────────────────────────────────────────────────────────────────────────────
# 2.  HOT / NON-HOT CLASSIFICATION PROMPT
#     This prompt is sent to the LLM for every relevant article.
#     Modify the categories, examples, edge-case rules, or instructions here.
# ─────────────────────────────────────────────────────────────────────────────
HOT_CLASSIFICATION_PROMPT = """You are an expert intelligence analyst for a specialty diagnostics company.

Your task is to classify news articles about Autoimmunity Diagnostics, Allergy Diagnostics, and Allergy Therapeutics.

=== STEP 1 — THERAPEUTIC RELEVANCE ===
First confirm the article is relevant to at least one of:
- Autoimmunity Diagnostics
- Allergy Diagnostics
- Allergy Therapeutics

If NOT relevant to any of these three areas, return:
{"classification":"EXCLUDED","news_type":"Other","confidence":"Confident",
 "rationale":"Article is not relevant to the monitored therapeutic areas.",
 "therapeutic_areas":[]}

=== STEP 2 — THERAPEUTIC AREA TAGGING ===
Return one or more of these exact strings in "therapeutic_areas":
- "Autoimmunity Diagnostics"
- "Allergy Diagnostics"
- "Allergy Therapeutics"

=== STEP 3 — HOT vs NON-HOT CLASSIFICATION ===

Classify as HOT when the article reports a CONFIRMED material event:

A. PRODUCT LAUNCH
   HOT: A new diagnostic product, assay, analyzer, platform, therapy, drug,
        treatment, or technology has ACTUALLY been launched/released/commercialized.
   NON-HOT: Company PLANS to launch, INTENDS to launch, WILL launch, EXPECTS to
        launch, or IS DEVELOPING the product. Future tense = NON-HOT.

B. REGULATORY APPROVAL
   HOT: A meaningful regulatory approval has ACTUALLY BEEN GRANTED — FDA approval,
        FDA clearance, CE mark, CE-IVDR, PMDA, NMPA, or other market authorisation,
        for a relevant product or therapy.
   NON-HOT: Pending submissions, "submitted to FDA", "seeking approval", "expects
        approval", or anticipated approvals.

C. M&A / DIVESTITURE / SPIN-OFF
   HOT: CONFIRMED acquisition, merger, divestiture, spin-off, sale of business/unit,
        or portfolio restructuring involving relevant Autoimmunity/Allergy assets.
   NON-HOT: Rumoured, potential, or speculated M&A.

D. STRATEGIC PARTNERSHIP
   HOT: Material co-development agreement, licensing agreement, joint venture, major
        distribution agreement, or strategic collaboration that significantly expands
        technology, geographic reach, product portfolio, or commercial capability.
   NON-HOT: Routine customer agreements, ordinary distribution, hospital contracts,
        or small commercial wins.

E. AI / DIGITAL INITIATIVE
   HOT: Company launches or introduces a meaningful AI initiative, ML solution,
        digital diagnostic platform, decision-support tool, automation platform,
        or significant software/digital capability relevant to the monitored market.
   NON-HOT: Routine IT upgrades, website changes, internal systems, or generic
        statements about AI strategy without a concrete product/launch.

F. SIGNIFICANT FUNDING
   HOT: Series B or later funding, large strategic investment, or major capital raise
        likely to materially accelerate development/commercialisation of a relevant
        Autoimmunity/Allergy product.
   NON-HOT: Seed funding, small grants, working-capital financing, minor financing.

G. MAJOR ORGANISATIONAL / STRATEGIC SHIFT
   HOT: Company spin-off, major restructuring, divestiture, new business unit,
        major strategic realignment specifically affecting Autoimmunity/Allergy,
        or rebranding that represents a meaningful strategic shift.
   IMPORTANT: Routine CEO/CFO/CMO/board/executive appointments are NON-HOT.
        A leadership change is HOT ONLY if the article clearly states it is part
        of a major strategic restructuring or pivot directly affecting the
        monitored Autoimmunity/Allergy business.

H. MARKET-LEVEL DEVELOPMENT
   HOT: Important external development — FDA guidance, major clinical guideline
        change, reimbursement change, important policy change, or significant
        industry consolidation — with a meaningful impact on Autoimmunity
        Diagnostics, Allergy Diagnostics, or Allergy Therapeutics.
   NON-HOT: Minor regulatory updates, general public health commentary, market
        reports without a specific actionable development.

=== STEP 4 — NON-HOT CATEGORIES ===
Classify as NON-HOT when relevant but routine:
- Financial results / earnings / revenue / quarterly updates
- Routine CEO/CXO/board appointments
- Conference participation or presentation announcements
- Webinars, awards, routine corporate updates
- Routine expansion announcements, customer wins, existing product promotion
- Future product-launch plans
- Pending regulatory submissions or early-stage research

=== EDGE-CASE RULES ===
FUTURE TENSE: "will launch", "plans to launch", "expects to launch",
  "intends to introduce" → NON-HOT unless another confirmed HOT event also appears.
APPROVAL vs SUBMISSION: "FDA approved/cleared" → HOT.
  "Submitted to FDA", "seeking approval", "expects FDA approval" → NON-HOT.
M&A: Confirmed acquisition → HOT. Rumoured/potential acquisition → NON-HOT.
PARTNERSHIP: Strategic co-development/licensing/material distribution → HOT.
  Routine contract/customer deal → NON-HOT.
EXECUTIVE APPOINTMENTS: Routine appointment → NON-HOT.
  Spin-off/divestiture/major strategic restructuring → HOT.
MULTIPLE HOT CATEGORIES: Return only ONE primary news_type using this priority:
  1. Product News  2. Regulatory News  3. Merger and Acquisition
  4. Partnership   5. Digital Initiative  6. Funding
  7. Organizational News  8. Market News
UNCERTAIN: If relevant but ambiguous, make your best HOT/NON-HOT decision and
  set confidence to "Review Recommended". Do NOT automatically classify
  uncertain articles as HOT — that creates too many false alerts.

=== OUTPUT FORMAT ===
Return ONLY valid JSON, no prose, no markdown fences.

{
  "classification": "HOT" | "NON-HOT" | "EXCLUDED",
  "news_type": "Product News" | "Regulatory News" | "Merger and Acquisition" |
               "Partnership" | "Digital Initiative" | "Funding" |
               "Organizational News" | "Market News" | "Financial News" |
               "Conference News" | "Other",
  "confidence": "Confident" | "Review Recommended",
  "rationale": "<1-2 sentences explaining the classification>",
  "therapeutic_areas": ["Autoimmunity Diagnostics", "Allergy Diagnostics", "Allergy Therapeutics"]
                        (include only relevant ones; empty array if EXCLUDED)
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# 3.  NEWS-TYPE PRIORITY ORDER (used when an article qualifies for multiple)
#     Lower index = higher priority
# ─────────────────────────────────────────────────────────────────────────────
NEWS_TYPE_PRIORITY = [
    "Product News",
    "Regulatory News",
    "Merger and Acquisition",
    "Partnership",
    "Digital Initiative",
    "Funding",
    "Organizational News",
    "Market News",
    "Financial News",
    "Conference News",
    "Other",
]

# ─────────────────────────────────────────────────────────────────────────────
# 4.  ALLOWED FIELD VALUES (for validation before writing to Excel)
# ─────────────────────────────────────────────────────────────────────────────
ALLOWED_CLASSIFICATIONS = {"HOT", "NON-HOT", "EXCLUDED"}
ALLOWED_NEWS_TYPES = {
    "Product News", "Regulatory News", "Merger and Acquisition",
    "Partnership", "Digital Initiative", "Funding",
    "Organizational News", "Market News", "Financial News",
    "Conference News", "Other",
}
ALLOWED_CONFIDENCE = {"Confident", "Review Recommended"}
