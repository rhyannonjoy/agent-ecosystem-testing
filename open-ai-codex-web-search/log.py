#!/usr/bin/env python3
"""
Interactive logger for the Codex Web Search Testing Framework.
Prompts for required and optional fields based on track, then logs
the result directly to the appropriate results CSV.

Usage:
    python log.py
"""

import sys
from framework import CodexTestingFramework, TEST_URLS, TRACKS

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
    section("Session Fields (all tracks)")

    categories = {
        "baseline":           "BASELINE TESTS",
        "structured_content": "STRUCTURED CONTENT TESTS",
        "offset_pagination":  "OFFSET/PAGINATION TESTS",
        "edge_cases":         "EDGE CASE TESTS",
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
            if len(name) > 38:
                name = name[:35] + "..."
            print(f"  {test_id:<8} {size:>10}   {name}")
    print()

    test_id = prompt("Test ID")
    while test_id not in TEST_URLS:
        print("    ✗ Unknown test ID. Choose from the table above.")
        test_id = prompt("Test ID")

    print(f"\n  Tracks:")
    for track_id, info in TRACKS.items():
        ws = "workspace" if info["workspace"] else "no workspace"
        print(f"    {track_id:<28}  {info['method']:<18}  {info['surface']}  ({ws})")
    print()

    track = prompt("Track", choices=list(TRACKS.keys()))

    permission_level = prompt("Permission level", choices=["default", "auto-review", "full-access"], default="default")
    model_observed = prompt("Model observed (LLM reported in output, if any)")
    model_intelligence_level = prompt(
        "Intelligence level",
        choices=["low", "medium", "high", "auto"],
        default="medium",
    )
    codex_version = prompt("Codex version (e.g. 1.0.0)")
    tools_named = prompt(
        "Tools named in output (e.g. web, web.open, curl)",
        required=False,
    )
    workspace_substitution = prompt(
        "Workspace substitution observed",
        choices=["yes", "no", "unknown"],
        default="no",
    )

    return {
        "test_id": test_id,
        "track": track,
        "permission_level": permission_level,
        "model_observed": model_observed,
        "model_intelligence_level": model_intelligence_level,
        "codex_version": codex_version,
        "tools_named": tools_named,
        "workspace_substitution": workspace_substitution,
    }

def collect_interpreted_fields() -> dict:
    section("Output Fields (interpreted track — T1 or T2)")

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
    section("Tool Behavior Fields (raw track — T3 or T4)")

    tools_used = prompt(
        "Tools used chain (e.g. web -> web.open)",
        required=False,
    )
    tools_blocked = prompt("Tools blocked", required=False)
    execution_attempts = prompt("Execution attempts (total tool calls)", required=False)

    section("Agent Self-Reported Fields (raw track)")

    ar_output_chars = prompt("agent_reported_output_chars", required=False)
    ar_truncated = prompt(
        "agent_reported_truncated", choices=["yes", "no"], required=False
    )
    ar_truncation_point = prompt("agent_reported_truncation_point", required=False)
    ar_tokens_est = prompt("agent_reported_tokens_est", required=False)
    ar_file_size = prompt("agent_reported_file_size_bytes", required=False)
    ar_md5 = prompt("agent_reported_md5_checksum", required=False)
    ar_lines = prompt("agent_reported_lines", required=False)
    ar_words = prompt("agent_reported_words", required=False)
    ar_code_blocks = prompt("agent_reported_code_blocks", required=False)
    ar_table_rows = prompt("agent_reported_table_rows", required=False)
    ar_headers = prompt("agent_reported_headers", required=False)

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
        "agent_reported_output_chars": to_int(ar_output_chars),
        "agent_reported_truncated": ar_truncated or None,
        "agent_reported_truncation_point": to_int(ar_truncation_point),
        "agent_reported_tokens_est": to_int(ar_tokens_est),
        "agent_reported_file_size_bytes": to_int(ar_file_size),
        "agent_reported_md5_checksum": ar_md5,
        "agent_reported_lines": to_int(ar_lines),
        "agent_reported_words": to_int(ar_words),
        "agent_reported_code_blocks": to_int(ar_code_blocks),
        "agent_reported_table_rows": to_int(ar_table_rows),
        "agent_reported_headers": to_int(ar_headers),
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
    print("              H4=surface context changes ceiling, H5=auto-chunking above ceiling")
    hypothesis = prompt(
        'Hypothesis match (e.g. "H1-indeterminate, H2-no, H3-indeterminate, H4-untested, H5-no")'
    )
    notes = prompt("Notes (observations, findings, tool behavior, workspace interference)")

    return {
        "hypothesis_match": hypothesis,
        "notes": notes,
    }


# --- Entry point ---

def main():
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║   Codex Testing Framework — Interactive Logger           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print("\nPress Enter to skip optional fields. No quotation marks necessary.\n")

    try:
        session = collect_session_fields()
        track = session["track"]
        track_info = TRACKS[track]
        is_raw = track_info["method"] == "raw"

        if is_raw:
            output = collect_raw_fields()
        else:
            output = collect_interpreted_fields()

        closing = collect_closing_fields()

        framework = CodexTestingFramework(track=track)
        framework.log_result(
            test_id=session["test_id"],
            permission_level=session["permission_level"],
            model_observed=session["model_observed"],
            model_intelligence_level=session["model_intelligence_level"],
            codex_version=session["codex_version"],
            tools_named=session["tools_named"],
            workspace_substitution=session["workspace_substitution"],
            hypothesis_match=closing["hypothesis_match"],
            notes=closing["notes"],
            **output,
        )

    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)

if __name__ == "__main__":
    main()