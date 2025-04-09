#!/bin/bash

# --- CONFIG ---
FRONTEND_SCRIPT="bank-atm.py"
BACKEND_SCRIPT="../main.py"

# --- INPUT ARGS ---
CURRENT_ACCOUNTS="${1:-Current_Bank_Accounts.txt}"
MASTER_ACCOUNTS="${2:-../old_master_accounts.txt}"
SESSION_INPUTS="${3:-daily_script_inputs}"
SESSION_OUTPUTS="${4:-daily_script_outputs}"
MERGED_FILE="${5:-../merged_transactions.txt}"

# --- SETUP ---
mkdir -p "$SESSION_OUTPUTS"
> "$MERGED_FILE"

echo "🔧 Normalizing line endings in session input files..."
for FILE in "$SESSION_INPUTS"/*.txt; do
    sed -i 's/\r$//' "$FILE"
done

echo "🔁 Running frontend sessions..."

for INPUT_FILE in "$SESSION_INPUTS"/*.txt; do
    TEST_NAME=$(basename "$INPUT_FILE" .txt)
    TRANSACTION_FILE="$SESSION_OUTPUTS/${TEST_NAME}.txt"

    echo "▶️ Session: $TEST_NAME"
    python3 "$FRONTEND_SCRIPT" "$CURRENT_ACCOUNTS" "$TRANSACTION_FILE" < "$INPUT_FILE"

    if [[ $? -eq 0 ]]; then
        echo "✅ Output saved to $TRANSACTION_FILE"
        cat "$TRANSACTION_FILE" >> "$MERGED_FILE"
    else
        echo "❌ Error in $TEST_NAME"
    fi

    echo "-------------------------------------------"
done

# --- RUN BACKEND ---
echo "🚀 Running backend with merged transactions..."
python3 "$BACKEND_SCRIPT" "$MASTER_ACCOUNTS" "$MERGED_FILE"

if [[ $? -eq 0 ]]; then
    echo "✅ Backend executed successfully."
else
    echo "❌ Backend failed to run properly."
fi

echo "✅ Daily integration complete!"
