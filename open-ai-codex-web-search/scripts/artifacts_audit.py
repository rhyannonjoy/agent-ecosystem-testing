#!/usr/bin/env python3
"""Audit Codex filesystem-event JSONL logs from artifacts_watcher.py.

Focuses on temporary artifacts (by default /private/tmp) so you can see which
Codex test run created what, whether temp files were moved to a workspace, and
whether the same basename appears under more than one temp directory (naming
collisions).

Usage:
    # Audit everything written to /private/tmp for one run
    python3 scripts/artifacts_audit.py \
        results/vscode-codex-interpreted/artifacts/fs-events/EC-1/*.jsonl

    # Focus strictly on /private/tmp and include delete timestamps
    python3 scripts/artifacts_audit.py .../*.jsonl --temp-root /private/tmp \
        --include created moved deleted

    # Also audit the resolved macOS $TMPDIR
    python3 scripts/artifacts_audit.py .../*.jsonl \
        --temp-root /private/tmp --temp-root "$TMPDIR"

    # Copy-paste friendly CSV for docs
    python3 scripts/artifacts_audit.py .../*.jsonl --csv temp_artifacts.csv

Exit code is nonzero if any anomaly flag fires.
"""

import argparse
import csv
import glob
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ELIDE_DIRS = {".git", "__pycache__"}


def format_duration(seconds: float | None) -> str:
    """Return a concise duration like '0:23' or '5:03.1'."""
    if seconds is None:
        return "—"
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    remaining = seconds - minutes * 60
    return f"{minutes}:{int(remaining):02d}"


def human_bytes(n: int | None) -> str:
    if n is None:
        return "—"
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024 or unit == "GB":
            if unit == "B" or n == int(n):
                return f"{int(n)} {unit}"
            return f"{n:.1f} {unit}"
        n /= 1024
    return "—"  # pragma: no cover


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def default_temp_roots() -> list[Path]:
    """Default temp directory to audit: /private/tmp.

    The watcher also records $TMPDIR and ~/.codex, but when a user asks
    "what was written to /private/tmp" they usually mean the literal path.
    Pass --temp-root repeatedly to include other roots.
    """
    p = Path("/private/tmp")
    if p.exists():
        return [p.resolve()]
    # Last-ditch fallback so the script still runs on Linux.
    return [Path("/tmp").resolve()]


def is_under(path: Path, roots: list[Path]) -> Path | None:
    """Return the matching root if path is under one of them, else None."""
    if not path:
        return None
    path = path.resolve()
    for root in roots:
        try:
            path.relative_to(root)
            return root
        except ValueError:
            continue
    return None


def temp_session_dir(path: Path, root: Path) -> str:
    """Return the first segment under the temp root for nested files.

    Files placed directly in the temp root return '' so they group together.
    e.g. /private/tmp/diff.ABC        -> ''
         /private/tmp/codex-ABC/data  -> 'codex-ABC'
    """
    try:
        rel = path.resolve().relative_to(root)
    except ValueError:
        return ""
    if len(rel.parts) > 1:
        return str(rel.parts[0])
    return ""


def load_records(path: Path) -> list[dict]:
    records = []
    with open(path, "r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  WARNING {path.name}:{n} unparseable: {e}", file=sys.stderr)
    return records


def audit_file(path: Path, temp_roots: list[Path]) -> dict:
    records = load_records(path)

    # Aggregate temp artifacts by absolute path.
    artifacts: dict[Path, dict] = {}
    event_counts = Counter()
    temp_event_counts = Counter()
    first_ts = last_ts = None
    largest_file: tuple[int | None, Path | None] = (None, None)

    for rec in records:
        ts = rec.get("timestamp")
        if ts:
            t = parse_ts(ts)
            first_ts = first_ts or t
            last_ts = t

        event_type = rec.get("event_type")
        event_counts[event_type] += 1

        src = Path(rec.get("src_path") or "")
        dest_raw = rec.get("dest_path")
        dest = Path(dest_raw) if dest_raw else None

        root = is_under(src, temp_roots)
        if root:
            temp_event_counts[event_type] += 1

        # Ensure both src and dest have artifact entries when under temp roots.
        for p, moved_from, moved_to in (
            (src, None, str(dest) if dest else None),
            (dest, str(src) if src else None, None),
        ):
            if not p or not p.is_absolute():
                continue
            matched_root = is_under(p, temp_roots)
            if not matched_root:
                continue
            if p not in artifacts:
                artifacts[p] = {
                    "created_ts": None,
                    "deleted_ts": None,
                    "moved_to": [],
                    "moved_from": None,
                    "modified_count": 0,
                    "max_size": rec.get("size") if p == src else None,
                    "is_directory": rec.get("is_directory", False),
                    "event_types": Counter(),
                    "root": matched_root,
                    "session_dir": "",
                }
            art = artifacts[p]
            art["event_types"][event_type] += 1
            art["session_dir"] = temp_session_dir(p, art["root"])
            size = rec.get("size")
            if size is not None and (art["max_size"] is None or size > art["max_size"]):
                art["max_size"] = size
            if event_type == "created" and art["created_ts"] is None:
                art["created_ts"] = ts
            if event_type == "modified":
                art["modified_count"] += 1
            if event_type == "deleted" and art["deleted_ts"] is None:
                art["deleted_ts"] = ts
            if moved_from and moved_from not in (art["moved_from"],):
                art["moved_from"] = moved_from
            if moved_to and moved_to not in art["moved_to"]:
                art["moved_to"].append(moved_to)

        # Largest temp file observed (size from create/modified event).
        if root and not src.is_dir() and rec.get("size"):
            size = rec["size"]
            if largest_file[0] is None or size > largest_file[0]:
                largest_file = (size, src)

    if not records:
        wallclock_s = None
    elif first_ts and last_ts:
        wallclock_s = round((last_ts - first_ts).total_seconds(), 1)
    else:
        wallclock_s = None

    created_temp = [p for p, a in artifacts.items() if a["event_types"].get("created", 0) > 0]
    created_files = [p for p in created_temp if not artifacts[p]["is_directory"]]
    created_dirs = [p for p in created_temp if artifacts[p]["is_directory"]]

    # Unmoved: created under temp and never moved or deleted.
    unmoved = [
        p for p in created_files
        if not artifacts[p]["moved_to"] and artifacts[p]["deleted_ts"] is None
    ]

    moved = [(p, artifacts[p]["moved_to"][0]) for p in created_files if artifacts[p]["moved_to"]]

    # Naive naming collision candidates per file: basename appears under more
    # than one temp session directory.
    basenames_by_session: dict[str, set[str]] = defaultdict(set)
    for p in created_files:
        a = artifacts[p]
        basenames_by_session[p.name].add(a["session_dir"])
    local_collisions = {
        name: sessions
        for name, sessions in basenames_by_session.items()
        if len(sessions) > 1
    }

    test_id = records[0].get("test_id") if records else None
    track = records[0].get("track") if records else None
    model = records[0].get("model") if records else None
    effort = records[0].get("effort") if records else None

    return {
        "file": path.name,
        "path": path,
        "test_id": test_id,
        "track": track,
        "model": model,
        "effort": effort,
        "records": len(records),
        "wallclock_s": wallclock_s,
        "event_counts": event_counts,
        "temp_event_counts": temp_event_counts,
        "temp_artifacts": artifacts,
        "created_files": created_files,
        "created_dirs": created_dirs,
        "moved": moved,
        "unmoved": unmoved,
        "local_collisions": local_collisions,
        "largest_file": largest_file,
        "flags": [],
    }


def format_artifact_history(a: dict, include: list[str]) -> str:
    """A concise summary of an artifact's event history."""
    parts = []
    if "created" in include and a["created_ts"]:
        parts.append(f"created {a['created_ts'][11:19]}")
    if "modified" in include and a["modified_count"]:
        parts.append(f"modified {a['modified_count']}x")
    if "moved" in include and a["moved_to"]:
        dest = a["moved_to"][0]
        parts.append(f"moved → {dest}")
    if "deleted" in include and a["deleted_ts"]:
        parts.append(f"deleted {a['deleted_ts'][11:19]}")
    if not parts:
        return ""
    return " | ".join(parts)


def summarize_events(types: Counter, kind: str) -> str:
    """Return a human sentence for event counts, omitting zeroes."""
    parts = []
    for label, key in (
        ("created", "created"),
        ("modified", "modified"),
        ("moved", "moved"),
        ("deleted", "deleted"),
    ):
        n = types.get(key, 0)
        if n:
            parts.append(f"{n} {label}")
    if not parts:
        return f"no {kind} events"
    return ", ".join(parts)


def temp_root_label(root: Path) -> str:
    """Short label for a temp root."""
    resolved = root.resolve()
    tmpdir_resolved = Path(os.environ.get("TMPDIR", "/tmp")).resolve()
    if resolved == tmpdir_resolved:
        return "$TMPDIR"
    return str(resolved)


def group_by_session_dir(paths: list[Path], artifacts: dict[Path, dict]) -> dict[str, list[Path]]:
    """Group created paths by their immediate temp session directory."""
    groups: dict[str, list[Path]] = defaultdict(list)
    for p in paths:
        groups[artifacts[p]["session_dir"]].append(p)
    return dict(groups)


def directory_total_size(paths: list[Path], artifacts: dict[Path, dict]) -> int:
    """Sum the largest observed size for each file in the group."""
    total = 0
    for p in paths:
        size = artifacts[p]["max_size"]
        if size is not None:
            total += size
    return total


def generate_flags(r: dict, churn_threshold: int) -> list[str]:
    flags = []

    if r["unmoved"]:
        flags.append(
            f"TEMP_UNMOVED: {len(r['unmoved'])} temp file(s) created but never moved/deleted "
            "within the observation window"
        )

    if r["local_collisions"]:
        detail = ", ".join(
            f"{name!r} in {len(sessions)} dirs"
            for name, sessions in sorted(r["local_collisions"].items())[:5]
        )
        if len(r["local_collisions"]) > 5:
            detail += f", ... ({len(r['local_collisions']) - 5} more)"
        flags.append(f"NAMING_COLLISION: {detail}")

    churners = [
        (p, r["temp_artifacts"][p]["modified_count"])
        for p in r["created_files"]
        if r["temp_artifacts"][p]["modified_count"] >= churn_threshold
    ]
    if churners:
        churners.sort(key=lambda x: x[1], reverse=True)
        flags.append(
            f"HIGH_CHURN: {len(churners)} file(s) modified >= {churn_threshold}x "
            f"(top: {churners[0][0].name} @ {churners[0][1]}x)"
        )

    return flags


def print_summary(r: dict, temp_roots: list[Path], include: list[str], max_files: int) -> None:
    print("=" * 78)
    print(f"{r['file']}")
    model_effort = " | ".join(
        x for x in (r.get("model"), r.get("effort")) if x
    ) or "model/effort not recorded"
    print(f"  run: {r['test_id']} | track: {r['track']} | {model_effort} | "
          f"{r['records']} event(s) | wallclock {format_duration(r['wallclock_s'])}")
    print(f"  all events: {summarize_events(r['event_counts'], 'filesystem')}")
    print(f"  temp events: {summarize_events(r['temp_event_counts'], 'temp')}")

    if r["largest_file"][1]:
        size, path = r["largest_file"]
        print(f"  largest temp file: {human_bytes(size)}  {path}")

    any_root_output = False
    for root in temp_roots:
        created_here = [p for p in r["created_files"] if is_under(p, [root])]
        created_dirs_here = [p for p in r["created_dirs"] if is_under(p, [root])]
        if not created_here and not created_dirs_here:
            print(f"  {temp_root_label(root)}: no created temp artifacts")
            continue

        any_root_output = True
        print(f"  {temp_root_label(root)}: {len(created_here)} file(s), "
              f"{len(created_dirs_here)} dir(s) created")

        groups = group_by_session_dir(created_here, r["temp_artifacts"])
        # Files not under a session subdir come first (empty key).
        for session_dir in sorted(groups, key=lambda k: (k != "", k)):
            paths = groups[session_dir]
            if session_dir:
                total_size = directory_total_size(paths, r["temp_artifacts"])
                print(f"    [{session_dir}/]  {len(paths)} file(s), {human_bytes(total_size)}")
                indent = "      "
            else:
                indent = "    "

            # Sort by size descending, name ascending for stability.
            paths.sort(key=lambda p: (-(r["temp_artifacts"][p]["max_size"] or 0), p.name))
            shown = paths[:max_files] if max_files > 0 else paths
            for p in shown:
                a = r["temp_artifacts"][p]
                history = format_artifact_history(a, include)
                marker = ""
                if p in r["unmoved"]:
                    marker = " [UNMOVED]"
                line = f"{indent}{human_bytes(a['max_size']):>10s}  {p.name}{marker}"
                if history:
                    line += f"  ({history})"
                print(line)
            remainder = len(paths) - len(shown)
            if remainder > 0:
                print(f"{indent}... and {remainder} more file(s) in this dir")

    if not any_root_output:
        print("  (no temp artifacts created under the selected roots)")

    if r["local_collisions"]:
        print("  local naming collisions:")
        for name, sessions in sorted(r["local_collisions"].items()):
            print(f"    {name!r} appears under {len(sessions)} temp dirs: "
                  f"{', '.join(sorted(sessions))}")

    if r["flags"]:
        for fl in r["flags"]:
            print(f"  !! {fl}")
    else:
        print("  OK: all created temp files were moved or deleted, no local naming collisions")


def detect_global_collisions(results: list[dict]) -> dict[str, list[tuple[str, Path]]]:
    """Detect basenames that appear as created temp files in multiple runs.

    Because Codex writes many artifacts directly into /private/tmp, the
    collision we care about is the same basename reused across watcher files
    (i.e. across test runs), not just across parent directories.
    """
    by_basename: dict[str, list[tuple[str, Path]]] = defaultdict(list)
    seen = set()
    for r in results:
        for p in r["created_files"]:
            key = (r["file"], str(p))
            if key in seen:
                continue
            seen.add(key)
            by_basename[p.name].append((r["file"], p))
    return {
        name: locs for name, locs in by_basename.items()
        if len({f for f, _ in locs}) > 1
    }


def main():
    ap = argparse.ArgumentParser(
        description="Audit Codex artifacts_watcher JSONL logs, focusing on temp files."
    )
    ap.add_argument("paths", nargs="+", help="jsonl files or globs")
    ap.add_argument(
        "--temp-root",
        action="append",
        type=Path,
        help="Temp root to focus on (may be given multiple times). "
             "Default: /private/tmp (falls back to /tmp on Linux).",
    )
    ap.add_argument(
        "--include",
        nargs="+",
        default=["created", "moved"],
        choices=["created", "modified", "moved", "deleted"],
        help="Event types to show in artifact history lines (default: created moved)",
    )
    ap.add_argument(
        "--max-files",
        type=int,
        default=15,
        help="Max files to list per temp session directory (default: 15; 0 = unlimited)",
    )
    ap.add_argument(
        "--churn-threshold",
        type=int,
        default=5,
        help="Flag temp files modified at least this many times (default: 5)",
    )
    ap.add_argument("--csv", help="also write results to this CSV path")
    args = ap.parse_args()

    temp_roots = [p.resolve() for p in (args.temp_root or default_temp_roots())]
    if not temp_roots:
        print("ERROR: no temp roots exist and none were specified", file=sys.stderr)
        sys.exit(1)

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
        r = audit_file(f, temp_roots)
        r["flags"] = generate_flags(r, args.churn_threshold)
        results.append(r)

    for r in results:
        print_summary(r, temp_roots, args.include, args.max_files)

    # Global cross-run collision report.
    global_collisions = detect_global_collisions(results)
    if global_collisions:
        print()
        print("=" * 78)
        print("GLOBAL NAMING COLLISIONS across input files")
        print("-" * 78)
        for name, locs in sorted(global_collisions.items()):
            unique_files = sorted({f for f, _ in locs})
            print(f"  {name!r}")
            print(f"    appears in {len(unique_files)} watcher file(s)")
            for f, p in locs[:15]:
                print(f"      {f}: {p}")
            if len(locs) > 15:
                print(f"      ... and {len(locs) - 15} more occurrence(s)")
        print()
        for r in results:
            participates = any(
                name in r["local_collisions"] or any(f == r["file"] for f, _ in locs)
                for name, locs in global_collisions.items()
            )
            if participates and not any("NAMING_COLLISION" in fl for fl in r["flags"]):
                r["flags"].append(
                    "NAMING_COLLISION: basename shared with another run or temp dir"
                )

    if args.csv and results:
        cols = [
            "file", "test_id", "track", "model", "effort", "records", "wallclock_s",
            "temp_event_created", "temp_event_modified", "temp_event_moved",
            "temp_event_deleted", "temp_created_files", "temp_created_dirs",
            "temp_moved_files", "temp_unmoved_files",
            "temp_largest_file_bytes", "temp_largest_file_path",
            "local_collision_count", "global_collision_count", "flags",
        ]
        with open(args.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in results:
                tec = r["temp_event_counts"]
                row = {
                    "file": r["file"],
                    "test_id": r["test_id"],
                    "track": r["track"],
                    "model": r.get("model") or "",
                    "effort": r.get("effort") or "",
                    "records": r["records"],
                    "wallclock_s": r["wallclock_s"],
                    "temp_event_created": tec.get("created", 0),
                    "temp_event_modified": tec.get("modified", 0),
                    "temp_event_moved": tec.get("moved", 0),
                    "temp_event_deleted": tec.get("deleted", 0),
                    "temp_created_files": len(r["created_files"]),
                    "temp_created_dirs": len(r["created_dirs"]),
                    "temp_moved_files": len(r["moved"]),
                    "temp_unmoved_files": len(r["unmoved"]),
                    "temp_largest_file_bytes": r["largest_file"][0],
                    "temp_largest_file_path": str(r["largest_file"][1]) if r["largest_file"][1] else "",
                    "local_collision_count": len(r["local_collisions"]),
                    "global_collision_count": sum(
                        1 for locs in global_collisions.values()
                        if any(f == r["file"] for f, _ in locs)
                    ),
                    "flags": "; ".join(r["flags"]),
                }
                w.writerow(row)
        print(f"CSV written to {args.csv}")

    any_flags = any(r["flags"] for r in results)
    sys.exit(1 if any_flags else 0)


if __name__ == "__main__":
    main()
