#!/usr/bin/env python3
"""
test_classification.py
======================
Unit tests for the HOT/NON-HOT classification logic.

Run locally:
    pip install -r requirements.txt
    export GROQ_API_KEY=<your key>
    python test_classification.py

If GROQ_API_KEY is not set, the test runs in keyword-only mode
(classification results will use the fallback logic and may differ).
"""

import json
import os
import sys
import time

# Make sure we can import from the project root
sys.path.insert(0, os.path.dirname(__file__))

from run import _classify_article_hot, classify_hot, classify_news_type

# ─── Test cases ──────────────────────────────────────────────────────────────
TEST_CASES = [
    {
        "id": 1,
        "headline": "Company receives FDA clearance for new allergy assay",
        "company": "QuidelOrtho",
        "expected_classification": "HOT",
        "expected_news_type": "Regulatory News",
        "description": "FDA clearance granted — confirmed regulatory milestone",
    },
    {
        "id": 2,
        "headline": "Company plans to launch allergy analyzer next year",
        "company": "Siemens Healthineers",
        "expected_classification": "NON-HOT",
        "expected_news_type": "Product News",
        "description": "Future-tense launch — not yet confirmed",
    },
    {
        "id": 3,
        "headline": "Company launches new autoimmune diagnostic panel",
        "company": "Bio-Rad",
        "expected_classification": "HOT",
        "expected_news_type": "Product News",
        "description": "Actual product launch confirmed",
    },
    {
        "id": 4,
        "headline": "Company reports Q2 revenue growth of 12 percent",
        "company": "Roche Diagnostics",
        "expected_classification": "NON-HOT",
        "expected_news_type": "Financial News",
        "description": "Routine financial results",
    },
    {
        "id": 5,
        "headline": "New CEO appointed at allergy diagnostics firm",
        "company": "HYCOR Biomedical",
        "expected_classification": "NON-HOT",
        "expected_news_type": "Organizational News",
        "description": "Routine executive appointment",
    },
    {
        "id": 6,
        "headline": "Company spins off immunodiagnostics division into separate entity",
        "company": "Danaher Corporation",
        "expected_classification": "HOT",
        "expected_news_type_options": ["Merger and Acquisition", "Organizational News"],
        "description": "Confirmed spin-off — major strategic event",
    },
    {
        "id": 7,
        "headline": "Company signs major licensing agreement for allergy therapeutic",
        "company": "ALK",
        "expected_classification": "HOT",
        "expected_news_type": "Partnership",
        "description": "Material licensing/partnership deal",
    },
    {
        "id": 8,
        "headline": "Company will present allergy study at upcoming EAACI congress",
        "company": "Stallergenes Greer",
        "expected_classification": "NON-HOT",
        "expected_news_type": "Conference News",
        "description": "Routine conference presentation",
    },
    {
        "id": 9,
        "headline": "FDA accepts regulatory submission for allergy immunotherapy",
        "company": "DBV Technologies",
        "expected_classification": "NON-HOT",
        "expected_news_type": "Regulatory News",
        "description": "Submission accepted, not approved",
    },
    {
        "id": 10,
        "headline": "FDA approves allergy therapy for new pediatric indication",
        "company": "Aimmune Therapeutics",
        "expected_classification": "HOT",
        "expected_news_type": "Regulatory News",
        "description": "FDA approval granted — confirmed regulatory milestone",
    },
]

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def run_llm_tests(api_key: str, model: str) -> list:
    print(f"\n{BOLD}Running {len(TEST_CASES)} test cases via LLM ({model})...{RESET}\n")
    results = []

    for tc in TEST_CASES:
        print(f"Test {tc['id']}: {tc['headline'][:70]}")
        result = _classify_article_hot(
            headline  = tc["headline"],
            company   = tc["company"],
            api_key   = api_key,
            model     = model,
        )
        classification = result["classification"]
        news_type      = result["news_type"]
        confidence     = result["confidence"]
        rationale      = result["rationale"]
        ta             = result["therapeutic_areas"]

        expected_c = tc["expected_classification"]
        # news_type may be one of multiple acceptable values
        expected_nt_options = tc.get("expected_news_type_options") or [tc.get("expected_news_type","")]

        c_pass  = classification == expected_c
        nt_pass = news_type in expected_nt_options or not expected_nt_options[0]

        status = f"{GREEN}PASS{RESET}" if (c_pass and nt_pass) else f"{RED}FAIL{RESET}"

        print(f"  {status} | Classification: {classification} (expected: {expected_c}) | "
              f"Type: {news_type} | Confidence: {confidence}")
        print(f"  Therapeutic Areas: {ta or '(none — would be excluded)'}")
        print(f"  Rationale: {rationale}")
        if not c_pass:
            print(f"  {RED}Classification mismatch: got {classification}, expected {expected_c}{RESET}")
        if not nt_pass:
            print(f"  {YELLOW}News-type mismatch: got {news_type}, expected one of {expected_nt_options}{RESET}")
        print()

        results.append({
            "id": tc["id"],
            "headline": tc["headline"],
            "classification_pass": c_pass,
            "newstype_pass": nt_pass,
            "result": result,
        })
        time.sleep(0.5)  # small pause between calls

    return results


def run_keyword_tests() -> list:
    """Fallback: test the keyword-based classifier (used when AI is unavailable)."""
    print(f"\n{BOLD}Running {len(TEST_CASES)} test cases via keyword fallback...{RESET}\n")
    results = []
    for tc in TEST_CASES:
        classification = classify_hot(tc["headline"])
        news_type      = classify_news_type(tc["headline"])
        expected_c     = tc["expected_classification"]
        # Keyword fallback uses NON-HOT (not Non-Hot) after our fix
        c_pass = classification == expected_c
        status = f"{GREEN}PASS{RESET}" if c_pass else f"{YELLOW}MISMATCH (keyword-only){RESET}"
        print(f"Test {tc['id']}: {tc['headline'][:60]}")
        print(f"  {status} | Classification: {classification} | Type: {news_type}")
        results.append({"id": tc["id"], "classification_pass": c_pass, "newstype_pass": True})
    return results


def print_summary(results: list):
    passed = sum(1 for r in results if r["classification_pass"])
    total  = len(results)
    colour = GREEN if passed == total else (YELLOW if passed >= total * 0.7 else RED)
    print(f"\n{BOLD}{'='*50}")
    print(f"Results: {colour}{passed}/{total} classification tests passed{RESET}")
    failed = [r for r in results if not r["classification_pass"]]
    if failed:
        print(f"\nFailed test IDs: {[r['id'] for r in failed]}")
    print(f"{'='*50}{RESET}\n")


if __name__ == "__main__":
    api_key = os.getenv("GROQ_API_KEY")
    model   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if api_key:
        results = run_llm_tests(api_key, model)
    else:
        print(f"{YELLOW}GROQ_API_KEY not set — running keyword-only fallback tests.{RESET}")
        print("Set GROQ_API_KEY to test the LLM classifier.\n")
        results = run_keyword_tests()

    print_summary(results)
    # Exit 1 if any classification test fails (for CI)
    sys.exit(0 if all(r["classification_pass"] for r in results) else 1)
