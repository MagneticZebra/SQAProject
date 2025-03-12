import os
from typing import List, Dict
from account_manager import AccountManager
from error_logger import ErrorLogger


class BankingSystem:
    def __init__(self, old_master_file: str, merged_transaction_file: str):
        self.old_master_file = old_master_file
        self.merged_transaction_file = merged_transaction_file
        self.new_master_file = "new_master_accounts.txt"
        self.new_current_file = "new_current_accounts.txt"
        self.accounts = {}  # Stores bank accounts as a dictionary {account_number: {details}}
        self.transactions = []

        self.error_logger = ErrorLogger()

        self.read_input_files()

        self.account_manager = AccountManager(self.accounts)

    def read_input_files(self) -> None:
        """Reads the Master Bank Accounts and Transaction Files"""
        self.accounts = self.read_old_bank_accounts(self.old_master_file)
        self.transactions = self.read_transactions(self.merged_transaction_file)


    def apply_transactions(self) -> None:
        """Applies each transaction to the respective account"""
        for transaction in self.transactions:
            success = self.account_manager.process_transaction(transaction)
            
            # ✅ Prevent accounts from going negative
            account_number = transaction["account_number"]
            if self.accounts[account_number]["balance"] < 0:
                print(f"❌ ERROR: Account {account_number} has gone negative! Rolling back.")
                self.accounts[account_number]["balance"] = 0.0  # ✅ Fix balance


    def update_master_file(self) -> None:
        """Writes the updated account list to the new Master Bank Accounts File"""
        self.write_master_file(list(self.accounts.values()), self.new_master_file)

    def update_current_file(self) -> None:
        """Writes the updated account list to the new Current Bank Accounts File"""
        self.write_new_current_accounts(list(self.accounts.values()), self.new_current_file)


    def calculate_transaction_fee(self) -> None:
        """Deducts transaction fees based on the account type"""
        for account_number, account in self.accounts.items():
            if account_number == "00000":  # ✅ Skip the special "END OF FILE" account
                continue

            fee = 0.05 if account["plan"] == "SP" else 0.10

            # ✅ Prevent negative balances
            if account["balance"] - fee < 0:
                print(f"❌ WARNING: Preventing negative balance for account {account_number}.")
                continue  # ✅ Skip fee deduction

            account["balance"] -= fee


    def read_old_bank_accounts(self, file_path: str) -> Dict[str, Dict]:
        """Reads the old Master Bank Accounts file and returns a dictionary of accounts"""
        accounts = {}
        with open(file_path, "r") as file:
            for line in file:
                print(f"Reading Line: {repr(line)}")  # Debugging output
                
                account_number = line[:5].strip()
                account_holder = line[6:26].strip()

                if "END OF FILE" in account_holder:  # ✅ Skip EOF entry
                    print("🔹 Skipping END OF FILE entry.")
                    continue

                status = line[27].strip()
                balance_str = line[28:36].strip()
                transaction_count_str = line[37:41].strip()

                print(f"Extracted Account: {account_number}, Holder: {account_holder}")  # ✅ Debugging Output

                # ✅ Ensure balance is valid
                try:
                    balance = float(balance_str) if balance_str else 0.0
                except ValueError:
                    print(f"ERROR: Could not convert balance: '{balance_str}' in line: {repr(line)}")
                    balance = 0.0  # Default to 0.0 if an error occurs

                # ✅ Ensure transaction count is valid
                transaction_count = int(transaction_count_str) if transaction_count_str.isdigit() else 0

                # ✅ Add default plan
                plan = "SP"  # Default to student plan unless specified later

                accounts[account_number] = {
                    "name": account_holder,
                    "status": status,
                    "balance": balance,
                    "transaction_count": transaction_count,
                    "plan": plan,
                }
        
        print(f"✅ Stored Accounts: {accounts.keys()}")  # ✅ Debugging output
        return accounts



    def write_new_current_accounts(self, accounts: Dict[str, Dict], file_path: str) -> None:
        """Writes the new Current Bank Accounts file"""
        with open(file_path, "w") as file:
            for account_number, acc in self.accounts.items():  # ✅ Loop through dict.items()
                file.write(f"{account_number:>5}_{acc['name']:<20}_{acc['status']}_{acc['balance']:>8.2f}\n")
            file.write("00000_END_OF_FILE______________________\n")  # ✅ Correct End-of-File format


    def write_master_file(self, accounts: List[Dict], file_path: str) -> None:
        """Writes the new Master Bank Accounts file"""
        with open(file_path, "w") as file:
            for account_number, acc in self.accounts.items():  # Loop through dict.items()
                file.write(f"{account_number:>5}_{acc['name']:<20}_{acc['status']}_{acc['balance']:>8.2f}_{acc['transaction_count']:>4}\n")


    def read_transactions(self, file_path: str) -> List[Dict]:
        """Reads the Merged Transaction File"""
        transactions = []
        with open(file_path, "r") as file:
            for line in file:
                print(f"Reading Transaction Line: {repr(line)}")  # Debugging Output
                if line.startswith("00"):  # End of session
                    break
                transaction = {
                    "code": line[:2].strip(),
                    "name": line[3:23].strip(),
                    "account_number": line[24:29].strip(),
                    "amount": float(line[30:38].strip()),
                    "misc": line[39:].strip(),
                }
                print(f"Extracted Transaction: {transaction}")  # Debugging Output
                transactions.append(transaction)
        return transactions

