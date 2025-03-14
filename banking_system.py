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
        """Applies transactions to accounts and confirms updates"""
        for transaction in self.transactions:
            account_number = transaction["account_number"]
            transaction_code = transaction["code"]

            success = self.account_manager.process_transaction(transaction)

            if success:
                print(f"✅ TRANSACTION SUCCESS: {transaction_code} for {account_number}. Updated Balance: {self.accounts[account_number]['balance']}")



    def update_master_file(self) -> None:
        """Writes the updated account list to the new Master Bank Accounts File"""
        print("\n📌 DEBUG: FINAL MASTER ACCOUNT BALANCES BEFORE WRITING:")
        for acc in self.accounts.values():
            print(f"📝 MASTER WRITE: {acc['account_number']} | {acc['name']} | Balance: {acc['balance']} | Transactions: {acc['transaction_count']}")

        self.write_master_file(list(self.accounts.values()), self.new_master_file)


    def update_current_file(self) -> None:
        """Writes the updated account list to the new Current Bank Accounts File"""
        
        # ✅ Print all account balances BEFORE writing
        print("\n📌 DEBUG: FINAL CURRENT ACCOUNT BALANCES BEFORE WRITING:")
        
        for acc_number, acc in self.accounts.items():
            print(f"📝 FINAL WRITE: {acc_number} | {acc['name']} | Balance: {acc['balance']} | Transactions: {acc['transaction_count']}")

        # ✅ Pass the updated list to ensure correct values are written
        self.write_new_current_accounts(self.new_current_file)



    def calculate_transaction_fee(self) -> None:
        """Deducts transaction fees based on transaction count"""
        print("\n📌 DEBUG: APPLYING TRANSACTION FEES")

        for account_number, account in self.accounts.items():
            if account_number == "00000":  # ✅ Skip special "END OF FILE" account
                continue

            fee = 0.05 if account["plan"] == "SP" else 0.10  # ✅ Different fees based on account type
            transaction_count = account.get("transaction_count", 0)
            total_fee = fee * transaction_count  # ✅ Apply fee for each transaction

            if transaction_count > 0:
                print(f"💰 TRANSACTION FEE: Deducting {total_fee:.2f} from {account_number} (Total Transactions: {transaction_count})")

                # ✅ Prevent negative balances
                if account["balance"] - total_fee < 0:
                    print(f"❌ WARNING: Preventing negative balance for account {account_number}.")
                    continue  # ✅ Skip fee deduction if insufficient balance

                account["balance"] -= total_fee  # ✅ Deduct total fee

    
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
                balance_str = line[28:36].strip().replace("_", "")  # ✅ Removes any unwanted underscores
                transaction_count_str = line[37:41].strip()

                # ✅ Ensure account number exists
                if not account_number:
                    print(f"❌ ERROR: Missing account number in line {repr(line)}")
                    continue

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

                # ✅ Store Account
                accounts[account_number] = {
                    "account_number": account_number,  # ✅ Ensure it's included
                    "name": account_holder,
                    "status": status,
                    "balance": balance,
                    "transaction_count": transaction_count,
                    "plan": plan,
                }
        
        print(f"✅ Stored Accounts: {accounts.keys()}")  # ✅ Debugging output
        return accounts


    # def write_new_current_accounts(self, file_path):
    #     """
    #     Writes Current Bank Accounts File with strict format validation.
    #     Raises ValueError for invalid data to enable testing.
    #     """
    #     with open(file_path, 'w') as file:
    #         for acc in self.accounts.values():  # ✅ Use self.accounts directly
    #             # ✅ Ensure each account has 'account_number'
    #             if 'account_number' not in acc:
    #                 print(f"❌ ERROR: Missing 'account_number' field in {acc}")
    #                 continue  # Skip invalid account entry

    #             # Validate account number
    #             if not isinstance(acc['account_number'], str) or not acc['account_number'].isdigit():
    #                 print(f"❌ ERROR: Invalid account number format: {acc['account_number']}")
    #                 continue

    #             if len(acc['account_number']) > 5:
    #                 print(f"❌ ERROR: Account number too long: {acc['account_number']}")
    #                 continue

    #             # Validate name length
    #             if len(acc['name']) > 20:
    #                 print(f"❌ ERROR: Name exceeds 20 characters: {acc['name']}")
    #                 continue

    #             # Validate status
    #             if acc['status'] not in ('A', 'D'):
    #                 print(f"❌ ERROR: Invalid status: {acc['status']}")
    #                 continue

    #             # Validate balance
    #             if not isinstance(acc['balance'], (int, float)):
    #                 print(f"❌ ERROR: Invalid balance type: {type(acc['balance'])}")
    #                 continue
    #             if acc['balance'] > 99999.99 or acc['balance'] < 0:
    #                 print(f"❌ ERROR: Balance out of range: {acc['balance']}")
    #                 continue

    #             # Format fields
    #             acc_num = acc['account_number'].zfill(5)
    #             name = acc['name'].ljust(20)[:20]
    #             balance = f"{acc['balance']:08.2f}"

    #             file.write(f"{acc_num} {name} {acc['status']} {balance}\n")

    #         # Add END_OF_FILE marker
    #         file.write("00000 END_OF_FILE          A 00000.00\n")

    def write_new_current_accounts(self, file_path):
        """Writes the updated Current Bank Accounts File."""
        with open(file_path, 'w') as file:
            for acc in self.accounts.values():
                print(f"📝 WRITING FINAL ACCOUNT: {acc['account_number']} | {acc['name']} | Final Balance: {acc['balance']}")

                acc_num = acc['account_number'].zfill(5)
                name = acc['name'].ljust(20)[:20]
                balance = f"{acc['balance']:08.2f}"

                file.write(f"{acc_num} {name} {acc['status']} {balance}\n")

            file.write("00000 END_OF_FILE          A 00000.00\n")


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

