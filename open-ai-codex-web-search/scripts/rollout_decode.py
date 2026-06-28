#!/usr/bin/env python3
"""Decode Codex rollout .jsonl session logs into readable form.

Three views, combinable:

  --census     What is this file made of? Counts every record type and payload
               type, and inventories which fields each carries. Answers "what
               are these logs actually logging" structurally.

  --timeline   The default. One line per record: elapsed time, who/what, and a
               readable summary. Shell commands, tool calls, searches, agent
               messages, and token checkpoints all appear in order.

  --pretty     Full indented JSON of every record, with encrypted reasoning
               blobs and other noise elided. Use --grep TYPE to limit it to
               one record or payload type, e.g. --pretty --grep web_search_call

Examples:
    python3 scripts/rollout_decode.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/rollout-*.jsonl --census
    python3 scripts/rollout_decode.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/{session}.jsonl --timeline
    python3 scripts/rollout_decode.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/{session}.jsonl --timeline --md decoded.md
    python3 scripts/rollout_decode.py results/vscode-codex-interpreted/artifacts/rollouts/SC-2/{session}.jsonl --pretty --grep task_complete
"""

import argparse
import glob
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from failure_classifier import FailureClass, classify_output, summarize as fc_summarize

ELIDE_KEYS = {"encrypted_content"}      # opaque blobs worth hiding by default
TRUNC = 160                             # summary truncation width


def parse_ts(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def trunc(s, width=TRUNC):
    s = " ".join(str(s).split())
    return s if len(s) <= width else s[: width - 3] + "..."


def load(path):
    records = []
    with open(path) as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append((n, json.loads(line)))
            except json.JSONDecodeError as e:
                print(f"  WARNING {path.name}:{n} unparseable: {e}", file=sys.stderr)
    return records


def record_kind(rec):
    """Two-level identity: top-level type, payload type if present."""
    t = rec.get("type", "?")
    pt = (rec.get("payload") or {}).get("type")
    return f"{t}/{pt}" if pt else t


# ---------------------------------------------------------------- census ----

def census(path, records):
    kinds = Counter()
    fields = defaultdict(Counter)
    for _, rec in records:
        k = record_kind(rec)
        kinds[k] += 1
        payload = rec.get("payload") or {}
        for key in payload:
            fields[k][key] += 1

    print(f"\n{'=' * 78}\nCENSUS  {path.name}  ({len(records)} records)\n")
    print(f"{'record kind':46s} {'count':>5s}   payload fields")
    print("-" * 78)
    for k, c in kinds.most_common():
        fl = ", ".join(f for f, _ in fields[k].most_common())
        print(f"{k:46s} {c:>5d}   {trunc(fl, 90)}")


# -------------------------------------------------------------- timeline ----

def summarize(rec):
    """One readable line per record. Returns (tag, text, failure_class)."""
    t = rec.get("type")
    p = rec.get("payload") or {}
    pt = p.get("type")
    failure: FailureClass | None = None

    def result(tag, text):
        return tag, text, failure

    if t == "session_meta":
        git = p.get("git") or {}
        return result("META", f"session {p.get('id','?')[-12:]} | cli {p.get('cli_version')} | "
                              f"branch {git.get('branch')} | cwd {p.get('cwd')}")
    if t == "turn_context":
        return result("META", f"model {p.get('model')} | effort {p.get('effort')} | "
                              f"sandbox {(p.get('sandbox_policy') or {}).get('type')} | "
                              f"approval {p.get('approval_policy')}")
    if t == "event_msg":
        if pt == "task_started":
            return result("TURN", f"task started | context window {p.get('model_context_window')}")
        if pt == "user_message":
            return result("USER", trunc(p.get("message", "")))
        if pt == "agent_message":
            phase = p.get("phase", "?")
            tag = "FINAL" if phase == "final_answer" else "AGENT"
            return result(tag, trunc(p.get("message", "")))
        if pt == "web_search_end":
            a = p.get("action") or {}
            return result("WEB", f"{a.get('type')} {a.get('url') or p.get('query') or ''}".strip())
        if pt == "mcp_tool_call_end":
            inv = p.get("invocation") or {}
            dur = p.get("duration") or {}
            secs = dur.get("secs", 0) + dur.get("nanos", 0) / 1e9
            result_block = p.get("result") or {}
            ok = result_block.get("Ok") or {}
            text = ""
            for block in ok.get("content", []) or []:
                if isinstance(block, dict) and block.get("type") == "text":
                    text += block.get("text", "")
            fc = classify_output(text)
            base = f"{inv.get('server')}.{inv.get('tool')} " \
                   f"[{(inv.get('arguments') or {}).get('title','')}] {secs:.2f}s"
            if fc.category != "ok":
                failure = fc
                return result("FAIL", f"[{fc.category}] {base}: {trunc(text)}")
            return result("MCP", base)
        if pt == "exec_command_begin" or pt == "exec_command_end":
            cmd = p.get("command")
            if isinstance(cmd, list):
                cmd = " ".join(cmd)
            out = p.get("output", "")
            fc = classify_output(out)
            text = trunc(out or cmd or pt)
            if fc.category != "ok":
                failure = fc
                return result("FAIL", f"[{fc.category}] {text}")
            return result("SHELL", text)
        if pt == "token_count":
            info = p.get("info") or {}
            tot = (info.get("total_token_usage") or {}).get("total_tokens")
            return result("TOKENS", f"cumulative {tot}")
        if pt == "task_complete":
            return result("TURN", f"task complete | duration {p.get('duration_ms', 0)/1000:.1f}s | "
                                  f"ttft {p.get('time_to_first_token_ms', 0)/1000:.1f}s")
        return result("EVENT", pt or "?")
    if t == "response_item":
        if pt == "message":
            role = p.get("role")
            phase = p.get("phase", "")
            texts = [c.get("text", "") for c in p.get("content", []) if "text" in c]
            label = {"assistant": "AGENT*", "user": "USER*", "developer": "DEV*"}.get(role, role)
            if role == "assistant" and phase == "final_answer":
                label = "FINAL*"
            return result(label, trunc("".join(texts)))
        if pt == "reasoning":
            blob = p.get("encrypted_content") or ""
            return result("THINK", f"encrypted reasoning block, {len(blob)} chars (opaque)")
        if pt == "web_search_call":
            a = p.get("action") or {}
            return result("WEB*", f"{a.get('type')} {a.get('url','')}".strip())
        if pt == "function_call":
            name = p.get("name", "?")
            ns = p.get("namespace")
            args = p.get("arguments", "")
            try:
                ad = json.loads(args)
                args = ad.get("command") or ad.get("title") or args
                if isinstance(args, list):
                    args = " ".join(args)
            except Exception:
                pass
            return result("CALL", f"{(ns + '.') if ns else ''}{name}  {trunc(args, 110)}")
        if pt == "function_call_output":
            out = p.get("output", "")
            fc = classify_output(out)
            if fc.category != "ok":
                failure = fc
                return result("FAIL", f"[{fc.category}] {fc.detail}: {trunc(out)}")
            return result("OUT", trunc(out))
        return result("ITEM", pt or "?")
    return result(t.upper() if t else "?", "")


def timeline(path, records, out=sys.stdout, md=False):
    t0 = None
    failures = []
    hdr = f"TIMELINE  {path.name}  ({len(records)} records)"
    if md:
        out.write(f"## {hdr}\n\n```text\n")
    else:
        out.write(f"\n{'=' * 78}\n{hdr}\n{'-' * 78}\n")
    for _, rec in records:
        ts = rec.get("timestamp")
        elapsed = ""
        if ts:
            t = parse_ts(ts)
            t0 = t0 or t
            elapsed = f"+{(t - t0).total_seconds():7.1f}s"
        tag, text, fc = summarize(rec)
        if fc is not None:
            failures.append(fc)
        out.write(f"{elapsed:>9s}  {tag:7s} {text}\n")
    if md:
        out.write("```\n\n")

    summary = fc_summarize(failures)
    if summary["total"]:
        breakdown = ", ".join(
            f"{cat}={c}" for cat, c in sorted(summary["category_counts"].items()) if cat != "ok"
        )
        summary_line = f"\nFAILURES: {summary['total']} total ({summary['error_count']} error, {summary['warning_count']} warning) | {breakdown}\n"
    else:
        summary_line = "\nFAILURES: none detected\n"
    out.write(summary_line)
    if not md:
        out.write("\nLegend: starred tags (FINAL*, AGENT*, WEB*) are LLM-facing transcript copies of\n"
                  "the corresponding UI event records; THINK blocks are encrypted and\n"
                  "unreadable by design; TOKENS rows are cumulative session usage checkpoints.\n")


# ---------------------------------------------------------------- pretty ----

def clean(obj):
    if isinstance(obj, dict):
        return {k: ("<elided>" if k in ELIDE_KEYS else clean(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean(x) for x in obj]
    return obj


def pretty(path, records, grep=None, out=sys.stdout):
    out.write(f"\n{'=' * 78}\nPRETTY  {path.name}" + (f"  filter: {grep}" if grep else "") + "\n")
    shown = 0
    for n, rec in records:
        kind = record_kind(rec)
        if grep and grep not in kind:
            continue
        shown += 1
        out.write(f"\n--- line {n}  [{kind}] ---\n")
        out.write(json.dumps(clean(rec), indent=2, ensure_ascii=False) + "\n")
    if grep and not shown:
        out.write(f"no records matching '{grep}'\n")


# ------------------------------------------------------------------ main ----

def main():
    ap = argparse.ArgumentParser(description="Decode and prettify Codex rollout .jsonl logs")
    ap.add_argument("paths", nargs="+", help="jsonl files or globs")
    ap.add_argument("--census", action="store_true", help="record and field inventory")
    ap.add_argument("--timeline", action="store_true", help="readable chronological view")
    ap.add_argument("--pretty", action="store_true", help="full indented JSON, noise elided")
    ap.add_argument("--grep", help="with --pretty: only records whose kind contains this string")
    ap.add_argument("--md", help="write timeline output to this markdown file instead of stdout")
    args = ap.parse_args()

    if not (args.census or args.timeline or args.pretty):
        args.timeline = True

    files = []
    for p in args.paths:
        expanded = glob.glob(p)
        files.extend(expanded if expanded else [p])
    files = [Path(f) for f in sorted(set(files))]

    md_out = open(args.md, "w") if args.md else None
    try:
        for f in files:
            if not f.exists():
                print(f"SKIP missing: {f}", file=sys.stderr)
                continue
            records = load(f)
            if args.census:
                census(f, records)
            if args.timeline:
                timeline(f, records, out=md_out or sys.stdout, md=bool(md_out))
            if args.pretty:
                pretty(f, records, grep=args.grep, out=md_out or sys.stdout)
    finally:
        if md_out:
            md_out.close()
            print(f"written to {args.md}")


if __name__ == "__main__":
    main()