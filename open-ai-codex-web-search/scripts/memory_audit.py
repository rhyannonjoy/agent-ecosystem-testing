#!/usr/bin/env python3
"""Audit Codex rollout .jsonl session logs for memory and skill influence.

Usage:
    python3 scripts/memory_audit.py results/{track}/artifacts/rollouts/{test}/rollout-*.jsonl
    python3 scripts/memory_audit.py results/{track}/artifacts/rollouts/*/*.jsonl --csv memory.csv

For each session file this reports:
  1. Whether .codex/memories content was loaded, read, or reasoned about
  2. Whether the workspace docs-consumption skill was loaded and followed
  3. Which source (system instructions, commentary, reasoning, final answer,
     tool output) contained each signal
"""

import argparse
import csv
import glob
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


# --- Patterns ---------------------------------------------------------------

SKILL_PATH = ".agents/skills/docs-consumption/SKILL.md"

# Memory-related paths, files, and skill names that appear in the rollout logs.
MEMORY_PATTERNS = {
    # Concrete paths and file names the agent can read or cite.
    "memory_dot_codex_path": re.compile(r"\.codex/memories", re.IGNORECASE),
    "memory_md_file": re.compile(r"MEMORY\.md", re.IGNORECASE),
    "raw_memories_file": re.compile(r"raw_memories\.md", re.IGNORECASE),
    "memory_summary_file": re.compile(r"memory_summary\.md", re.IGNORECASE),
    "rollout_summaries_dir": re.compile(r"rollout_summaries", re.IGNORECASE),
    "single_url_retrieval_skill": re.compile(r"single-url-retrieval-measurement", re.IGNORECASE),
    "memory_skills_dir": re.compile(r"\.codex/memories/skills", re.IGNORECASE),
    # Broader agent-generated references to Codex memory (e.g. "check the local
    # memory notes", "memory pattern", "relevant memory"). These show up in the
    # thought panel / commentary and are not tied to a specific file path.
    "memory_mentioned": re.compile(
        r"\b(?:local memory|memory notes?|memory patterns?|relevant memory|codex memory|"
        r"from memory|memory skill)\b",
        re.IGNORECASE,
    ),
}

# The system prompt contains a separate "## Memory" instruction that tells the
# agent it has access to a memory folder and should use it by default. This is
# distinct from the <skills_instructions> block and is the primary mechanism by
# which the memory skill dominates the workspace skill.
SYSTEM_MEMORY_INSTRUCTION_RE = re.compile(
    r"## Memory.*You have access to a memory folder", re.IGNORECASE | re.DOTALL
)

# Skills are announced in a developer <skills_instructions> block. Each skill
# is one Markdown bullet: - name: description (locator: path)
SKILLS_BLOCK_RE = re.compile(r"<skills_instructions>(.*?)</skills_instructions>", re.DOTALL)
SKILL_LINE_RE = re.compile(
    r"^- (?P<name>.+?):\s+(?P<desc>.+?)\s+\((?P<locator>[^:)]+):\s+(?P<path>[^)]+)\)",
    re.MULTILINE,
)

# The workspace docs-consumption skill requires the report to be prefaced with
# COMPLETE, PARTIAL, or UNVERIFIABLE, optionally followed by a colon, dash, or
# newline (some rollouts use an em dash after the prefix).
PROTOCOL_PREFIX_RE = re.compile(
    r"^\s*(?:\*\*|\*|__|_|#+\s*)?(COMPLETE|PARTIAL|UNVERIFIABLE)"
    r"(?:\*\*|\*|__|_)?\s*(?::|—|–|-|\n|$)",
    re.IGNORECASE,
)

# Phrases that indicate the agent reasoned with the docs-consumption protocol.
SKILL_LANGUAGE_PATTERNS = [
    re.compile(r"\bthe tool ran\b", re.IGNORECASE),
    re.compile(r"\bfull content\b", re.IGNORECASE),
    re.compile(r"\bnot verified\b", re.IGNORECASE),
    re.compile(r"\bcannot confirm\b", re.IGNORECASE),
    re.compile(r"\bunverifiable\b", re.IGNORECASE),
    re.compile(r"\btruncation\b", re.IGNORECASE),
    re.compile(r"\blimitation\b", re.IGNORECASE),
    re.compile(r"\bcache miss\b", re.IGNORECASE),
    re.compile(r"\b0 bytes\b", re.IGNORECASE),
    re.compile(r"\bdns resolution failed\b", re.IGNORECASE),
    re.compile(r"\buse curl\b", re.IGNORECASE),
]


# --- Helpers ----------------------------------------------------------------

def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def parse_skills(records: list[dict]) -> list[dict]:
    """Return skill entries observed in developer <skills_instructions> blocks."""
    skills = []
    for rec in records:
        if rec.get("type") != "response_item":
            continue
        payload = rec.get("payload", {}) or {}
        if payload.get("type") != "message" or payload.get("role") != "developer":
            continue
        for block in payload.get("content", []) or []:
            text = block.get("text", "")
            for block_match in SKILLS_BLOCK_RE.finditer(text):
                for line_match in SKILL_LINE_RE.finditer(block_match.group(1)):
                    skills.append(
                        {
                            "name": line_match.group("name").strip(),
                            "description": line_match.group("desc").strip(),
                            "locator": line_match.group("locator").strip(),
                            "path": line_match.group("path").strip(),
                        }
                    )
    return skills


def _extract_text_from_content(content) -> list[str]:
    """Extract text fragments from a message content field."""
    texts = []
    if isinstance(content, str):
        if content:
            texts.append(content)
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                text = block.get("text", "")
                if text:
                    texts.append(text)
    return texts


def extract_texts(record: dict) -> list[str]:
    """Extract all human-readable text fragments from a record."""
    texts = []
    payload = record.get("payload", {}) or {}
    it = payload.get("type")

    # Message content
    if it == "message":
        texts.extend(_extract_text_from_content(payload.get("content", [])))

    # Reasoning content (may be a string or a content list)
    if it == "reasoning":
        reasoning = payload.get("reasoning") or payload.get("content") or payload.get("summary") or ""
        if isinstance(reasoning, str) and reasoning:
            texts.append(reasoning)
        elif isinstance(reasoning, list):
            texts.extend(_extract_text_from_content(reasoning))

    # Tool outputs
    if it == "function_call_output":
        out = payload.get("output") or ""
        if out:
            texts.append(str(out))
    elif it == "custom_tool_call_output":
        out_blocks = payload.get("output") or []
        if isinstance(out_blocks, str):
            if out_blocks:
                texts.append(out_blocks)
        else:
            texts.extend(_extract_text_from_content(out_blocks))

    return texts


def audit_file(path: Path) -> dict:
    records = []
    line_no_by_index: dict[int, int] = {}
    with open(path) as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                line_no_by_index[len(records)] = n
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  WARNING {path.name}:{n} unparseable line: {e}", file=sys.stderr)

    r = {
        "file": path.name,
        "session_id": None,
        "model": None,
        "effort": None,
        "cli_version": None,
        "test_id": None,

        # Text sources
        "system_texts": [],
        "commentary_texts": [],
        "reasoning_texts": [],
        "final_answer_texts": [],
        "tool_output_texts": [],

        # Memory signals (true/false)
        "system_memory_instruction": "false",
        "memory_dot_codex_path": "false",
        "memory_md_file": "false",
        "raw_memories_file": "false",
        "memory_summary_file": "false",
        "rollout_summaries_dir": "false",
        "single_url_retrieval_skill": "false",
        "memory_skills_dir": "false",

        # Memory citation field (schema-level signal; present even when memory
        # content is not injected)
        "memory_citation_field_present": "false",
        "memory_citation_used": "false",

        # Memory sources
        "memory_sources": [],

        # Docs-consumption signals
        "docs_consumption_loaded": "false",
        "docs_consumption_path": "",
        "docs_consumption_desc": "",
        "docs_consumption_name_mentioned": "false",
        "docs_consumption_path_mentioned": "false",
        "protocol_prefix": "",
        "protocol_prefix_source": "none",
        "skill_language": "false",
        "skill_language_source": "none",
        "skill_sources": [],
    }

    for i, rec in enumerate(records):
        rtype = rec.get("type")
        p = rec.get("payload", {}) or {}

        if rtype == "session_meta":
            r["session_id"] = p.get("id")
            r["cli_version"] = p.get("cli_version")

        elif rtype == "turn_context":
            r["model"] = p.get("model")
            r["effort"] = p.get("effort")

        elif rtype == "event_msg":
            pt = p.get("type")
            if pt == "user_message":
                msg = p.get("message") or ""
                for line in msg.splitlines():
                    if line.strip().lower().startswith("test id:"):
                        r["test_id"] = line.split(":", 1)[1].strip()

            elif pt == "agent_message":
                phase = p.get("phase")
                msg = p.get("message") or ""
                if phase == "commentary":
                    r["commentary_texts"].append(msg)
                elif phase == "final_answer":
                    r["final_answer_texts"].append(msg)
                # memory_citation is a schema field that appears whenever Codex
                # is memory-aware, even if no memory was actually cited.
                if "memory_citation" in p:
                    r["memory_citation_field_present"] = "true"
                    if p.get("memory_citation") is not None:
                        r["memory_citation_used"] = "true"

        elif rtype == "response_item":
            it = p.get("type")
            if it == "message":
                role = p.get("role")
                if role == "developer":
                    r["system_texts"].extend(extract_texts(rec))
                elif role == "assistant":
                    phase = p.get("phase")
                    texts = extract_texts(rec)
                    if phase == "final_answer":
                        r["final_answer_texts"].extend(texts)
                    elif phase == "commentary":
                        r["commentary_texts"].extend(texts)
            elif it == "reasoning":
                r["reasoning_texts"].extend(extract_texts(rec))
            elif it in ("function_call_output", "custom_tool_call_output"):
                r["tool_output_texts"].extend(extract_texts(rec))

    # ---- Detect memory signals by source ------------------------------------
    source_names = {
        "system": r["system_texts"],
        "commentary": r["commentary_texts"],
        "reasoning": r["reasoning_texts"],
        "final_answer": r["final_answer_texts"],
        "tool_output": r["tool_output_texts"],
    }

    # Agent-generated sources are what we care about for skill compliance;
    # system/developer instructions naturally contain the skill text itself,
    # so matching them would be a false positive.
    agent_sources = {
        "commentary": r["commentary_texts"],
        "reasoning": r["reasoning_texts"],
        "final_answer": r["final_answer_texts"],
        "tool_output": r["tool_output_texts"],
    }

    memory_detected = {name: False for name in MEMORY_PATTERNS}
    memory_sources: set[str] = set()
    skill_sources: set[str] = set()

    # The system "## Memory" instruction is distinct from the loaded skills.
    if any(SYSTEM_MEMORY_INSTRUCTION_RE.search(text) for text in r["system_texts"]):
        r["system_memory_instruction"] = "true"
        memory_sources.add("system_instruction")

    for source_name, texts in source_names.items():
        if not texts:
            continue

        # Memory patterns (system block is relevant because it lists loaded skills)
        for pattern_name, pattern in MEMORY_PATTERNS.items():
            for text in texts:
                if pattern.search(text):
                    memory_detected[pattern_name] = True
                    memory_sources.add(source_name)
                    break

    for source_name, texts in agent_sources.items():
        if not texts:
            continue
        lowered = [text.lower() for text in texts]

        # Docs-consumption skill name or path mention
        if any("docs-consumption" in text for text in lowered):
            r["docs_consumption_name_mentioned"] = "true"
            skill_sources.add(source_name)
        if any(SKILL_PATH.lower() in text for text in lowered):
            r["docs_consumption_path_mentioned"] = "true"
            skill_sources.add(source_name)

        # Protocol prefix
        for text in lowered:
            match = PROTOCOL_PREFIX_RE.search(text)
            if match:
                r["protocol_prefix"] = match.group(1).upper()
                r["protocol_prefix_source"] = source_name
                skill_sources.add(source_name)
                break

        # Skill language
        if r["skill_language"] == "false":
            for pattern in SKILL_LANGUAGE_PATTERNS:
                for text in lowered:
                    if pattern.search(text):
                        r["skill_language"] = "true"
                        r["skill_language_source"] = source_name
                        skill_sources.add(source_name)
                        break
                if r["skill_language"] == "true":
                    break

    for pattern_name in MEMORY_PATTERNS:
        r[pattern_name] = "true" if memory_detected[pattern_name] else "false"

    r["memory_sources"] = sorted(memory_sources)
    r["skill_sources"] = sorted(skill_sources)

    # ---- Parse loaded skills ------------------------------------------------
    skills = parse_skills(records)
    docs_consumption = next(
        (s for s in skills if "docs-consumption" in s["name"]), None
    )
    if docs_consumption:
        r["docs_consumption_loaded"] = "true"
        r["docs_consumption_path"] = docs_consumption["path"]
        r["docs_consumption_desc"] = docs_consumption["description"][:120]
        skill_sources.add("system_loaded")

    memory_skill = next(
        (s for s in skills if "single-url-retrieval-measurement" in s["name"]), None
    )
    if memory_skill:
        memory_detected["single_url_retrieval_skill"] = True
        r["single_url_retrieval_skill"] = "true"
        memory_sources.add("system_loaded")

    r["memory_sources"] = sorted(set(memory_sources))
    r["skill_sources"] = sorted(set(skill_sources))

    # Collapse the two boolean citation flags into a single, audit-friendly
    # status so the terminal output can immediately be compared with the
    # self-reported memory sources.
    if r["memory_citation_used"] == "true":
        r["memory_citation_status"] = "used"
    elif r["memory_citation_field_present"] == "true":
        r["memory_citation_status"] = "null"
    else:
        r["memory_citation_status"] = "absent"

    # Flag when the rollout's memory_citation field disagrees with the sources
    # the agent actually produced in its own text.
    has_sources = bool(r["memory_sources"])
    citation_used = r["memory_citation_status"] == "used"
    if citation_used and not has_sources:
        r["memory_citation_source_discrepancy"] = (
            "memory_citation used but no memory sources detected"
        )
    elif has_sources and not citation_used:
        r["memory_citation_source_discrepancy"] = (
            f"memory sources detected but memory_citation is {r['memory_citation_status']}"
        )
    else:
        r["memory_citation_source_discrepancy"] = ""

    return r


def main():
    ap = argparse.ArgumentParser(
        description="Audit Codex rollout logs for memory and skill influence"
    )
    ap.add_argument("paths", nargs="+", help="jsonl files or globs")
    ap.add_argument("--csv", help="write results to this CSV path")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        expanded = glob.glob(p)
        files.extend(expanded if expanded else [p])
    files = [Path(f) for f in sorted(set(files))]

    results = []
    for f in files:
        if not f.exists():
            print(f"SKIP missing file: {f}", file=sys.stderr)
            continue
        r = audit_file(f)
        results.append(r)

        print("=" * 78)
        print(f"{r['file']}")
        print(
            f"  session {r['session_id']} | {r['model']} {r['effort']} | "
            f"cli {r['cli_version']} | test {r['test_id']}"
        )

        memory_bits = [k for k in MEMORY_PATTERNS if r[k] == "true"]
        if r["system_memory_instruction"] == "true":
            memory_bits.insert(0, "system_memory_instruction")
        if r["memory_citation_field_present"] == "true" or r["memory_citation_used"] == "true":
            memory_bits.append(f"memory_citation: {r['memory_citation_status']}")

        if memory_bits or r["memory_sources"] or r["memory_citation_source_discrepancy"]:
            print(f"  memory signals: {', '.join(memory_bits) if memory_bits else 'none'}")
            print(f"  memory sources: {', '.join(r['memory_sources']) if r['memory_sources'] else 'none'}")
            if r["memory_citation_source_discrepancy"]:
                print(f"  discrepancy: {r['memory_citation_source_discrepancy']}")
        else:
            print("  memory signals: none")

        skill_bits = []
        if r["docs_consumption_loaded"] == "true":
            skill_bits.append("docs-consumption loaded")
        if r["docs_consumption_name_mentioned"] == "true":
            skill_bits.append("name mentioned")
        if r["docs_consumption_path_mentioned"] == "true":
            skill_bits.append("path mentioned")
        if r["protocol_prefix"]:
            skill_bits.append(f"prefix={r['protocol_prefix']} ({r['protocol_prefix_source']})")
        if r["skill_language"] == "true":
            skill_bits.append(f"skill-language ({r['skill_language_source']})")
        if skill_bits:
            print(f"  skill signals: {' | '.join(skill_bits)}")
            print(f"  skill sources: {', '.join(r['skill_sources']) if r['skill_sources'] else 'none'}")
        else:
            print("  skill signals: none")

    if args.csv and results:
        cols = [
            "file",
            "session_id",
            "model",
            "effort",
            "cli_version",
            "test_id",
            "system_memory_instruction",
            "memory_dot_codex_path",
            "memory_md_file",
            "raw_memories_file",
            "memory_summary_file",
            "rollout_summaries_dir",
            "single_url_retrieval_skill",
            "memory_skills_dir",
            "memory_mentioned",
            "memory_citation_status",
            "memory_citation_source_discrepancy",
            "memory_sources",
            "docs_consumption_loaded",
            "docs_consumption_path",
            "docs_consumption_desc",
            "docs_consumption_name_mentioned",
            "docs_consumption_path_mentioned",
            "protocol_prefix",
            "protocol_prefix_source",
            "skill_language",
            "skill_language_source",
            "skill_sources",
        ]
        with open(args.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in results:
                row = {k: r[k] for k in cols}
                row["memory_sources"] = ", ".join(r["memory_sources"])
                row["skill_sources"] = ", ".join(r["skill_sources"])
                w.writerow(row)
        print(f"\nCSV written to {args.csv}")

    sys.exit(0)


if __name__ == "__main__":
    main()
