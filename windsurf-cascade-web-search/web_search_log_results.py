#!/usr/bin/env python3
"""
Interactive logger for the Cascade Web Search Testing Framework.
Prompts for required and optional fields based on track, then logs
the result directly to the appropriate results CSV.

Usage:
    python web_search_log_results.py
"""

import sys
from web_search_testing_framework import CascadeTestingFramework

# --- Helpers ---

def prompt(label: str, required: bool = True, default: str = None, choices: list = None) -> str:
    """Prompt the user for a value, with optional default and choice validation."""
    choice_str = f" [{'/'.join(choices)}]" if choices else ""
    default_str = f" (default: {default})" if default else ""
    required_str = "" if required else " (optional, press Enter to skip)"

    while True:
        raw = input(f"  {label}{choice_str}{default_str}{required_str}: ").strip()

        if not raw:
            if default:
                return default
            if not required:
                return None
            print("    ✗ Required field, please enter a value.")
            continue

        if choices and raw not in choices:
            print(f"    ✗ Must be one of: {', '.join(choices)}")
            continue

        return raw

def to_int(value: str) -> int:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None

def to_float(value: str) -> float:
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None

def section(title: str):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


# --- Field collectors ---

def collect_session_fields() -> dict:
    from web_search_testing_framework import TEST_URLS

    section("Session Fields (all tracks)")

    categories = {
        "baseline":          "BASELINE TESTS",
        "structured_content": "STRUCTURED CONTENT TESTS",
        "offset_pagination": "OFFSET/PAGINATION TESTS",
        "edge_cases":        "EDGE CASE TESTS",
    }

    for category, label in categories.items():
        tests = {k: v for k, v in TEST_URLS.items() if v["category"] == category}
        print(f"\n  {label}")
        print(f"  {'─' * 56}")
        print(f"  {'ID':<8} {'Expected':>10}   Description")
        print(f"  {'─' * 56}")
        for test_id, test in tests.items():
            size = f"~{test['expected_size_kb']}KB"
            name = test["name"]
            # Truncate long names to keep table width consistent
            if len(name) > 38:
                name = name[:35] + "..."
            print(f"  {test_id:<8} {size:>10}   {name}")
    print()

    test_id = prompt("Test ID")
    while test_id not in TEST_URLS:
        print(f"    ✗ Unknown test ID. Choose from the table above.")
        test_id = prompt("Test ID")
    
    track = prompt("Track", choices=["interpreted", "raw", "explicit"])
    model_selector = prompt("Model selector", default="Hybrid Arena")
    model_observed = prompt("Model observed (e.g. Claude Sonnet 4.6 Thinking)")
    windsurf_version = prompt("Windsurf version (e.g. 1.9600.40-pro)")
    approval_required = prompt("Approval required", choices=["yes", "no", "unknown"])
    pagination_observed = prompt(
        "Pagination observed",
        choices=["yes-auto", "yes-prompted", "no", "unknown"],
    )

    return {
        "test_id": test_id,
        "track": track,
        "model_selector": model_selector,
        "model_observed": model_observed,
        "windsurf_version": windsurf_version,
        "approval_required": approval_required,
        "pagination_observed": pagination_observed,
    }

def collect_interpreted_fields() -> dict:
    section("Output Fields (interpreted/explicit track)")

    output_chars = prompt("Output chars (integer or range midpoint)", required=False)
    truncated = prompt("Truncated", choices=["yes", "no"])
    truncation_point = None
    if truncated == "yes":
        truncation_point = prompt("Truncation point (character position)", required=False)
    tokens = prompt("Estimated token count", required=False)

    return {
        "output_chars": to_int(output_chars),
        "truncated": truncated,
        "truncation_char_num": to_int(truncation_point),
        "tokens_est": to_int(tokens),
    }

def collect_raw_fields() -> dict:
    section("Tool Behavior Fields (raw track)")

    tools_used = prompt(
        "Tools used chain (e.g. read_url_content -> view_content_chunk)",
        required=False,
    )
    tools_blocked = prompt("Tools blocked", required=False)
    execution_attempts = prompt("Execution attempts (total tool calls)", required=False)

    section("Cascade Self-Reported Fields (raw track)")

    cr_output_chars = prompt("cascade_reported_output_chars", required=False)
    cr_truncated = prompt("cascade_reported_truncated", choices=["yes", "no"], required=False)
    cr_truncation_point = prompt("cascade_reported_truncation_point", required=False)
    cr_tokens_est = prompt("cascade_reported_tokens_est", required=False)
    cr_file_size = prompt("cascade_reported_file_size_bytes", required=False)
    cr_md5 = prompt("cascade_reported_md5_checksum", required=False)
    cr_lines = prompt("cascade_reported_lines", required=False)
    cr_words = prompt("cascade_reported_words", required=False)
    cr_code_blocks = prompt("cascade_reported_code_blocks", required=False)
    cr_table_rows = prompt("cascade_reported_table_rows", required=False)
    cr_headers = prompt("cascade_reported_headers", required=False)

    section("Verified Fields (raw track)")

    v_file_size = prompt("verified_file_size_bytes", required=False)
    v_md5 = prompt("verified_md5_checksum", required=False)
    v_lines = prompt("verified_total_lines", required=False)
    v_words = prompt("verified_total_words", required=False)
    v_tokens = prompt("verified_tokens", required=False)
    v_chars_per_token = prompt("verified_chars_per_token", required=False)
    v_code_blocks = prompt("verified_code_blocks", required=False)
    v_table_rows = prompt("verified_table_rows", required=False)
    v_headers = prompt("verified_headers", required=False)

    return {
        "tools_used": tools_used,
        "tools_blocked": tools_blocked,
        "execution_attempts": to_int(execution_attempts),
        "cascade_reported_output_chars": to_int(cr_output_chars),
        "cascade_reported_truncated": cr_truncated or None,
        "cascade_reported_truncation_point": to_int(cr_truncation_point),
        "cascade_reported_tokens_est": to_int(cr_tokens_est),
        "cascade_reported_file_size_bytes": to_int(cr_file_size),
        "cascade_reported_md5_checksum": cr_md5,
        "cascade_reported_lines": to_int(cr_lines),
        "cascade_reported_words": to_int(cr_words),
        "cascade_reported_code_blocks": to_int(cr_code_blocks),
        "cascade_reported_table_rows": to_int(cr_table_rows),
        "cascade_reported_headers": to_int(cr_headers),
        "verified_file_size_bytes": to_int(v_file_size),
        "verified_md5_checksum": v_md5,
        "verified_total_lines": to_int(v_lines),
        "verified_total_words": to_int(v_words),
        "verified_tokens": to_int(v_tokens),
        "verified_chars_per_token": to_float(v_chars_per_token),
        "verified_code_blocks": to_int(v_code_blocks),
        "verified_table_rows": to_int(v_table_rows),
        "verified_headers": to_int(v_headers),
    }

def collect_closing_fields() -> dict:
    section("Hypothesis and Notes (all tracks)")

    print("  Hypotheses: H1=char ceiling, H2=token ceiling, H3=structure-aware,")
    print("              H4=@web changes behavior, H5=auto-pagination via DocumentId")
    hypothesis = prompt(
        'Hypothesis match (e.g. "H1-indeterminate, H2-no, H3-indeterminate, H4-untested, H5-no")'
    )
    notes = prompt("Notes (observations, findings, tool behavior)")

    return {
        "hypothesis_match": hypothesis,
        "notes": notes,
    }

# --- Entry point ---

def main():
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║   Cascade Testing Framework — Interactive Logger         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print("\nPress Enter to skip optional fields. No quotation marks necessary.\n")

    try:
        session = collect_session_fields()
        track = session["track"]

        if track in ("interpreted", "explicit"):
            output = collect_interpreted_fields()
        else:
            output = collect_raw_fields()

        closing = collect_closing_fields()

        method_map = {
            "interpreted": "cascade-implicit",
            "raw": "cascade-implicit",
            "explicit": "cascade-explicit",
        }

        framework = CascadeTestingFramework(track=track)
        framework.log_result(
            test_id=session["test_id"],
            method=method_map[track],
            model_selector=session["model_selector"],
            model_observed=session["model_observed"],
            windsurf_version=session["windsurf_version"],
            approval_required=session["approval_required"],
            pagination_observed=session["pagination_observed"],
            hypothesis_match=closing["hypothesis_match"],
            notes=closing["notes"],
            **output,
        )

    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)

if __name__ == "__main__":
    main()