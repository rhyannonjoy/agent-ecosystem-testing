import csv

input_path = "results/codex-interpreted/results.csv"
output_path = "results/codex-interpreted/results_fixed.csv"

with open(input_path, newline="") as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
expected_cols = 48

# Identify where the 4 fields should be inserted (after tokens_est)
insert_after = header.index("tokens_est") + 1
new_fields = ["escalation_trigger", "artifact_path", "artifact_size_bytes", "last_50_chars"]
fixed_header = header[:insert_after] + new_fields + header[insert_after:]

fixed_rows = [fixed_header]
for row in rows[1:]:
    if len(row) == 44:
        # Pad with 4 empty values at the same insertion point
        fixed_row = row[:insert_after] + ["", "", "", ""] + row[insert_after:]
    else:
        fixed_row = row  # already 48, leave alone
    fixed_rows.append(fixed_row)

with open(output_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(fixed_rows)

print(f"Done. Verify {output_path} before replacing original.")