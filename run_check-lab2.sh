#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: ./run_check-lab2.sh <username>"
  exit 1
fi

USERNAME="$1"
# if feed in abc123/ then username is just abc123
USERNAME="${USERNAME%/}"
BASE_PATH="$USERNAME/lab2"
CHECKER="python3 convention-checker.py"

DUMP_DIR="dump"
DUMP_FILE="${DUMP_DIR}/${USERNAME}.txt"

mkdir -p "$DUMP_DIR"
touch "$DUMP_FILE"
> "$DUMP_FILE"

FILES=(
  Adder_16b_RTL.v
  AdderCarrySelect_16b_GL.v
  AdderRippleCarry_8b_GL.v
  AdderRippleCarry_16b_GL.v
  Calculator_GL.v
  FullAdder_GL.v
  Multiplier_1x16b_GL.v
  Multiplier_2x16b_GL.v
  Multiplier_2x16b_RTL.v
  Mux2_1b_GL.v
  Mux2_8b_GL.v
  Mux2_16b_GL.v
  
  test/Adder_16b_RTL-test.v
  test/Adder_16b-test-cases.v
  test/AdderCarrySelect_16b_GL-test.v
  test/AdderRippleCarry_8b_GL-test.v
  test/AdderRippleCarry_16b_GL-test.v
  test/Calculator_GL-test.v
  test/FullAdder_GL-test.v
  test/Multiplier_1x16b_GL-test.v
  test/Multiplier_2x16b_RTL-test.v
  test/Multiplier_2x16b_GL-test.v
  test/Multiplier_2x16b-test-cases.v
  test/Mux2_1b_GL-test.v
  test/Mux2_8b_GL-test.v
  test/Mux2_16b_GL-test.v
)

# rule -> total count across all files
declare -A RULE_COUNTS

for file in "${FILES[@]}"; do
  FULL_PATH="${BASE_PATH}/${file}"

  if [ ! -f "$FULL_PATH" ]; then
    echo "File not found: $FULL_PATH" | tee -a "$DUMP_FILE"
    continue
  fi

  echo "################################################" | tee -a "$DUMP_FILE"
  echo "Running checker on $FULL_PATH" | tee -a "$DUMP_FILE"
  echo "################################################" | tee -a "$DUMP_FILE"

  OUTPUT=$($CHECKER "$FULL_PATH" 2>&1)
  echo "$OUTPUT" | tee -a "$DUMP_FILE"
  echo "" | tee -a "$DUMP_FILE"

  # Extract rules like "Rule 3.2:" and count them
  while IFS= read -r rule; do
    if [ -n "$rule" ]; then
      ((RULE_COUNTS["$rule"]++))
    fi
  done < <(echo "$OUTPUT" | awk '/^Rule[[:space:]]+[0-9]+\.[0-9]+:/{print $2}' | tr -d ':')

done

echo "################################################" | tee -a "$DUMP_FILE"
echo "Warnings Summary Across All Files" | tee -a "$DUMP_FILE"
echo "################################################" | tee -a "$DUMP_FILE"

if [ ${#RULE_COUNTS[@]} -eq 0 ]; then
  echo "(none)" | tee -a "$DUMP_FILE"
  echo "Total Unique Rules: 0" | tee -a "$DUMP_FILE"
  echo "Total Warnings: 0" | tee -a "$DUMP_FILE"
  echo "################################################" | tee -a "$DUMP_FILE"
  exit 0
fi

total_warnings=0
printf "%s\n" "${!RULE_COUNTS[@]}" | sort -V | while IFS= read -r rule; do
  count="${RULE_COUNTS[$rule]}"
  echo "$rule: $count" | tee -a "$DUMP_FILE"
done

for v in "${RULE_COUNTS[@]}"; do
  total_warnings=$((total_warnings + v))
done

echo "################################################" | tee -a "$DUMP_FILE"
echo "Total Unique Rules: ${#RULE_COUNTS[@]}" | tee -a "$DUMP_FILE"
echo "Total Warnings: $total_warnings" | tee -a "$DUMP_FILE"
echo "################################################" | tee -a "$DUMP_FILE"
