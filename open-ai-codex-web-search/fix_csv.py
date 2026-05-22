"""
fix_csv.py — repairs results.csv for the Codex testing framework

Problems fixed:
  1. Header missing 4 raw-track columns: escalation_trigger, artifact_path,
     artifact_size_bytes, last_50_chars (should appear after execution_attempts)
  2. Header has wrong name: agent_reported_truncation_point → agent_reported_truncation_note
  3. Old 44-column rows are missing the 4 values at position 24, causing every
     agent_reported_* and verified_* column to read shifted/wrong data

Usage:
    python fix_csv.py                          # reads results.csv, writes results_fixed.csv
    python fix_csv.py my/path/results.csv      # custom input path
"""

import csv
import sys
from pathlib import Path

INPUT  = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results.csv")
OUTPUT = INPUT.with_name("results_fixed.csv")

CORRECT_HEADER = [
    "test_id", "timestamp", "date", "url", "track", "surface", "method",
    "workspace_present", "permission_level", "model_observed", "model_intelligence_level",
    "input_est_chars", "hypothesis_match", "codex_version", "notes",
    "tools_named", "workspace_substitution",
    "output_chars", "truncated", "truncation_note", "tokens_est",
    "tools_used", "tools_blocked", "execution_attempts",
    # --- 4 columns that were missing from the old header ---
    "escalation_trigger", "artifact_path", "artifact_size_bytes", "last_50_chars",
    # --- agent_reported_* (note: truncation_note not truncation_point) ---
    "agent_reported_output_chars", "agent_reported_truncated",
    "agent_reported_truncation_note", "agent_reported_tokens_est",
    "agent_reported_file_size_bytes", "agent_reported_md5_checksum",
    "agent_reported_lines", "agent_reported_words", "agent_reported_code_blocks",
    "agent_reported_table_rows", "agent_reported_headers",
    # --- verified_* ---
    "verified_file_size_bytes", "verified_md5_checksum", "verified_total_lines",
    "verified_total_words", "verified_tokens", "verified_chars_per_token",
    "verified_code_blocks", "verified_table_rows", "verified_headers",
]

# The 4 missing columns belong right after execution_attempts (index 23)
INSERT_AT    = 24
INSERT_COUNT = 4
TARGET_COLS  = 48

assert len(CORRECT_HEADER) == TARGET_COLS, "Header definition error"

with open(INPUT, newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))

old_header = rows[0]
print(f"Input:      {INPUT}")
print(f"Old header: {len(old_header)} columns")

if len(old_header) == TARGET_COLS:
    print("Header already has 48 columns — checking for misnamed column only.")

fixed_rows  = [CORRECT_HEADER]
counts      = {44: 0, 48: 0, "other": 0}
warnings    = []

for line_num, row in enumerate(rows[1:], start=2):
    n = len(row)

    if n == 44:
        # Insert 4 empty strings at the position where the raw-track columns belong
        fixed = row[:INSERT_AT] + [""] * INSERT_COUNT + row[INSERT_AT:]
        counts[44] += 1

    elif n == TARGET_COLS:
        # Already correct width — pass through unchanged
        fixed = row
        counts[48] += 1

    else:
        warnings.append(f"  line {line_num}: unexpected {n} columns — passed through unchanged")
        fixed = row
        counts["other"] += 1

    fixed_rows.append(fixed)

# Verify all rows are now the right width (skip "other" rows)
bad = [
    i + 2
    for i, r in enumerate(fixed_rows[1:])
    if len(r) != TARGET_COLS and len(rows[1:][i]) != counts["other"]
]

if warnings:
    print("\nWarnings:")
    for w in warnings:
        print(w)

print(f"\nRows padded 44 → 48:  {counts[44]}")
print(f"Rows already 48:      {counts[48]}")
print(f"Rows other (skipped): {counts['other']}")
print(f"Total data rows:      {len(fixed_rows) - 1}")

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(fixed_rows)

print(f"\nWritten to: {OUTPUT}")
print("Verify it looks correct before replacing your original.")