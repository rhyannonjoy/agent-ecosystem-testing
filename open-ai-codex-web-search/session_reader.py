#!/usr/bin/env python3
"""
codex_session_reader.py — Codex Session Observability Log
Agent Ecosystem Testing · https://rhyannonjoy.github.io/agent-ecosystem-testing/

Converts a Codex .jsonl session file into a structured observability report.
Surfaces agent configuration, skills, sandbox policy, token usage, tool calls,
reasoning presence, and conversation — everything in the session, not just chat.

Usage:
    python3 codex_session_reader.py ~/Documents/rollout-*.jsonl
    python3 codex_session_reader.py ~/Documents/rollout-*.jsonl -o report.html
    python3 codex_session_reader.py ~/Documents/rollout-*.jsonl --list-sessions
    python3 codex_session_reader.py ~/Documents/rollout-*.jsonl --session-id <id>
"""

import argparse
import html
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# Parse
# ─────────────────────────────────────────────────────────────

def parse_ndjson(path: Path) -> list:
    events = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as ex:
                print(f"  [warn] line {lineno}: {ex}", file=sys.stderr)
    return events


def group_by_session(events: list) -> dict:
    """Bucket events by session id. Each session_meta starts a new bucket."""
    buckets = defaultdict(list)
    order = []
    current = "unknown"
    for ev in events:
        if ev.get("type") == "session_meta":
            sid = ev.get("payload", {}).get("id", "unknown")
            current = sid
            if sid not in order:
                order.append(sid)
        buckets[current].append(ev)
    result = {sid: buckets[sid] for sid in order if sid in buckets}
    if "unknown" in buckets and "unknown" not in result:
        result["unknown"] = buckets["unknown"]
    return result


# ─────────────────────────────────────────────────────────────
# Extract structured data from a session's events
# ─────────────────────────────────────────────────────────────

def extract_session_meta(events: list) -> dict:
    for ev in events:
        if ev.get("type") == "session_meta":
            p = ev.get("payload", {})
            return {
                "id": p.get("id", ""),
                "timestamp": p.get("timestamp", ""),
                "cwd": p.get("cwd", ""),
                "cli_version": p.get("cli_version", ""),
                "source": p.get("source", ""),
                "originator": p.get("originator", ""),
                "model_provider": p.get("model_provider", ""),
                "memory_mode": p.get("memory_mode", ""),
                "git_branch": p.get("git", {}).get("branch", ""),
                "git_commit": p.get("git", {}).get("commit_hash", "")[:12],
                "git_repo": p.get("git", {}).get("repository_url", ""),
                "base_instructions": p.get("base_instructions", {}).get("text", ""),
            }
    return {}


def extract_developer_context(events: list) -> dict:
    """
    Extract skills, plugins, collaboration mode, and permissions from
    developer-role and user-role response_item messages.
    """
    skills = []
    plugins = []
    collab_mode = ""
    permissions_text = ""
    env_context = ""
    seen_skills = False
    seen_plugins = False

    for ev in events:
        if ev.get("type") != "response_item":
            continue
        payload = ev.get("payload", {})
        role = payload.get("role")
        content = payload.get("content") or []

        for block in content:
            if block.get("type") != "input_text":
                continue
            text = block.get("text", "")

            if role == "developer":
                if "<skills_instructions>" in text and not seen_skills:
                    seen_skills = True
                    for line in text.splitlines():
                        line = line.strip()
                        if line.startswith("- ") and ": " in line and "(file:" in line:
                            try:
                                name_part = line[2:line.index(":")]
                                desc_start = line.index(": ") + 2
                                desc_end = line.index(" (file:") if " (file:" in line else len(line)
                                file_start = line.index("(file: ") + 7 if "(file: " in line else -1
                                file_end = line.rindex(")") if ")" in line else len(line)
                                skills.append({
                                    "name": name_part.strip(),
                                    "description": line[desc_start:desc_end].strip(),
                                    "file": line[file_start:file_end].strip() if file_start > 0 else "",
                                })
                            except (ValueError, IndexError):
                                pass

                if "<plugins_instructions>" in text and not seen_plugins:
                    seen_plugins = True
                    for line in text.splitlines():
                        line = line.strip()
                        if line.startswith("- `") and "`:" in line:
                            try:
                                name = line[3:line.index("`:", 3)]
                                desc = line[line.index("`:", 3) + 2:].strip()
                                plugins.append({"name": name, "description": desc})
                            except (ValueError, IndexError):
                                pass

                if "<collaboration_mode>" in text and not collab_mode:
                    collab_mode = text

                if "<permissions instructions>" in text and not permissions_text:
                    permissions_text = text

            elif role == "user":
                if "<environment_context>" in text and not env_context:
                    env_context = text

    return {
        "skills": skills,
        "plugins": plugins,
        "collab_mode_raw": collab_mode,
        "permissions_raw": permissions_text,
        "env_context_raw": env_context,
    }


def extract_turns(events: list) -> list:
    """Extract per-turn observability data."""
    turns = []
    current = None

    for ev in events:
        ev_type = ev.get("type")
        payload = ev.get("payload", {})
        ts = ev.get("timestamp", "")

        if ev_type == "event_msg":
            msg_type = payload.get("type", "")

            if msg_type == "task_started":
                current = {
                    "turn_id": payload.get("turn_id", ""),
                    "timestamp": ts,
                    "context_window": payload.get("model_context_window"),
                    "model": None,
                    "effort": None,
                    "collab_mode": None,
                    "sandbox_policy": None,
                    "approval_policy": None,
                    "truncation_policy": None,
                    "user_message": None,
                    "assistant_messages": [],
                    "tool_calls": [],
                    "reasoning_count": 0,
                    "token_snapshots": [],
                    "duration_ms": None,
                    "ttft_ms": None,
                    "completed": False,
                }
                turns.append(current)

            elif msg_type == "task_complete" and current is not None:
                current["duration_ms"] = payload.get("duration_ms")
                current["ttft_ms"] = payload.get("time_to_first_token_ms")
                current["completed"] = True

            elif msg_type == "user_message" and current is not None:
                current["user_message"] = payload.get("message", "")

            elif msg_type == "token_count" and current is not None:
                info = payload.get("info") or {}
                last = info.get("last_token_usage") or {}
                total = info.get("total_token_usage") or {}
                rate = payload.get("rate_limits") or {}
                primary = rate.get("primary") or {}
                current["token_snapshots"].append({
                    "input": last.get("input_tokens"),
                    "cached_input": last.get("cached_input_tokens"),
                    "output": last.get("output_tokens"),
                    "reasoning_output": last.get("reasoning_output_tokens"),
                    "total_turn": last.get("total_tokens"),
                    "total_session": total.get("total_tokens"),
                    "context_window": info.get("model_context_window"),
                    "rate_used_pct": primary.get("used_percent"),
                    "plan_type": rate.get("plan_type"),
                    "rate_window_min": primary.get("window_minutes"),
                })

        elif ev_type == "turn_context" and current is not None:
            current["model"] = payload.get("model")
            current["effort"] = payload.get("effort")
            current["approval_policy"] = payload.get("approval_policy")
            sp = payload.get("sandbox_policy") or {}
            current["sandbox_policy"] = {
                "type": sp.get("type"),
                "network_access": sp.get("network_access"),
            }
            tp = payload.get("truncation_policy") or {}
            current["truncation_policy"] = {
                "mode": tp.get("mode"),
                "limit": tp.get("limit"),
            }
            cm = payload.get("collaboration_mode") or {}
            current["collab_mode"] = cm.get("mode")

        elif ev_type == "response_item" and current is not None:
            item_type = payload.get("type")
            role = payload.get("role")

            if item_type == "message" and role == "assistant":
                phase = payload.get("phase", "")
                for block in payload.get("content", []):
                    if block.get("type") == "output_text":
                        current["assistant_messages"].append({
                            "phase": phase,
                            "text": block.get("text", ""),
                        })

            elif item_type == "function_call":
                args = payload.get("arguments", "")
                current["tool_calls"].append({
                    "kind": "function_call",
                    "name": payload.get("name", ""),
                    "args": _trunc(args, 400),
                    "call_id": payload.get("call_id", ""),
                    "result": None,
                })

            elif item_type == "function_call_output":
                cid = payload.get("call_id", "")
                out = payload.get("output", "")
                for tc in reversed(current["tool_calls"]):
                    if tc.get("call_id") == cid:
                        tc["result"] = _trunc(out, 400)
                        break

            elif item_type == "custom_tool_call":
                inp = payload.get("input", "")
                if not isinstance(inp, str):
                    inp = json.dumps(inp, indent=2)
                current["tool_calls"].append({
                    "kind": "custom_tool_call",
                    "name": payload.get("name", ""),
                    "args": _trunc(inp, 400),
                    "call_id": payload.get("call_id", ""),
                    "status": payload.get("status", ""),
                    "result": None,
                })

            elif item_type == "custom_tool_call_output":
                cid = payload.get("call_id", "")
                out = payload.get("output", "")
                for tc in reversed(current["tool_calls"]):
                    if tc.get("call_id") == cid:
                        tc["result"] = _trunc(out, 400)
                        break

            elif item_type == "reasoning":
                current["reasoning_count"] += 1

    return turns


def _trunc(s: str, n: int) -> str:
    if len(s) > n:
        return s[:n] + f" … [{len(s) - n} chars truncated]"
    return s


# ─────────────────────────────────────────────────────────────
# HTML rendering
# ─────────────────────────────────────────────────────────────

CSS = """
:root {
    --bg: #0c0c0c;
    --surface: #141414;
    --surface2: #1a1a1a;
    --surface3: #202020;
    --border: #252525;
    --border2: #2e2e2e;
    --text: #c8c8c8;
    --text-dim: #6e6e6e;
    --text-faint: #3a3a3a;
    --accent: #d4a847;
    --accent-blue: #5b8db8;
    --accent-green: #5c9e6e;
    --accent-red: #a05555;
    --accent-purple: #7b6aab;
    --mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Mono', monospace;
    --sans: 'IBM Plex Sans', 'DM Sans', system-ui, sans-serif;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { background: var(--bg); color: var(--text); font-family: var(--sans); font-size: 13px; line-height: 1.6; }
.layout { display: flex; min-height: 100vh; }
.sidebar {
    width: 240px; min-width: 240px; background: var(--surface);
    border-right: 1px solid var(--border); position: sticky; top: 0;
    height: 100vh; overflow-y: auto; padding: 16px 0; flex-shrink: 0;
}
.main { flex: 1; min-width: 0; padding: 32px 36px; }
.sb-logo { padding: 0 14px 14px; border-bottom: 1px solid var(--border); margin-bottom: 10px; }
.sb-logo h1 { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); font-family: var(--mono); }
.sb-logo p { font-size: 10px; color: var(--text-dim); margin-top: 3px; }
.sb-section { padding: 10px 14px 4px; font-size: 9px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-faint); font-family: var(--mono); }
.sb-link { display: block; padding: 4px 14px; font-size: 11px; font-family: var(--mono); color: var(--text-dim); text-decoration: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; border-left: 2px solid transparent; transition: all 0.1s; }
.sb-link:hover { color: var(--text); border-left-color: var(--accent); background: var(--surface2); }
.sb-link.indent { padding-left: 22px; font-size: 10px; color: var(--text-faint); }
.sb-link.indent:hover { color: var(--text-dim); }
.page-hd { border-bottom: 1px solid var(--border2); padding-bottom: 20px; margin-bottom: 28px; }
.page-hd h2 { font-size: 15px; font-weight: 500; letter-spacing: -0.01em; margin-bottom: 8px; }
.stat-row { display: flex; gap: 10px; flex-wrap: wrap; }
.stat { background: var(--surface); border: 1px solid var(--border); border-radius: 3px; padding: 5px 10px; font-family: var(--mono); }
.stat-label { font-size: 9px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-faint); }
.stat-value { font-size: 12px; color: var(--accent); font-weight: 600; }
.stat-value.blue { color: var(--accent-blue); }
.stat-value.green { color: var(--accent-green); }
.section { margin-bottom: 36px; }
.section-title { font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; font-family: var(--mono); color: var(--text-dim); padding-bottom: 8px; border-bottom: 1px solid var(--border); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
.pill { font-size: 9px; padding: 1px 6px; border-radius: 2px; background: var(--surface2); border: 1px solid var(--border2); color: var(--text-faint); letter-spacing: 0.04em; }
.kv-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 8px; }
.kv { background: var(--surface); border: 1px solid var(--border); border-radius: 3px; padding: 8px 10px; }
.kv-label { font-size: 9px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-faint); font-family: var(--mono); margin-bottom: 3px; }
.kv-value { font-family: var(--mono); font-size: 11px; color: var(--text-dim); word-break: break-all; }
.kv-value.hi { color: var(--accent); }
.kv-value.green { color: var(--accent-green); }
.kv-value.blue { color: var(--accent-blue); }
.kv-value.red { color: var(--accent-red); }
.kv-value.purple { color: var(--accent-purple); }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 8px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 3px; padding: 10px 12px; }
.card-name { font-family: var(--mono); font-size: 11px; color: var(--accent); font-weight: 600; margin-bottom: 4px; }
.card-desc { font-size: 11px; color: var(--text-dim); line-height: 1.5; }
.card-file { font-family: var(--mono); font-size: 9px; color: var(--text-faint); margin-top: 5px; word-break: break-all; }
.raw-toggle { font-size: 10px; font-family: var(--mono); color: var(--text-dim); background: var(--surface2); border: 1px solid var(--border2); border-radius: 3px; padding: 3px 8px; cursor: pointer; margin-bottom: 6px; display: inline-block; }
.raw-toggle:hover { color: var(--text); }
.raw-block { background: var(--surface2); border: 1px solid var(--border); border-radius: 3px; padding: 10px 12px; font-family: var(--mono); font-size: 10px; color: var(--text-dim); white-space: pre-wrap; word-break: break-word; max-height: 300px; overflow-y: auto; line-height: 1.55; }
.turns-list { display: flex; flex-direction: column; gap: 14px; }
.turn { border: 1px solid var(--border); border-radius: 4px; overflow: hidden; }
.turn-hd { display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: var(--surface); cursor: pointer; border-bottom: 1px solid var(--border); user-select: none; }
.turn-hd:hover { background: var(--surface2); }
.turn-idx { font-family: var(--mono); font-size: 10px; color: var(--accent); min-width: 22px; }
.turn-preview { flex: 1; font-size: 11px; color: var(--text-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.turn-badges { display: flex; gap: 5px; align-items: center; flex-shrink: 0; flex-wrap: wrap; justify-content: flex-end; }
.badge { font-size: 9px; font-family: var(--mono); letter-spacing: 0.04em; padding: 1px 5px; border-radius: 2px; background: var(--surface2); border: 1px solid var(--border2); color: var(--text-faint); }
.badge.yellow { color: var(--accent); border-color: #3a2e10; }
.badge.blue { color: var(--accent-blue); border-color: #1a2a38; }
.badge.green { color: var(--accent-green); border-color: #1a2e20; }
.badge.red { color: var(--accent-red); border-color: #2e1a1a; }
.badge.purple { color: var(--accent-purple); border-color: #241e38; }
.tog-icon { font-size: 9px; color: var(--text-faint); margin-left: 4px; flex-shrink: 0; }
.turn-body { padding: 14px; display: flex; flex-direction: column; gap: 14px; }
.sub-label { font-size: 9px; letter-spacing: 0.07em; text-transform: uppercase; font-family: var(--mono); color: var(--text-faint); margin-bottom: 6px; }
.token-table { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 10px; }
.token-table th { text-align: left; padding: 4px 8px; color: var(--text-faint); font-weight: 400; border-bottom: 1px solid var(--border); font-size: 9px; letter-spacing: 0.05em; }
.token-table td { padding: 4px 8px; color: var(--text-dim); border-bottom: 1px solid var(--border); }
.token-table td.num { color: var(--accent); text-align: right; }
.token-table td.green { color: var(--accent-green); text-align: right; }
.token-table td.blue { color: var(--accent-blue); text-align: right; }
.token-table tr:last-child td { border-bottom: none; }
.msg { border-left: 2px solid var(--border2); padding: 8px 10px; margin-bottom: 6px; }
.msg.user { border-left-color: var(--accent-blue); }
.msg.final { border-left-color: var(--accent-green); }
.msg.commentary { border-left-color: var(--text-faint); }
.msg-role { font-size: 9px; font-family: var(--mono); letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 5px; }
.msg-role.user { color: var(--accent-blue); }
.msg-role.final { color: var(--accent-green); }
.msg-role.commentary { color: var(--text-faint); }
.msg-text { font-size: 12px; color: var(--text); white-space: pre-wrap; word-break: break-word; line-height: 1.6; }
.tool { background: var(--surface2); border: 1px solid var(--border); border-radius: 3px; padding: 8px 10px; margin-bottom: 6px; }
.tool-name { font-family: var(--mono); font-size: 11px; color: var(--accent); font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
.tool-kind { font-size: 9px; color: var(--text-faint); font-weight: 400; }
.tool-args { font-family: var(--mono); font-size: 10px; color: var(--text-faint); white-space: pre-wrap; max-height: 100px; overflow-y: auto; }
.tool-result { margin-top: 6px; padding-top: 6px; border-top: 1px solid var(--border); }
.tool-result-label { font-size: 9px; font-family: var(--mono); color: var(--text-faint); margin-bottom: 3px; }
.tool-result-text { font-family: var(--mono); font-size: 10px; color: var(--text-dim); white-space: pre-wrap; max-height: 80px; overflow-y: auto; }
.sep { border: none; border-top: 1px solid var(--border); margin: 24px 0; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }
@media (max-width: 680px) { .sidebar { display: none; } .main { padding: 16px; } }
"""

JS = """
function tog(id) {
    var b = document.getElementById('b' + id);
    var i = document.getElementById('i' + id);
    var hidden = b.style.display === 'none';
    b.style.display = hidden ? '' : 'none';
    i.textContent = hidden ? '▲' : '▼';
}
function togRaw(id) {
    var el = document.getElementById(id);
    el.style.display = el.style.display === 'none' ? '' : 'none';
}
"""


def e(s) -> str:
    return html.escape(str(s) if s is not None else "")


def fmt_ts(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return ts


def fmt_dur(ms) -> str:
    if ms is None:
        return "—"
    return f"{ms / 1000:.2f}s" if ms >= 1000 else f"{ms}ms"


def kv_html(label, value, cls="") -> str:
    return (
        f'<div class="kv"><div class="kv-label">{e(label)}</div>'
        f'<div class="kv-value {cls}">{e(value)}</div></div>'
    )


def raw_section(label: str, text: str, uid: str) -> str:
    if not text.strip():
        return ""
    return (
        f'<div class="sub-section" style="margin-top:12px">'
        f'<div class="sub-label">{e(label)}</div>'
        f'<span class="raw-toggle" onclick="togRaw(\'{uid}\')">show / hide raw</span>'
        f'<div class="raw-block" id="{uid}" style="display:none">{e(text.strip())}</div>'
        f'</div>'
    )


def render_session(sid: str, events: list) -> tuple:
    meta = extract_session_meta(events)
    dev_ctx = extract_developer_context(events)
    turns = extract_turns(events)

    short = sid[:8]
    ts_fmt = fmt_ts(meta.get("timestamp", ""))

    # ── Sidebar ──────────────────────────────────────────────
    turn_links = []
    for i, t in enumerate(turns, 1):
        um = t.get("user_message") or ""
        lines = [l for l in um.splitlines() if l.strip() and not l.startswith("#") and not l.startswith("-")]
        preview = lines[0][:36] if lines else "…"
        turn_links.append(
            f'<a class="sb-link indent" href="#t-{short}-{i}">#{i} {e(preview)}</a>'
        )

    sb = (
        f'<div class="sb-section">session {e(short)}</div>'
        f'<a class="sb-link" href="#sess-{e(short)}">↳ config &amp; context</a>'
        f'<a class="sb-link" href="#skills-{e(short)}">↳ skills ({len(dev_ctx["skills"])})</a>'
        f'<a class="sb-link" href="#turns-{e(short)}">↳ turns ({len(turns)})</a>'
        + "".join(turn_links)
    )

    # ── Session config ───────────────────────────────────────
    sp0 = (turns[0].get("sandbox_policy") or {}) if turns else {}
    kv_items = "".join([
        kv_html("Session ID", meta.get("id", "")),
        kv_html("Timestamp", ts_fmt),
        kv_html("CLI Version", meta.get("cli_version", ""), "blue"),
        kv_html("Model Provider", meta.get("model_provider", ""), "hi"),
        kv_html("Memory Mode", meta.get("memory_mode", ""), "green"),
        kv_html("Source", meta.get("source", "")),
        kv_html("Originator", meta.get("originator", "")),
        kv_html("Git Branch", meta.get("git_branch", ""), "blue"),
        kv_html("Git Commit", meta.get("git_commit", "")),
        kv_html("Git Repo", meta.get("git_repo", "")),
        kv_html("Working Dir", meta.get("cwd", "")),
        kv_html("Sandbox Type", sp0.get("type", "—")),
        kv_html("Network Access",
                str(sp0.get("network_access", "—")),
                "red" if sp0.get("network_access") is False else "green"),
    ])

    total_tool_calls = sum(len(t["tool_calls"]) for t in turns)
    total_reasoning = sum(t["reasoning_count"] for t in turns)

    stats = (
        '<div class="stat-row">'
        f'<div class="stat"><div class="stat-label">turns</div><div class="stat-value">{len(turns)}</div></div>'
        f'<div class="stat"><div class="stat-label">skills</div><div class="stat-value blue">{len(dev_ctx["skills"])}</div></div>'
        f'<div class="stat"><div class="stat-label">plugins</div><div class="stat-value blue">{len(dev_ctx["plugins"])}</div></div>'
        f'<div class="stat"><div class="stat-label">tool calls</div><div class="stat-value">{total_tool_calls}</div></div>'
        f'<div class="stat"><div class="stat-label">reasoning blocks</div><div class="stat-value">{total_reasoning}</div></div>'
        '</div>'
    )

    config_section = (
        f'<div class="section" id="sess-{e(short)}">'
        f'<div class="section-title">Session Configuration <span class="pill">{e(short)}</span></div>'
        f'{stats}<div style="height:12px"></div>'
        f'<div class="kv-grid">{kv_items}</div>'
        + raw_section("Base Instructions", meta.get("base_instructions", ""), f"bi-{short}")
        + raw_section("Permissions / Sandbox Policy", dev_ctx.get("permissions_raw", ""), f"perm-{short}")
        + raw_section("Collaboration Mode Instructions", dev_ctx.get("collab_mode_raw", ""), f"cm-{short}")
        + raw_section("Environment Context", dev_ctx.get("env_context_raw", ""), f"env-{short}")
        + '</div>'
    )

    # ── Skills ───────────────────────────────────────────────
    if dev_ctx["skills"]:
        cards = "".join(
            f'<div class="card"><div class="card-name">{e(s["name"])}</div>'
            f'<div class="card-desc">{e(s["description"])}</div>'
            f'<div class="card-file">{e(s["file"])}</div></div>'
            for s in dev_ctx["skills"]
        )
        skill_cards = f'<div class="card-grid">{cards}</div>'
    else:
        skill_cards = '<div style="color:var(--text-faint);font-size:11px">No skills detected.</div>'

    plugin_cards = ""
    if dev_ctx["plugins"]:
        cards = "".join(
            f'<div class="card"><div class="card-name">{e(p["name"])}</div>'
            f'<div class="card-desc">{e(p["description"])}</div></div>'
            for p in dev_ctx["plugins"]
        )
        plugin_cards = (
            '<div style="height:10px"></div>'
            '<div class="sub-label">Plugins</div>'
            f'<div class="card-grid">{cards}</div>'
        )

    skills_section = (
        f'<div class="section" id="skills-{e(short)}">'
        f'<div class="section-title">Available Skills &amp; Plugins</div>'
        f'{skill_cards}{plugin_cards}</div>'
    )

    # ── Turns ────────────────────────────────────────────────
    turns_html = []
    for i, turn in enumerate(turns, 1):
        tid = f"t-{short}-{i}"

        um = turn.get("user_message") or ""
        lines = [l for l in um.splitlines() if l.strip() and not l.startswith("#") and not l.startswith("-")]
        preview = lines[0][:72] if lines else "(no message)"

        # Badges
        badges = []
        if turn.get("model"):
            badges.append(f'<span class="badge yellow">{e(turn["model"])}</span>')
        if turn.get("effort"):
            badges.append(f'<span class="badge">{e(turn["effort"])}</span>')
        if turn.get("collab_mode"):
            badges.append(f'<span class="badge blue">{e(turn["collab_mode"])}</span>')
        sp2 = turn.get("sandbox_policy") or {}
        if sp2.get("network_access") is False:
            badges.append('<span class="badge red">no network</span>')
        if turn.get("reasoning_count", 0) > 0:
            badges.append(f'<span class="badge purple">reasoning ×{turn["reasoning_count"]}</span>')
        if turn.get("duration_ms"):
            badges.append(f'<span class="badge green">{fmt_dur(turn["duration_ms"])}</span>')

        # Turn context KVs
        tp = turn.get("truncation_policy") or {}
        ctx_kvs = "".join([
            kv_html("Model", turn.get("model") or "—", "hi"),
            kv_html("Effort", turn.get("effort") or "—"),
            kv_html("Collaboration Mode", turn.get("collab_mode") or "—", "blue"),
            kv_html("Approval Policy", turn.get("approval_policy") or "—"),
            kv_html("Sandbox Type", sp2.get("type") or "—"),
            kv_html("Network Access",
                    str(sp2.get("network_access", "—")),
                    "red" if sp2.get("network_access") is False else "green"),
            kv_html("Truncation Mode", tp.get("mode") or "—"),
            kv_html("Truncation Limit", str(tp.get("limit") or "—")),
            kv_html("Context Window",
                    f'{turn["context_window"]:,}' if turn.get("context_window") else "—"),
            kv_html("Duration", fmt_dur(turn.get("duration_ms")), "green"),
            kv_html("Time to First Token", fmt_dur(turn.get("ttft_ms"))),
            kv_html("Reasoning Blocks",
                    str(turn.get("reasoning_count", 0)),
                    "purple" if turn.get("reasoning_count", 0) > 0 else ""),
        ])
        ctx_section = (
            '<div class="sub-section">'
            '<div class="sub-label">Turn Context</div>'
            f'<div class="kv-grid">{ctx_kvs}</div>'
            '</div>'
        )

        # Token table
        token_section = ""
        if turn.get("token_snapshots"):
            rows = ""
            for snap in turn["token_snapshots"]:
                rows += (
                    f'<tr>'
                    f'<td class="num">{snap.get("input") or "—"}</td>'
                    f'<td class="green">{snap.get("cached_input") or "—"}</td>'
                    f'<td class="num">{snap.get("output") or "—"}</td>'
                    f'<td class="blue">{snap.get("reasoning_output") or "—"}</td>'
                    f'<td class="num">{snap.get("total_turn") or "—"}</td>'
                    f'<td class="num">{snap.get("total_session") or "—"}</td>'
                    f'<td>{snap.get("rate_used_pct") or "—"}%</td>'
                    f'<td>{snap.get("plan_type") or "—"}</td>'
                    f'</tr>'
                )
            token_section = (
                '<div class="sub-section">'
                '<div class="sub-label">Token Usage</div>'
                '<table class="token-table"><thead><tr>'
                '<th>input</th><th>cached in</th><th>output</th><th>reasoning out</th>'
                '<th>turn total</th><th>session total</th><th>rate used</th><th>plan</th>'
                f'</tr></thead><tbody>{rows}</tbody></table>'
                '</div>'
            )

        # User message
        user_section = ""
        if um:
            req_start = 0
            for li, l in enumerate(um.splitlines()):
                if "## My request" in l:
                    req_start = li + 1
                    break
            actual = "\n".join(um.splitlines()[req_start:]).strip() if req_start else um
            user_section = (
                '<div class="sub-section">'
                '<div class="sub-label">User Message</div>'
                f'<div class="msg user"><div class="msg-role user">User</div>'
                f'<div class="msg-text">{e(actual)}</div></div>'
                '</div>'
            )

        # Tool calls
        tool_section = ""
        if turn.get("tool_calls"):
            tools_inner = ""
            for tc in turn["tool_calls"]:
                result_html = ""
                if tc.get("result"):
                    result_html = (
                        '<div class="tool-result">'
                        '<div class="tool-result-label">result</div>'
                        f'<div class="tool-result-text">{e(tc["result"])}</div>'
                        '</div>'
                    )
                tools_inner += (
                    '<div class="tool">'
                    f'<div class="tool-name">{e(tc["name"])} '
                    f'<span class="tool-kind">{e(tc.get("kind", ""))}</span></div>'
                    f'<div class="tool-args">{e(tc.get("args", ""))}</div>'
                    f'{result_html}</div>'
                )
            tool_section = (
                '<div class="sub-section">'
                f'<div class="sub-label">Tool Calls ({len(turn["tool_calls"])})</div>'
                f'{tools_inner}</div>'
            )

        # Assistant messages
        asst_section = ""
        if turn.get("assistant_messages"):
            msgs = ""
            for msg in turn["assistant_messages"]:
                phase = msg.get("phase", "")
                cls = "final" if phase == "final_answer" else "commentary"
                label = phase.replace("_", " ") if phase else "assistant"
                msgs += (
                    f'<div class="msg {cls}">'
                    f'<div class="msg-role {cls}">{e(label)}</div>'
                    f'<div class="msg-text">{e(msg["text"])}</div>'
                    f'</div>'
                )
            asst_section = (
                '<div class="sub-section">'
                '<div class="sub-label">Assistant Output</div>'
                f'{msgs}</div>'
            )

        turn_html = (
            f'<div class="turn" id="{tid}">'
            f'<div class="turn-hd" onclick="tog(\'{tid}\')">'
            f'<span class="turn-idx">#{i}</span>'
            f'<span class="turn-preview">{e(preview)}</span>'
            f'<span class="turn-badges">{"".join(badges)}</span>'
            f'<span class="tog-icon" id="i{tid}">▲</span>'
            f'</div>'
            f'<div class="turn-body" id="b{tid}">'
            f'{ctx_section}{token_section}{user_section}{tool_section}{asst_section}'
            f'</div></div>'
        )
        turns_html.append(turn_html)

    turns_section = (
        f'<div class="section" id="turns-{e(short)}">'
        f'<div class="section-title">Turns <span class="pill">{len(turns)}</span></div>'
        f'<div class="turns-list">{"".join(turns_html)}</div>'
        f'</div>'
    )

    main = (
        '<div style="margin-bottom:48px">'
        f'<div class="page-hd">'
        f'<h2>Session <span style="font-family:var(--mono);color:var(--accent)">{e(short)}</span></h2>'
        f'<div style="font-size:11px;color:var(--text-dim);margin-top:4px">'
        f'{e(ts_fmt)} · {e(meta.get("git_branch",""))} · {e(meta.get("model_provider",""))}'
        f'</div></div>'
        f'{config_section}'
        f'<hr class="sep">'
        f'{skills_section}'
        f'<hr class="sep">'
        f'{turns_section}'
        f'</div>'
    )

    return sb, main


def render_html(sessions: dict, source_path: Path, filter_sid=None) -> str:
    all_sb = []
    all_main = []
    total_sessions = 0
    total_turns = 0

    for sid, events in sessions.items():
        if filter_sid and sid != filter_sid:
            continue
        sb, main = render_session(sid, events)
        all_sb.append(sb)
        all_main.append(main)
        total_sessions += 1
        total_turns += len(extract_turns(events))

    top_stats = (
        '<div class="stat-row" style="margin-bottom:28px">'
        f'<div class="stat"><div class="stat-label">file</div>'
        f'<div class="stat-value" style="font-size:10px">{e(source_path.name)}</div></div>'
        f'<div class="stat"><div class="stat-label">sessions</div>'
        f'<div class="stat-value">{total_sessions}</div></div>'
        f'<div class="stat"><div class="stat-label">turns</div>'
        f'<div class="stat-value">{total_turns}</div></div>'
        '</div>'
    )

    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Codex Observability Log — Agent Ecosystem Testing</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600'
        '&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">\n'
        f'<style>{CSS}</style>\n'
        '</head>\n<body>\n'
        '<div class="layout">\n'
        '<nav class="sidebar">\n'
        '<div class="sb-logo"><h1>Observability Log</h1><p>Agent Ecosystem Testing</p></div>\n'
        + "".join(all_sb)
        + '\n</nav>\n<main class="main">\n'
        + top_stats
        + "".join(all_main)
        + '\n</main>\n</div>\n'
        f'<script>{JS}</script>\n'
        '</body>\n</html>'
    )


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def list_sessions(sessions: dict) -> None:
    print(f"\n{'SESSION ID':<40}  {'DATE':<20}  {'TURNS':>5}  {'SKILLS':>6}  {'BRANCH'}")
    print("─" * 96)
    for sid, events in sessions.items():
        meta = extract_session_meta(events)
        dev_ctx = extract_developer_context(events)
        turns = extract_turns(events)
        ts = fmt_ts(meta.get("timestamp", ""))[:19]
        branch = meta.get("git_branch", "")
        print(f"{sid:<40}  {ts:<20}  {len(turns):>5}  {len(dev_ctx['skills']):>6}  {branch}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Codex session observability log — surfaces config, skills, tokens, and tools."
    )
    parser.add_argument("session_file", help="Path to a Codex .jsonl session file")
    parser.add_argument("--output", "-o", help="Output HTML file (default: same name, .html extension)")
    parser.add_argument("--session-id", help="Render a specific session ID only")
    parser.add_argument("--list-sessions", action="store_true", help="List sessions and exit")
    args = parser.parse_args()

    path = Path(args.session_file).expanduser()
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing {path} …", file=sys.stderr)
    events = parse_ndjson(path)
    print(f"  {len(events)} events", file=sys.stderr)

    sessions = group_by_session(events)
    print(f"  {len(sessions)} session(s)", file=sys.stderr)

    if args.list_sessions:
        list_sessions(sessions)
        return

    out_path = Path(args.output) if args.output else path.with_suffix(".html")
    out = render_html(sessions, path, filter_sid=args.session_id)
    out_path.write_text(out, encoding="utf-8")
    print(f"\nWrote  → {out_path}", file=sys.stderr)
    print(f"Open:    open {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()