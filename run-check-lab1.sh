#!/bin/bash

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

declare -A SEEN_RULES

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

  while IFS= read -r rule; do
    if [ -n "$rule" ]; then
      SEEN_RULES["$rule"]=1
    fi
  done < <(echo "$OUTPUT" | awk '/^Rule[[:space:]]+[0-9]+\.[0-9]+:/{print $2}' | tr -d ':')

done

echo "========================================" | tee -a "$DUMP_FILE"
echo "Unique Warnings Across All Files" | tee -a "$DUMP_FILE"
echo "========================================" | tee -a "$DUMP_FILE"

if [ ${#SEEN_RULES[@]} -eq 0 ]; then
  echo "(none)" | tee -a "$DUMP_FILE"
  echo "Total Unique Rules: 0" | tee -a "$DUMP_FILE"
  echo "========================================" | tee -a "$DUMP_FILE"
  exit 0
fi

printf "%s\n" "${!SEEN_RULES[@]}" | sort -V | tee -a "$DUMP_FILE"
echo "----------------------------------------" | tee -a "$DUMP_FILE"
echo "Total Unique Warnings: ${#SEEN_RULES[@]}" | tee -a "$DUMP_FILE"
echo "========================================" | tee -a "$DUMP_FILE"