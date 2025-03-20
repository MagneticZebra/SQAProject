from typing import List, Dict
from account_manager import AccountManager
from error_logger import ErrorLogger

class BankingSystem:
    def __init__(self, old_master_file: str, merged_transaction_file: str):
        self.old_master_file = old_master_file
        self.merged_transaction_file = merged_transaction_file
        self.new_master_file = "new_master_accounts.txt"
        self.new_current_file = "new_current_accounts.txt"
        self.accounts = {}  # Stores bank accounts as a dictionary
        self.transactions = []

        self.error_logger = ErrorLogger()

        self.read_input_files()

        self.account_manager = AccountManager(self.accounts)

    # Reads the Master Bank Accounts and Transaction Files
    def read_input_files(self) -> None:
        self.accounts = self.read_old_bank_accounts(self.old_master_file)
        self.transactions = self.read_transactions(self.merged_transaction_file)

    # Applies transactions to accounts and confirms updates
    def apply_transactions(self) -> None:
        for transaction in self.transactions:
            if transaction["code"] not in ["01", "03", "04", "05", "06", "07", "08"]:
                self.error_logger.log_fatal_error("Invalid Transaction Code", 
                    f"Unknown transaction code {transaction['code']} in merged transaction file.")
                exit(1)  # Stop execution due to fatal error

            self.account_manager.process_transaction(transaction)
            if transaction["code"] == "05":  # Create account
                success = self.account_manager.create_account(transaction)
                if success:
                    # Ensure the new account is reflected in self.accounts
                    self.accounts = self.account_manager.accounts
            elif transaction["code"] == "06": # delete account
                success = self.account_manager.delete_account(transaction["account_number"])
                if success:
                    # Ensure the deleted account is reflected in self.accounts
                    self.accounts = self.account_manager.accounts
            elif transaction["code"] == "07": # disable account
                success = self.account_manager.disable_account(transaction["account_number"])
                if success:
                    # Ensure the disabled account is reflected in self.accounts
                    self.accounts = self.account_manager.accounts
            elif transaction["code"] == "08": # change plan
                success = self.account_manager.changeplan(transaction["account_number"], transaction["misc"])
                if success:
                    # Ensure the plan change is reflected in self.accounts
                    self.accounts = self.account_manager.accounts
            self.accounts = self.account_manager.accounts

    # Writes the updated account list to the new Master Bank Accounts File
    def update_master_file(self) -> None:
        for acc in self.account_manager.accounts.values():
            print(f"📝 MASTER WRITE: {acc['account_number']} | {acc['name']} | Balance: {acc['balance']} | Transactions: {acc['transaction_count']}")

        self.write_master_file(list(self.account_manager.accounts.values()), self.new_master_file)

    # Writes the updated account list to the new Current Bank Accounts File
    def update_current_file(self) -> None:
        self.write_new_current_accounts(self.new_current_file)


    # Deducts transaction fees based on transaction count
    def calculate_transaction_fee(self) -> None:
        print("\n📌 DEBUG: APPLYING TRANSACTION FEES")

        for account_number, account in self.accounts.items():
            if account_number == "00000":  # Skip special "END OF FILE" account
                continue

            fee = 0.05 if account["plan"] == "SP" else 0.10  # Different fees based on account type
            transaction_count = account.get("transaction_count", 0)
            total_fee = fee * transaction_count  # Apply fee for each transaction

            if transaction_count > 0:
                #print(f"💰 TRANSACTION FEE: Deducting {total_fee:.2f} from {account_number} (Total Transactions: {transaction_count})")

                # ✅ Prevent negative balances
                if account["balance"] - total_fee < 0:
                    print(f"❌ WARNING: Preventing negative balance for account {account_number}.")
                    continue  # Skip fee deduction if insufficient balance

                account["balance"] -= total_fee  # Deduct total fee

    # Reads the old Master Bank Accounts file and returns a dictionary of accounts
    def read_old_bank_accounts(self, file_path: str) -> Dict[str, Dict]:
        accounts = {}
        with open(file_path, "r") as file:
            for line in file:
                account_number = line[:5].strip()
                account_holder = line[6:26].strip("_")

                # Skip EOF entry if it exists
                if "END_OF_FILE" in account_holder:
                    continue

                status = line[27].strip()
                balance_str = line[28:36].strip().replace("_", "")
                transaction_count_str = line[37:41].strip()

                try:
                    balance = float(balance_str) if balance_str else 0.0
                except ValueError:
                    balance = 0.0

                transaction_count = int(transaction_count_str) if transaction_count_str.isdigit() else 0

                accounts[account_number] = {
                    "account_number": account_number,
                    "name": account_holder,
                    "status": status,
                    "balance": balance,
                    "transaction_count": transaction_count,
                    "plan": "SP",
                }
        return accounts

    # Writes the updated Current Bank Accounts file
    def write_new_current_accounts(self, file_path):
        with open(file_path, 'w') as file:
            for acc in sorted(self.accounts.values(), key=lambda x: int(x["account_number"])):
                acc_num = acc['account_number'].zfill(5)
                name = acc['name'].ljust(20, '_')[:20]
                balance = f"{acc['balance']:08.2f}"

                file.write(f"{acc_num}_{name}_{acc['status']}_{balance}\n")

            # Ensure only one EOF entry exists
            if self.accounts:
                last_account_number = max(int(acc["account_number"]) for acc in self.accounts.values())
            else:
                last_account_number = 10000  # Default if no accounts exist

            eof_account_number = str(last_account_number + 1).zfill(5)
            file.write(f"{eof_account_number}_END_OF_FILE__________A_00000.00\n")


    # Writes the updated Master Bank Accounts file
    def write_master_file(self, accounts: List[Dict], file_path: str) -> None:
        with open(file_path, "w") as file:
            # Write all active accounts
            for acc in sorted(self.accounts.values(), key=lambda x: int(x["account_number"])):
                file.write(f"{acc['account_number']:>5}_{acc['name'].ljust(20, '_')}_{acc['status']}_{acc['balance']:08.2f}_{str(acc['transaction_count']).zfill(4)}\n")

            # Ensure only one EOF entry exists
            if self.accounts:  # Ensure there are accounts left
                last_account_number = max(int(acc["account_number"]) for acc in self.accounts.values())
            else:
                last_account_number = 10000  # Default if no accounts exist

            eof_account_number = str(last_account_number + 1).zfill(5)
            file.write(f"{eof_account_number}_END_OF_FILE__________A_00000.00_0000\n")

    # Reads the merged transaction file
    def read_transactions(self, file_path: str) -> List[Dict]:
        transactions = []
        with open(file_path, "r") as file:
            for line in file:
                if line.startswith("00"):  # End of session
                    break
                transaction = {
                    "code": line[:2].strip(),
                    "name": line[3:23].strip("_"),
                    "account_number": line[24:29].strip(),
                    "amount": float(line[30:38].strip()),
                    "misc": line[39:].strip(),
                }
                transactions.append(transaction)
       
        return transactions

