#!/usr/bin/env python3
"""artifacts_watcher.py — Record filesystem events during a Codex session.

Codex rollouts do not log temp-file creation or workspace artifact writes.
This watcher runs in parallel with a test and records create/modify/move/delete
events under ~/.codex and the macOS temp directories. The resulting JSONL log
can be correlated with rollout_audit.py CSV output by session id and timestamp.

Usage:
    # Start before the Codex test
    python3 scripts/artifacts_watcher.py --test SC-4 --track vscode-codex-interpreted

    # Stop with Ctrl-C after the Codex turn completes

    # Custom output location
    python3 scripts/artifacts_watcher.py --test SC-4 --track vscode-codex-interpreted \
        --output /tmp/sc4-fs-events.jsonl

Output format (one JSON object per line):
    {
      "timestamp": "2026-06-27T02:15:03.123456+00:00",
      "event_type": "modified",
      "src_path": "/private/tmp/codex-.../data.html",
      "dest_path": null,
      "size": 64659,
      "is_directory": false,
      "test_id": "SC-4",
      "track": "vscode-codex-interpreted"
    }
"""

import argparse
import json
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


DEFAULT_WATCH_PATHS = [
    Path.home() / ".codex",
    Path("/private/tmp"),
    Path(os.environ.get("TMPDIR", "/tmp")),
]

DEFAULT_EXCLUDE_PATTERNS = [
    ".DS_Store",
    "*.swp",
    "*.swo",
    "*~",
    "#*#",
    ".git/",
    "__pycache__/",
    "*.pyc",
]

# Path-segment patterns to skip. macOS services write constantly under the user
# tempdir, and Codex artifacts almost never live inside these subdirectories.
DEFAULT_PATH_EXCLUDE_PATTERNS = [
    "com.apple.*",
    ".icloud",
    "FileProvider",
    "NSFileProvider",
    "TemporaryItems",
    "DocumentRevisions-*",
]


def should_ignore(path: Path, patterns: list[str]) -> bool:
    """Return True if any exclude pattern matches the path name."""
    name = path.name
    for pat in patterns:
        if pat.endswith("/"):
            if path.is_dir() and name == pat.rstrip("/"):
                return True
        if name == pat or name.endswith(pat.lstrip("*")):
            return True
    return False


def should_ignore_path(path: Path, path_patterns: list[str]) -> bool:
    """Return True if any path segment matches a path-exclude glob."""
    parts = path.parts
    for pat in path_patterns:
        # Match whole segments only (e.g. `com.apple.*` matches `com.apple.bird`).
        pat_clean = pat.rstrip("/")
        for part in parts:
            if pat_clean.startswith("*"):
                if part.endswith(pat_clean.lstrip("*")):
                    return True
            elif part == pat_clean or (pat_clean.endswith("*") and part.startswith(pat_clean.rstrip("*"))):
                return True
    return False


def file_size(path: str) -> int | None:
    try:
        st = os.stat(path)
        if os.path.isfile(path):
            return st.st_size
    except OSError:
        pass
    return None


class ArtifactEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        test_id: str,
        track: str,
        exclude_patterns: list[str],
        path_exclude_patterns: list[str],
        out_fh,
    ):
        self.test_id = test_id
        self.track = track
        self.exclude_patterns = exclude_patterns
        self.path_exclude_patterns = path_exclude_patterns
        self.out_fh = out_fh
        self._stopped = False
        self._event_count = 0

    def on_any_event(self, event):
        if self._stopped:
            return

        # Ignore directory traversal noise and filtered names.
        src = Path(event.src_path)
        if should_ignore(src, self.exclude_patterns):
            return
        if should_ignore_path(src, self.path_exclude_patterns):
            return

        dest = Path(event.dest_path) if getattr(event, "dest_path", None) else None
        if dest and should_ignore(dest, self.exclude_patterns):
            return
        if dest and should_ignore_path(dest, self.path_exclude_patterns):
            return

        # Skip events for the watcher itself.
        if src.name.startswith("fs-events-") and src.suffix == ".jsonl":
            return

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event.event_type,
            "src_path": str(src),
            "dest_path": str(dest) if dest else None,
            "size": file_size(event.src_path),
            "is_directory": event.is_directory,
            "test_id": self.test_id,
            "track": self.track,
        }
        self.out_fh.write(json.dumps(record, default=str) + "\n")
        self.out_fh.flush()
        self._event_count += 1


def default_output_path(track: str, test_id: str) -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    out_dir = repo_root / "results" / track / "artifacts" / "fs-events" / test_id
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"fs-events-{ts}.jsonl"


def watch_paths_for_host() -> list[Path]:
    """Return watch paths that exist on this machine."""
    return [p for p in DEFAULT_WATCH_PATHS if p.exists()]


def main():
    ap = argparse.ArgumentParser(
        description="Watch filesystem activity while a Codex session runs."
    )
    ap.add_argument("--test", required=True, help="Test ID, e.g. SC-4")
    ap.add_argument("--track", required=True, help="Track name, e.g. vscode-codex-interpreted")
    ap.add_argument("--output", "-o", type=Path, help="Output JSONL path")
    ap.add_argument(
        "--watch",
        action="append",
        type=Path,
        help="Additional directories to watch (may be given multiple times)",
    )
    ap.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional filename patterns to ignore",
    )
    ap.add_argument(
        "--path-exclude",
        action="append",
        default=[],
        help="Additional path-segment patterns to ignore (e.g. 'com.apple.*')",
    )
    ap.add_argument(
        "--quiet",
        action="store_true",
        help="Only print errors and the final summary",
    )
    args = ap.parse_args()

    watch_paths = watch_paths_for_host()
    if args.watch:
        watch_paths.extend(args.watch)
    watch_paths = sorted({p.resolve() for p in watch_paths})

    if not watch_paths:
        print("ERROR: no watch directories exist", file=sys.stderr)
        sys.exit(1)

    exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + args.exclude
    path_exclude_patterns = DEFAULT_PATH_EXCLUDE_PATTERNS + args.path_exclude

    output_path = args.output or default_output_path(args.track, args.test)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    with open(output_path, "w", encoding="utf-8") as out_fh:
        handler = ArtifactEventHandler(
            args.test, args.track, exclude_patterns, path_exclude_patterns, out_fh
        )

        for p in watch_paths:
            observer.schedule(handler, str(p), recursive=True)

        def shutdown(signum, frame):
            if not args.quiet:
                print("\nShutting down watcher...", file=sys.stderr)
            observer.stop()
            handler._stopped = True

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        observer.start()

        if not args.quiet:
            print(f"Watching {len(watch_paths)} path(s):", file=sys.stderr)
            for p in watch_paths:
                print(f"  {p}", file=sys.stderr)
            print(f"Writing events to {output_path}", file=sys.stderr)
            print("Press Ctrl-C to stop.", file=sys.stderr)

        try:
            while observer.is_alive():
                observer.join(0.5)
        finally:
            observer.stop()
            observer.join()

    if not args.quiet:
        print(f"Wrote {handler._event_count} event(s) to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
