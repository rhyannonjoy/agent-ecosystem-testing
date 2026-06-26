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

Run it before logging the result with ``log.py``::

    python scripts/assess_hypotheses.py

The script is intentionally small and focused: it does not log results,
does not modify CSVs, and does not automate data collection.  It only
produces the hypothesis string for the analyst to paste into ``log.py``.

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
import re
import sys


# Markdown sanitiser: the assessment file must not contain parentheses or any
# kind of dash (hyphen, en dash, em dash).
_DASH_RE = re.compile(r"[-–—]")


def md_safe(text, dash_replacement: str = "_") -> str:
    """Return text stripped of parentheses and dash-like characters."""
    text = str(text).replace("(", "").replace(")", "")
    text = _DASH_RE.sub(dash_replacement, text)
    return text


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
    """H2: Token-based truncation.

    A token ceiling can only be supported when a truncation event was actually
    observed, the token count describes the returned excerpt or a stated tool
    limit, and that count sits near a recognized ceiling tier with a plausible
    chars/token ratio. Full-page size estimates (e.g., "the curl response is
    ~200K tokens") do not support the hypothesis because they describe the raw
    source, not a truncation point.
    """
    token_count = obs.get("token_count") or 0
    output_chars = obs.get("output_chars") or 0
    truncated = obs.get("truncated", "unknown")
    token_scope = obs.get("token_scope", "unknown")

    if not token_count:
        return "indeterminate", "No token count available; token-based ceiling cannot be evaluated."

    if truncated == "no":
        return "indeterminate", "No truncation event observed; token-based ceiling cannot be inferred from token count alone."

    # Known approximate retrieval/token ceiling tiers.
    near_threshold = (
        1_800 <= token_count <= 2_200
        or 7_200 <= token_count <= 8_800
        or 28_800 <= token_count <= 35_200
        or 115_200 <= token_count <= 140_800
        or token_count >= 180_000
    )

    # A reported token count for the full fetched page is evidence about the
    # source size, not about where the retrieved excerpt was cut.
    if token_scope == "full_raw_page":
        return (
            "no",
            f"Token count ({token_count:,}) describes the full fetched page, not the returned excerpt or a truncation ceiling.",
        )

    # If we cannot tell what the count measures, we cannot treat it as a ceiling.
    if token_scope == "unknown":
        return (
            "indeterminate",
            f"Token count ({token_count:,}) reported, but its scope is unclear (returned excerpt vs. source page); token-based ceiling cannot be evaluated.",
        )

    # A stated tool/agent limit is evaluated against known tiers without assuming
    # it matches the returned output size.
    if token_scope == "tool_limit_cutoff":
        if truncated == "yes" and near_threshold:
            return (
                "yes",
                f"Agent/tool reported a token limit ({token_count:,}) near a recognized ceiling and truncation was observed.",
            )
        if near_threshold:
            return (
                "partially",
                f"Agent/tool reported a token limit ({token_count:,}) near a recognized ceiling, but truncation was not confirmed.",
            )
        return (
            "no",
            f"Agent/tool reported token limit ({token_count:,}) is not near a recognized ceiling tier.",
        )

    # token_scope == "returned_excerpt" — apply chars/token ratio consistency.
    ratio = output_chars / token_count if token_count else 0

    if truncated == "yes" and near_threshold and 3.0 <= ratio <= 5.0:
        return (
            "yes",
            f"Truncation observed; token count ({token_count:,}) is near a known ceiling and chars/token ratio ({ratio:.2f}) is consistent with token-based truncation.",
        )

    if near_threshold and 2.0 <= ratio <= 6.0:
        return (
            "partially",
            f"Token count ({token_count:,}) is near a known ceiling and ratio ({ratio:.2f}) is plausible, but truncation evidence is not definitive.",
        )

    if not near_threshold:
        return (
            "no",
            f"Token count ({token_count:,}) is not near a recognized token ceiling tier.",
        )

    return (
        "no",
        f"Chars/token ratio ({ratio:.2f}) is not consistent with token-based truncation.",
    )


def assess_h3(obs: dict) -> tuple[str, str]:
    """H3: Structure-aware truncation.

    H3 asks whether any truncation that occurred respected structural
    boundaries. If no truncation event was observed, the hypothesis cannot
    be tested: it is ``indeterminate``, not a positive claim that structure
    was preserved.
    """
    truncated = obs.get("truncated", "no")

    # No truncation event — the mechanism was never observable.
    if truncated == "no":
        return (
            "indeterminate",
            "No truncation event observed; structure-aware boundary behavior could not be evaluated.",
        )

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

    # A truncation event was reported, but we cannot confidently label the
    # boundary as clearly clean or clearly mid-structure.
    return (
        "partially",
        "Truncation event observed, but the exact boundary is unclear or mixed.",
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
    attempts = obs.get("execution_attempts") or 0
    chunking = obs.get("chunking", False)
    many_attempts = bool(attempts) and attempts >= 3

    if chunking:
        return (
            "yes",
            "Agent visibly paginated, fetched tail/offset sections, filled gaps, or reasoned about chunking.",
        )

    if many_attempts:
        return (
            "partially",
            f"{attempts} execution attempts/tool calls observed, but no explicit chunking/pagination signal.",
        )

    return "no", "No visible pagination or multi-step chunking signal."


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

    truncated = prompt(
        "Was the output truncated (stopped before the full page)?",
        choices=["yes", "no", "unknown"],
        default="unknown",
    )

    token_count = to_int(prompt("Token count", required=False))

    token_scope = prompt(
        "What does that token count describe?",
        choices=[
            "returned_excerpt",
            "tool_limit_cutoff",
            "full_raw_page",
            "unknown",
        ],
        default="unknown",
    )

    return {
        "token_count": token_count,
        "output_chars": output_chars,
        "truncated": truncated,
        "token_scope": token_scope,
    }


def collect_h3_observations() -> dict:
    section("H3 — Structure-aware truncation")
    print("  H3 asks whether truncation, when it occurs, lands on structural")
    print("  boundaries (headings, paragraphs, code fences, tables) rather")
    print("  than arbitrary byte positions. If no truncation event happened,")
    print("  the outcome is *indeterminate* — not a claim that structure")
    print("  was preserved.")

    truncated = prompt(
        "Was a truncation event observed?",
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
    """Return a single assessment entry suitable for appending to a test file.

    Written Markdown is sanitized: no parentheses and no dashes (hyphen,
    en dash, em dash). Tables are avoided because their header separator
    requires dashes.
    """
    safe_test_id = md_safe(test_id)
    safe_track = md_safe(track)
    safe_model = md_safe(model_reasoning)
    safe_time = md_safe(timestamp)

    lines = []
    lines.append(f"## Assessment {safe_time}")
    lines.append("")
    lines.append(f"Test: {safe_test_id}")
    lines.append(f"Track: {safe_track}")
    lines.append(f"LLM/reasoning: {safe_model}")
    lines.append(f"Generated: {safe_time}")
    lines.append("")
    lines.append("### Result")
    lines.append("")
    for i in range(1, 6):
        key = f"H{i}"
        label = md_safe(HYPOTHESIS_LABELS[key])
        val = md_safe(values[key]["value"])
        rationale = md_safe(values[key]["rationale"])
        lines.append(f"**{key} {label}**")
        lines.append(f"Value: {val}")
        lines.append(f"Rationale: {rationale}")
        lines.append("")
    lines.append("### Copy/paste")
    lines.append("")
    hypothesis_string = build_string(values)
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

    section("Copy-paste")
    print("  For log.py, paste this when prompted:")
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
    """Append the assessment to results/{track}/artifacts/hypotheses-assessment/{test_id}.md.

    The first assessment for a given test and track creates the file; later
    assessments are appended as new sections.
    """
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    # Anchor to the project root so the file is written to the same place
    # regardless of where the script is launched from.
    _root = Path(__file__).resolve().parent.parent
    out_dir = _root / "results" / track / "artifacts" / "hypotheses-assessment"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_test_id = test_id.replace("/", "_").replace("\\", "_")
    out_path = out_dir / f"{safe_test_id}.md"
    entry = format_markdown_entry(values, test_id, track, model_reasoning, timestamp)
    if out_path.exists():
        existing = out_path.read_text(encoding="utf-8").rstrip()
        content = f"{existing}\n\n{entry}"
    else:
        header = f"# Hypothesis Assessment\n\nTrack: {md_safe(track)}\n\n"
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

        if confirm(f"Save this assessment to results/{track}/artifacts/hypotheses-assessment/{test_id}.md?"):
            out_path = save_assessment(values, test_id, track, model_reasoning)
            print(f"\n  ✓ Saved: {out_path}")

    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
