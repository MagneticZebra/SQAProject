#!/bin/bash

# --- CONFIG ---
FRONTEND_SCRIPT="bank-atm.py"
BACKEND_SCRIPT="../main.py"

CURRENT_ACCOUNTS="Current_Bank_Accounts.txt"
MASTER_ACCOUNTS="../old_master_accounts.txt"
MERGED_FILE="../merged_transactions.txt"

SESSION_INPUTS="session_inputs"
SESSION_OUTPUTS="session_outputs"

# --- SETUP ---
mkdir -p "$SESSION_OUTPUTS"
> "$MERGED_FILE"
> "$ALL_SESSIONS_FILE"

echo "🔧 Normalizing line endings in session input files..."
for FILE in "$SESSION_INPUTS"/*.txt; do
    sed -i 's/\r$//' "$FILE"
done

echo "🔁 Running frontend sessions..."

# --- FRONT END PASSES ---
for INPUT_FILE in "$SESSION_INPUTS"/*.txt; do
    TEST_NAME=$(basename "$INPUT_FILE" .txt)
    TRANSACTION_FILE="$SESSION_OUTPUTS/${TEST_NAME}.txt"

    echo "▶️ Session: $TEST_NAME"

    # Run Front End and save the transaction output as a .txt file in session_outputs
    python3 "$FRONTEND_SCRIPT" "$CURRENT_ACCOUNTS" "$TRANSACTION_FILE" < "$INPUT_FILE"

    if [[ $? -eq 0 ]]; then
        echo "✅ Output saved to $TRANSACTION_FILE"
        cat "$TRANSACTION_FILE" >> "$MERGED_FILE"
    else
        echo "❌ Error in $TEST_NAME"
    fi

    echo "-------------------------------------------"
done

# End marker for merged_transactions only
echo "00                      00000 00000.00 00" >> "$MERGED_FILE"

echo "📦 Merged transactions with end marker saved to: $MERGED_FILE"

# --- RUN BACKEND ---
echo "🚀 Running backend with merged transactions..."
python3 "$BACKEND_SCRIPT" "$MASTER_ACCOUNTS" "$MERGED_FILE"

if [[ $? -eq 0 ]]; then
    echo "✅ Backend executed successfully."
else
    echo "❌ Backend failed to run properly."
fi

echo "✅ Daily integration complete!"
