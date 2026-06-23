#!/usr/bin/env python3
"""Audit Codex rollout .jsonl session logs for duplicate emissions and timing drift.

Usage:
    python3 rollout_audit.py session1.jsonl session2.jsonl ...
    python3 rollout_audit.py ~/.codex/sessions/rollout-*.jsonl
    python3 rollout_audit.py --csv audit.csv /rollout-*.jsonl

For each session file this reports:
  1. Identity: session id, model, reasoning effort, CLI version, test prompt ID if present
  2. Emission counts: user messages, commentary updates, final answers, reasoning blocks
  3. API call counts: web search calls, function/tool calls, by tool name
  4. Duplicate detection: any assistant final answer generated more than once,
     and verification that event_msg, response_item, and task_complete.last_agent_message
     are three copies of ONE generation rather than separate generations
  5. Post-completion records: anything appended after the last task_complete
  6. Timing: duration_ms, time_to_first_token_ms, wall clock between first and last record
  7. Token usage from the final token_count event

Exit code is nonzero if any anomaly flag fires, so it can run in CI.
"""

import argparse
import csv
import glob
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def audit_file(path: Path) -> dict:
    records = []
    with open(path) as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
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
        "turns": 0,
        "user_messages": 0,
        "commentary_msgs": 0,
        "final_answers_event": 0,
        "final_answers_item": 0,
        "reasoning_blocks": 0,
        "web_search_calls": 0,
        "function_calls": 0,
        "tools": Counter(),
        "task_completes": 0,
        "records_after_complete": 0,
        "after_complete_types": [],
        "duration_s": None,
        "ttft_s": None,
        "wallclock_s": None,
        "tokens_total": None,
        "context_window": None,
        "flags": [],
    }

    final_event_texts = []          # final answers as emitted in the live event stream
    final_item_texts = []           # final answers as stored in the durable transcript
    last_agent_message = None
    last_complete_idx = None
    first_ts = last_ts = None
    last_tokens = None

    for i, rec in enumerate(records):
        ts = rec.get("timestamp")
        if ts:
            t = parse_ts(ts)
            first_ts = first_ts or t
            last_ts = t

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
            if pt == "task_started":
                r["turns"] += 1
            elif pt == "user_message":
                r["user_messages"] += 1
                msg = p.get("message") or ""
                for line in msg.splitlines():
                    if line.strip().lower().startswith("test id:"):
                        r["test_id"] = line.split(":", 1)[1].strip()
            elif pt == "agent_message":
                if p.get("phase") == "commentary":
                    r["commentary_msgs"] += 1
                elif p.get("phase") == "final_answer":
                    r["final_answers_event"] += 1
                    final_event_texts.append(p.get("message") or "")
            elif pt == "task_complete":
                r["task_completes"] += 1
                last_complete_idx = i
                last_agent_message = p.get("last_agent_message")
                if p.get("duration_ms") is not None:
                    r["duration_s"] = round(p["duration_ms"] / 1000, 1)
                if p.get("time_to_first_token_ms") is not None:
                    r["ttft_s"] = round(p["time_to_first_token_ms"] / 1000, 1)
            elif pt == "token_count":
                info = p.get("info") or {}
                total = (info.get("total_token_usage") or {}).get("total_tokens")
                if total is not None:
                    last_tokens = total
                r["context_window"] = info.get("model_context_window") or r["context_window"]

        elif rtype == "response_item":
            it = p.get("type")
            if it == "message" and p.get("role") == "assistant" and p.get("phase") == "final_answer":
                r["final_answers_item"] += 1
                texts = [c.get("text", "") for c in p.get("content", []) if c.get("type") == "output_text"]
                final_item_texts.append("".join(texts))
            elif it == "reasoning":
                r["reasoning_blocks"] += 1
            elif it == "web_search_call":
                r["web_search_calls"] += 1
            elif it == "function_call":
                r["function_calls"] += 1
                name = p.get("name", "?")
                ns = p.get("namespace")
                r["tools"][f"{ns}.{name}" if ns else name] += 1

    r["tokens_total"] = last_tokens
    if first_ts and last_ts:
        r["wallclock_s"] = round((last_ts - first_ts).total_seconds(), 1)

    # Records appended after the last task_complete: the post-hoc alteration check
    if last_complete_idx is not None:
        tail = records[last_complete_idx + 1:]
        r["records_after_complete"] = len(tail)
        r["after_complete_types"] = [
            f"{x.get('type')}/{(x.get('payload') or {}).get('type', '')}" for x in tail
        ]

    # ---- Anomaly flags ----------------------------------------------------
    # A. More final answers than turns means a genuine double generation
    if r["final_answers_event"] > r["turns"]:
        r["flags"].append(
            f"DOUBLE_GENERATION: {r['final_answers_event']} final answers across {r['turns']} turn(s)"
        )

    # B. Identical text generated twice as separate emissions
    dupes = [t for t, c in Counter(sha(t) for t in final_event_texts).items() if c > 1]
    if dupes:
        r["flags"].append(f"DUPLICATE_EMISSION: identical final answer emitted more than once")

    # C. Event stream and durable transcript should be copies of one generation
    if final_event_texts and final_item_texts:
        if [sha(t) for t in final_event_texts] != [sha(t) for t in final_item_texts]:
            r["flags"].append("STREAM_TRANSCRIPT_MISMATCH: event_msg and response_item final answers differ")

    # D. task_complete should carry the same single message
    if last_agent_message is not None and final_event_texts:
        if last_agent_message != final_event_texts[-1]:
            r["flags"].append("LAST_MESSAGE_MISMATCH: task_complete.last_agent_message differs from emitted final answer")

    # E. Anything written after completion is post-hoc activity
    if r["records_after_complete"]:
        r["flags"].append(
            f"POST_COMPLETION_RECORDS: {r['records_after_complete']} record(s) after task_complete: "
            + ", ".join(r["after_complete_types"][:5])
        )

    # F. Multiple completion events in a single-turn session
    if r["task_completes"] > r["turns"]:
        r["flags"].append(f"EXTRA_TASK_COMPLETE: {r['task_completes']} completes for {r['turns']} turn(s)")

    # G. Structural sanity: a final answer should exist at all
    if r["turns"] and not r["final_answers_event"]:
        r["flags"].append("NO_FINAL_ANSWER: turn completed without a final answer emission")

    return r


def main():
    ap = argparse.ArgumentParser(description="Audit Codex rollout .jsonl logs for duplicate emissions and drift")
    ap.add_argument("paths", nargs="+", help="jsonl files or globs")
    ap.add_argument("--csv", help="also write results to this CSV path")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        expanded = glob.glob(p)
        files.extend(expanded if expanded else [p])
    files = [Path(f) for f in sorted(set(files))]

    results = []
    any_flags = False
    for f in files:
        if not f.exists():
            print(f"SKIP missing file: {f}", file=sys.stderr)
            continue
        r = audit_file(f)
        results.append(r)

        print("=" * 78)
        print(f"{r['file']}")
        print(f"  session {r['session_id']} | {r['model']} {r['effort']} | cli {r['cli_version']} | test {r['test_id']}")
        print(f"  turns {r['turns']} | user msgs {r['user_messages']} | commentary {r['commentary_msgs']} | "
              f"final answers: event {r['final_answers_event']}, transcript {r['final_answers_item']}")
        print(f"  api calls: web_search {r['web_search_calls']} | function {r['function_calls']} "
              f"{dict(r['tools']) if r['tools'] else ''}")
        print(f"  timing: duration {r['duration_s']}s | ttft {r['ttft_s']}s | file wallclock {r['wallclock_s']}s")
        print(f"  tokens {r['tokens_total']} / {r['context_window']}")
        if r["flags"]:
            any_flags = True
            for fl in r["flags"]:
                print(f"  !! {fl}")
        else:
            print("  OK: single emission, no post-completion records, all three copies match")

    if args.csv and results:
        cols = ["file", "session_id", "model", "effort", "test_id", "turns", "user_messages",
                "commentary_msgs", "final_answers_event", "final_answers_item", "web_search_calls",
                "function_calls", "task_completes", "records_after_complete", "duration_s",
                "ttft_s", "wallclock_s", "tokens_total", "flags"]
        with open(args.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in results:
                row = {k: r[k] for k in cols if k != "flags"}
                row["flags"] = "; ".join(r["flags"])
                w.writerow(row)
        print(f"\nCSV written to {args.csv}")

    sys.exit(1 if any_flags else 0)


if __name__ == "__main__":
    main()