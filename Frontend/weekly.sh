#!/bin/bash

# --- CONFIG ---
INPUT_BASE="week_script_inputs"
OUTPUT_DIR="week_script_outputs"
DAILY_SCRIPT="./daily.sh"

# Initial input files (used only on Day 1)
START_CURRENT="Current_Bank_Accounts.txt"
START_MASTER="../old_master_accounts.txt"

# Working copies that will get replaced day to day
WORKING_CURRENT="current_input.txt"
WORKING_MASTER="master_input.txt"

# Reset output and temp files
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

rm -f new_current_accounts.txt new_master_accounts.txt
rm -f "$WORKING_CURRENT" "$WORKING_MASTER"

# Use Day 1 input files to initialize working versions
cp "$START_CURRENT" "$WORKING_CURRENT"
cp "$START_MASTER" "$WORKING_MASTER"

# Run for 7 days
for DAY in {1..7}; do
  echo "📅 Running Day $DAY"

  INPUT_FOLDER="$INPUT_BASE/day$DAY"
  MERGED_FILE="$OUTPUT_DIR/merged_day${DAY}.txt"
  TEMP_OUTPUT_FOLDER="temp_day${DAY}_outputs"

  # Clean and create temp output folder for this day
  rm -rf "$TEMP_OUTPUT_FOLDER"
  mkdir -p "$TEMP_OUTPUT_FOLDER"

  # Run the daily script with inputs for this day
  $DAILY_SCRIPT "$WORKING_CURRENT" "$WORKING_MASTER" "$INPUT_FOLDER" "$TEMP_OUTPUT_FOLDER" "$MERGED_FILE"

  # Merge all session outputs from this day into a single dayN.txt file
  cat "$TEMP_OUTPUT_FOLDER"/*.txt > "$OUTPUT_DIR/day${DAY}.txt"

  # Update input files for the next day
  cp new_current_accounts.txt "$WORKING_CURRENT"
  cp new_master_accounts.txt "$WORKING_MASTER"

  echo "✅ Day $DAY complete"
  echo ""
done

echo "🎉 Weekly script complete. All outputs saved in $OUTPUT_DIR/"
