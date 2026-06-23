#!/usr/bin/env python3
"""
Interactive Codex Hypotheses Assessor
=======================================

A lightweight terminal questionnaire that turns observations from a Codex
agent session into a standardized ``hypothesis_match`` string.

This is designed to remove the bottleneck in the assessment step: you look at
the agent's chat output and tool behavior, then answer a short set of
questions.  The script maps the answers to H1–H5 support values in the format
``framework.py`` and ``analyze.py`` expect::

    H1-partially, H2-no, H3-indeterminate, H4-untested, H5-partially

Run it before logging the result with ``log.py`` or ``framework.py``::

    python scripts/assess_hypotheses.py

The script is intentionally small and focused: it does not log results,
does not modify CSVs, and does not automate data collection.  It only
produces the hypothesis string for the analyst to paste into ``log.py`` or
``framework.py``.

Design notes
------------
* The H1–H5 decision functions are pure: they accept a small observation dict
  and return ``(value, rationale)``.  This keeps the logic testable and makes
  it easy to add a non-interactive CSV batch mode later.
* The interactive layer (``collect_*`` functions) mirrors ``log.py``.
* Answers are conservative: "indeterminate" / "untested" is preferred when
  the observation is ambiguous.
"""

try:
    from framework import TEST_URLS
except ImportError:
    TEST_URLS = {}

from datetime import datetime
from pathlib import Path
import sys


# ---------------------------------------------------------------------------
# Expected-size helper
# ---------------------------------------------------------------------------
def expected_chars_for_test(test_id: str) -> int | None:
    """Return expected character count from the test corpus, if known."""
    if TEST_URLS and test_id in TEST_URLS:
        return TEST_URLS[test_id]["expected_size_kb"] * 1024
    return None


# ---------------------------------------------------------------------------
# Prompt helpers (mirror log.py style)
# ---------------------------------------------------------------------------
def prompt(label: str, required: bool = True, default: str = None, choices: list = None) -> str:
    choice_str = f" [{ '/'.join(choices) }]" if choices else ""
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

        if choices:
            lower_choices = [c.lower() for c in choices]
            lower_raw = raw.lower()
            if lower_raw in lower_choices:
                idx = lower_choices.index(lower_raw)
                return choices[idx]
            prefixes = [c for c in choices if c.lower().startswith(lower_raw)]
            if len(prefixes) == 1:
                return prefixes[0]
            print(f"    ✗ Must be one of: {', '.join(choices)}")
            continue

        return raw


def to_int(value):
    if not value:
        return None
    try:
        return int(value.replace(",", ""))
    except ValueError:
        return None


def confirm(label: str, default: bool = False) -> bool:
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        raw = input(f"  {label}{suffix}: ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("    ✗ Please answer y or n.")


def section(title: str):
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}")


# ---------------------------------------------------------------------------
# Pure decision functions: observation dict -> (value, rationale)
# ---------------------------------------------------------------------------
def assess_h1(obs: dict) -> tuple[str, str]:
    """H1: Character-based truncation at a fixed ceiling."""
    size_relation = obs.get("size_relation", "unclear")
    cap_signal = obs.get("cap_signal", False)
    repeatable = obs.get("repeatable_ceiling", False)
    reported = obs.get("reported_chars")
    expected = obs.get("expected_chars")

    size_detail = ""
    if reported and expected:
        size_detail = f" Agent reported {reported:,} chars vs expected {expected:,}."
    elif reported == 0:
        size_detail = " Agent did not report a character count."

    if size_relation == "full":
        return (
            "no",
            f"Output reached the expected size; no fixed-character ceiling is evident.{size_detail}",
        )

    if cap_signal and repeatable:
        return (
            "yes",
            f"Output is capped well below page size, a fixed cap is reported, and the ceiling is repeatable.{size_detail}",
        )

    if cap_signal or repeatable or size_relation == "much smaller":
        return (
            "partially",
            f"Output appears capped or smaller than expected, but the ceiling is not clearly fixed across runs.{size_detail}",
        )

    return (
        "indeterminate",
        f"Truncation behavior is unclear; cannot distinguish a fixed character ceiling from other factors.{size_detail}",
    )


def assess_h2(obs: dict) -> tuple[str, str]:
    """H2: Token-based truncation."""
    token_count = obs.get("token_count") or 0
    output_chars = obs.get("output_chars") or 0

    if not token_count or not output_chars:
        return "indeterminate", "No token count available; token-based ceiling cannot be evaluated."

    ratio = output_chars / token_count if token_count else 0
    near_threshold = (
        1_800 <= token_count <= 2_200
        or 7_200 <= token_count <= 8_800
        or 28_800 <= token_count <= 35_200
        or 115_200 <= token_count <= 140_800
        or token_count >= 180_000
    )

    if near_threshold and 3.0 <= ratio <= 5.0:
        return (
            "yes",
            f"Token count ({token_count:,}) is near a known threshold and chars/token ratio ({ratio:.2f}) is consistent with token-based truncation.",
        )

    if 2.0 <= ratio <= 6.0:
        return (
            "partially",
            f"Token data exists and ratio ({ratio:.2f}) is plausible, but the count is not cleanly aligned with a standard ceiling.",
        )

    return (
        "no",
        f"Chars/token ratio ({ratio:.2f}) or token count ({token_count:,}) is not consistent with a token ceiling.",
    )


def assess_h3(obs: dict) -> tuple[str, str]:
    """H3: Structure-aware truncation."""
    truncated = obs.get("truncated", "no")

    if truncated == "no":
        return "yes", "No truncation reported; Markdown/HTML structure is intact by default."

    boundary = obs.get("boundary", "not_sure")

    if boundary == "clean_boundary":
        return (
            "yes",
            "Truncation landed on a clean structural boundary (heading, paragraph, code fence, tag, or table row).",
        )

    if boundary in ("mid_word", "mid_link", "mid_code_block", "mid_table"):
        return (
            "no",
            f"Truncation cut {boundary.replace('_', '-')} — structure was not preserved.",
        )

    return (
        "partially",
        "Truncation is reported but the exact boundary is unclear or mixed.",
    )


def assess_h4(obs: dict) -> tuple[str, str]:
    """H4: Surface context changes retrieval ceiling."""
    if not obs.get("other_surface_run", False):
        return "untested", "No cross-surface comparison available."

    if obs.get("surfaces_same", False):
        return "no", "Both surfaces produced comparable output; surface context did not change the ceiling."

    if obs.get("meaningfully_different", False):
        return "yes", "Output size or truncation tier differs meaningfully between surfaces."

    return "partially", "Some cross-surface difference exists but is small or ambiguous."


def assess_h5(obs: dict) -> tuple[str, str]:
    """H5: Agent auto-chunks above the truncation ceiling."""
    import re

    tools_used = obs.get("tools_used", "") or ""
    tools_named = obs.get("tools_named", "") or ""
    attempts = obs.get("execution_attempts") or 0
    chunking = obs.get("chunking", False)

    combined = f"{tools_used} {tools_named}".strip().lower()
    multi_step = "->" in tools_used

    # View markers like turn0view0 / turn1view0 indicate multiple page views.
    views = re.findall(r"turn\d+view\d+", combined)
    # Repeated web-family tool calls (web, web.open, web.run).
    web_calls = re.findall(r"\bweb(?:\.open|\.run|_run)?\b", combined)
    # Distinct tools named or chained.
    distinct_tools = {t.strip() for t in re.split(r"[\s,;->]+", combined) if t.strip()}

    has_view_pagination = len(views) >= 2
    has_repeated_web = len(web_calls) >= 2
    many_attempts = bool(attempts) and attempts >= 3

    if multi_step and chunking:
        return (
            "yes",
            f"Multi-step tool chain observed ('{tools_used.strip()}') with explicit chunking/pagination behavior.",
        )

    if has_view_pagination or has_repeated_web or chunking or many_attempts or len(distinct_tools) >= 3:
        return (
            "partially",
            "Some pagination or multi-tool signal present, but not extensive auto-chunking.",
        )

    return "no", "Single tool call or simple retrieval path; no auto-chunking signal."


# ---------------------------------------------------------------------------
# Interactive observation collectors
# ---------------------------------------------------------------------------
def collect_h1_observations(test_id: str) -> dict:
    section("H1 — Character-based truncation at a fixed ceiling")
    print("  H1 asks whether the truncation is a fixed character/line ceiling.")
    print("  The agent report may give an exact count, an estimate, or nothing.")

    expected_chars = expected_chars_for_test(test_id)
    if expected_chars:
        print(f"  Expected size for {test_id}: ~{expected_chars:,} characters")
    else:
        expected_chars = to_int(
            prompt("Expected page size in characters", required=False)
        )

    reported_raw = prompt(
        "Agent-reported output characters (integer, range midpoint, or 0 if none/unclear)"
    )
    reported_chars = to_int(reported_raw)

    size_relation = "unclear"
    if reported_chars and expected_chars:
        ratio = reported_chars / expected_chars
        if ratio >= 0.85:
            size_relation = "full"
        elif ratio >= 0.30:
            size_relation = "smaller"
        else:
            size_relation = "much smaller"
        print(f"  → reported/expected ≈ {ratio:.2f} ({size_relation})")
    elif reported_chars == 0:
        size_relation = "unclear"

    cap_signal = confirm(
        "Did the agent explicitly mention a cap, ceiling, wordlim, line limit, or fixed window?"
    )
    repeatable = confirm(
        "Across repeated runs, does the output land near the same ceiling?",
        default=False,
    )

    return {
        "size_relation": size_relation,
        "cap_signal": cap_signal,
        "repeatable_ceiling": repeatable,
        "reported_chars": reported_chars,
        "expected_chars": expected_chars,
    }


def collect_h2_observations(output_chars: int = None) -> dict:
    section("H2 — Token-based truncation")

    has_tokens = confirm("Was a token count reported by the agent or calculable with tiktoken?")
    if not has_tokens:
        return {}

    return {
        "token_count": to_int(prompt("Token count", required=False)),
        "output_chars": output_chars,
    }


def collect_h3_observations() -> dict:
    section("H3 — Structure-aware truncation")

    truncated = prompt(
        "Was the content truncated?",
        choices=["yes", "no", "mixed", "implicit"],
        default="no",
    )

    if truncated == "no":
        return {"truncated": "no"}

    return {
        "truncated": truncated,
        "boundary": prompt(
            "If truncated, where did it cut?",
            choices=[
                "clean_boundary",
                "mid_word",
                "mid_link",
                "mid_code_block",
                "mid_table",
                "not_sure",
            ],
            default="not_sure",
        ),
    }


def collect_h4_observations() -> dict:
    section("H4 — Surface context changes retrieval ceiling")

    if not confirm("Have you run the complementary surface (Codex IDE ↔ VS Code-Codex) for this same test?"):
        return {"other_surface_run": False}

    same = confirm("Did both surfaces return roughly the same output size and truncation behavior?")
    if same:
        return {"other_surface_run": True, "surfaces_same": True}

    return {
        "other_surface_run": True,
        "surfaces_same": False,
        "meaningfully_different": confirm(
            "Was the difference meaningful (>20% or a different truncation tier)?"
        ),
    }


def collect_h5_observations() -> dict:
    section("H5 — Agent auto-chunks above the truncation ceiling")

    return {
        "tools_used": prompt(
            "Observed tool chain / views (e.g. web -> web.open -> curl, or turn0view0 turn1view0)",
            required=False,
        )
        or "",
        "tools_named": prompt(
            "Tools named by agent (if different from chain above)", required=False
        )
        or "",
        "execution_attempts": to_int(
            prompt("Total execution attempts / tool calls", required=False)
        ),
        "chunking": confirm(
            "Did the agent visibly paginate, fetch tail/offset sections, fill gaps, or reason about chunking?"
        ),
    }


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------
def build_string(values: dict) -> str:
    return ", ".join(f"H{i}-{values[f'H{i}']['value']}" for i in range(1, 6))


def build_rationale(values: dict) -> str:
    parts = []
    for i in range(1, 6):
        key = f"H{i}"
        parts.append(f"{key}={values[key]['value']}: {values[key]['rationale']}")
    return " ".join(parts)


HYPOTHESIS_LABELS = {
    "H1": "Character-based truncation at a fixed ceiling",
    "H2": "Token-based truncation",
    "H3": "Structure-aware truncation",
    "H4": "Surface context changes retrieval ceiling",
    "H5": "Agent auto-chunks above the truncation ceiling",
}


def format_markdown_entry(
    values: dict, test_id: str, track: str, model_reasoning: str, timestamp: str
) -> str:
    """Return a single assessment entry suitable for appending to a test file."""
    lines = []
    lines.append(f"## Assessment — {timestamp}")
    lines.append("")
    lines.append(f"Test: {test_id}")
    lines.append(f"Track: {track}")
    lines.append(f"LLM/reasoning: {model_reasoning}")
    lines.append(f"Generated: {timestamp}")
    lines.append("")
    lines.append("### Result")
    lines.append("")
    lines.append("| Hypothesis | Value | Rationale |")
    lines.append("|------------|-------|-----------|")
    for i in range(1, 6):
        key = f"H{i}"
        label = f"{key}: {HYPOTHESIS_LABELS[key]}"
        val = values[key]["value"]
        rationale = values[key]["rationale"].replace("|", "\\|")
        lines.append(f"| {label} | {val} | {rationale} |")
    lines.append("")
    lines.append("### Copy-paste")
    lines.append("")
    hypothesis_string = build_string(values)
    lines.append("**framework.py --log**")
    lines.append("")
    lines.append("```bash")
    lines.append(f"--hypothesis \"{hypothesis_string}\"")
    lines.append("```")
    lines.append("")
    lines.append("**log.py**")
    lines.append("")
    lines.append("```text")
    lines.append(hypothesis_string)
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def print_results(values: dict, test_id: str, track: str, model_reasoning: str):
    section("Generated hypothesis assessment")

    hypothesis_string = build_string(values)
    print(f"\n  Test: {test_id}")
    print(f"  Track: {track}")
    print(f"  LLM/reasoning: {model_reasoning}\n")
    print(f"  hypothesis_match:\n    {hypothesis_string}\n")

    print("  | Hypothesis | Value |")
    print("  |------------|-------|")
    for i in range(1, 6):
        key = f"H{i}"
        print(f"  | {key} — {HYPOTHESIS_LABELS[key]} | {values[key]['value']} |")

    print("\n  Rationale:")
    for i in range(1, 6):
        key = f"H{i}"
        print(f"    {key}: {values[key]['value']}")
        print(f"       {values[key]['rationale']}")

    section("Copy-paste commands")
    print("  For framework.py --log, add:")
    print(f"    --hypothesis \"{hypothesis_string}\"")
    print("\n  For log.py, paste this when prompted:")
    print(f"    {hypothesis_string}")

    print("\n  Suggested notes snippet:")
    print("    | Hyp | Value | Notes |")
    print("    |-----|-------|-------|")
    for i in range(1, 6):
        key = f"H{i}"
        print(f"    | {key} | {values[key]['value']:<11} | {values[key]['rationale']} |")


def save_assessment(
    values: dict, test_id: str, track: str, model_reasoning: str
) -> Path:
    """Append the assessment to results/{track}/hypotheses/{test_id}.md.

    The first assessment for a given test and track creates the file; later
    assessments are appended as new sections.
    """
    timestamp = datetime.now().isoformat()
    out_dir = Path("results") / track / "hypotheses"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_test_id = test_id.replace("/", "_").replace("\\", "_")
    out_path = out_dir / f"{safe_test_id}.md"
    entry = format_markdown_entry(values, test_id, track, model_reasoning, timestamp)
    if out_path.exists():
        existing = out_path.read_text(encoding="utf-8").rstrip()
        content = f"{existing}\n\n{entry}"
    else:
        header = f"# Hypothesis Assessment\n\nTrack: {track}\n\n"
        content = header + entry
    out_path.write_text(content + "\n", encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║   Codex Testing Framework — Interactive Hypotheses Assessor      ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("\nAnswer the questions based on the agent chat output you just reviewed.")
    print("Press Enter to skip optional fields.\n")

    try:
        section("Run context (for copy/paste convenience)")
        test_id = prompt("Test ID (e.g. BL-1)", required=False, default="unknown")
        model_reasoning = prompt(
            "LLM/reasoning (e.g. GPT-5.4-Mini Low)",
            required=False,
            default="unknown",
        )
        track = prompt("Track", choices=[
            "codex-interpreted",
            "vscode-codex-interpreted",
            "codex-raw",
            "vscode-codex-raw",
        ], default="codex-interpreted")

        h1_obs = collect_h1_observations(test_id)
        observations = {
            "H1": h1_obs,
            "H2": collect_h2_observations(output_chars=h1_obs.get("reported_chars")),
            "H3": collect_h3_observations(),
            "H4": collect_h4_observations(),
            "H5": collect_h5_observations(),
        }

        values = {}
        values["H1"] = {"value": assess_h1(observations["H1"])[0], "rationale": assess_h1(observations["H1"])[1]}
        values["H2"] = {"value": assess_h2(observations["H2"])[0], "rationale": assess_h2(observations["H2"])[1]}
        values["H3"] = {"value": assess_h3(observations["H3"])[0], "rationale": assess_h3(observations["H3"])[1]}
        values["H4"] = {"value": assess_h4(observations["H4"])[0], "rationale": assess_h4(observations["H4"])[1]}
        values["H5"] = {"value": assess_h5(observations["H5"])[0], "rationale": assess_h5(observations["H5"])[1]}

        print_results(values, test_id, track, model_reasoning)

        if confirm(f"Save this assessment to results/{track}/hypotheses/{test_id}.md?"):
            out_path = save_assessment(values, test_id, track, model_reasoning)
            print(f"\n  ✓ Saved: {out_path}")

    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
