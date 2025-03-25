"""
Banking System - Backend
----------------------------------------
Description:
    This backend is responsible for updating and maintaining 
    the Master Bank Accounts File based on transactions recorded by the 
    front-end system. It processes a merged set of daily bank transactions 
    and applies them to the previous day's master accounts file, generating 
    an updated master accounts file and a new current accounts file.

Input Files:
    - Old Master Bank Accounts File (Contains all bank accounts from the previous day)
    - Merged Bank Account Transaction File (Concatenation of transaction files from multiple front-end sessions)

Output Files:
    - New Master Bank Accounts File (Updated list of bank accounts after processing transactions)
    - New Current Bank Accounts File (Contains only active bank accounts)
"""


from banking_system import BankingSystem

# File paths
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
