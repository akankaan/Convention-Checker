#!/usr/bin/env bash

if [ $# -ne 1 ]; then
  echo "Usage: ./run_check-lab1.sh <username>"
  exit 1
fi

USERNAME="$1"
# if feed in abc123/ then username is just abc123
USERNAME="${USERNAME%/}"
BASE_PATH="$USERNAME/lab1"
CHECKER="python3 convention-checker.py"

DUMP_DIR="dump"
DUMP_FILE="${DUMP_DIR}/${USERNAME}.txt"

mkdir -p "$DUMP_DIR"
touch "$DUMP_FILE"
> "$DUMP_FILE"

FILES=(
  BinaryToBinCodedDec_GL.v
  BinaryToSevenSegOpt_GL.v
  BinaryToSevenSegUnopt_GL.v
  DisplayOpt_GL.v
  DisplayUnopt_GL.v
  test/BinaryToBinCodedDec_GL-test.v
  test/BinaryToSevenSeg-test-cases.v
  test/BinaryToSevenSegOpt_GL-test.v
  test/BinaryToSevenSegUnopt_GL-test.v
  test/Display-test-cases.v
  test/DisplayOpt_GL-test.v
  test/DisplayUnopt_GL-test.v
)

# rule -> total count across all files
declare -A RULE_COUNTS

for file in "${FILES[@]}"; do
  FULL_PATH="${BASE_PATH}/${file}"

  if [ ! -f "$FULL_PATH" ]; then
    echo "File not found: $FULL_PATH" | tee -a "$DUMP_FILE"
    continue
  fi

  echo "========================================" | tee -a "$DUMP_FILE"
  echo "Running checker on $FULL_PATH" | tee -a "$DUMP_FILE"
  echo "========================================" | tee -a "$DUMP_FILE"

  OUTPUT=$($CHECKER "$FULL_PATH" 2>&1)
  echo "$OUTPUT" | tee -a "$DUMP_FILE"
  echo "" | tee -a "$DUMP_FILE"

  # Prefer the per-file "Warning Summary" counts, e.g.:
  #   Rule 4.7: 3
  # This correctly counts multiple occurrences within a file.
  #
  # If a checker ever prints multiple Rule lines, we sum them all.
  while IFS= read -r line; do
    rule="$(echo "$line" | awk '{print $2}' | tr -d ':')"
    cnt="$(echo "$line"  | awk '{print $3}')"
    if [[ -n "$rule" && "$cnt" =~ ^[0-9]+$ ]]; then
      ((RULE_COUNTS["$rule"] += cnt))
    fi
  done < <(echo "$OUTPUT" | awk '/^Rule[[:space:]]+[0-9]+\.[0-9]+:[[:space:]]+[0-9]+/{print}')

done

echo "========================================" | tee -a "$DUMP_FILE"
echo "Warnings Summary Across All Files" | tee -a "$DUMP_FILE"
echo "========================================" | tee -a "$DUMP_FILE"

if [ ${#RULE_COUNTS[@]} -eq 0 ]; then
  echo "(none)" | tee -a "$DUMP_FILE"
  echo "Total Unique Rules: 0" | tee -a "$DUMP_FILE"
  echo "Total Warnings: 0" | tee -a "$DUMP_FILE"
  echo "========================================" | tee -a "$DUMP_FILE"
  exit 0
fi

# print sorted rules
mapfile -t sorted_rules < <(printf "%s\n" "${!RULE_COUNTS[@]}" | sort -V)

total_warnings=0
for rule in "${sorted_rules[@]}"; do
  count="${RULE_COUNTS[$rule]}"
  echo "$rule: $count" | tee -a "$DUMP_FILE"
  total_warnings=$((total_warnings + count))
done

echo "----------------------------------------" | tee -a "$DUMP_FILE"
echo "Total Unique Rules: ${#RULE_COUNTS[@]}" | tee -a "$DUMP_FILE"
echo "Total Warnings: $total_warnings" | tee -a "$DUMP_FILE"
echo "========================================" | tee -a "$DUMP_FILE"