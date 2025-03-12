from banking_system import BankingSystem

# File paths (Make sure these files exist in your project folder)
old_master_file = "old_master_accounts.txt"
merged_transaction_file = "merged_transactions.txt"

# Initialize Banking System
banking_system = BankingSystem(old_master_file, merged_transaction_file)

# Step 1: Read Input Files
banking_system.read_input_files()

# Step 2: Apply Transactions
banking_system.apply_transactions()

# Step 3: Apply Transaction Fees
banking_system.calculate_transaction_fee()

# Step 4: Update Master & Current Account Files
banking_system.update_master_file()
banking_system.update_current_file()

print("Banking system executed successfully!")
