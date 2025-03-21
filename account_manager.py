from error_logger import ErrorLogger

class AccountManager:
    def __init__(self, accounts: dict):
        self.accounts = accounts
        self.error_logger = ErrorLogger()
    
    # Processes a transaction and updates the account balances
    def process_transaction(self, transaction: dict) -> bool:
        account_number = transaction["account_number"]
        amount = transaction["amount"]
        transaction_code = transaction["code"]

        if account_number not in self.accounts:
            self.error_logger.log_constraint_error("Invalid Account", f"Account {account_number} does not exist.")
            return False

        success = False
        if transaction_code == "01":  # withdrawalal
            success = self.withdrawal(account_number, amount)
        elif transaction_code == "03":  # Paybill
            success = self.paybill(account_number, transaction["misc"], amount)
        elif transaction_code == "04":  # Deposit
            success = self.deposit(account_number, amount)
        elif transaction_code == "05":  # Create Account
            success = self.create_account(transaction)
        elif transaction_code == "06":  # Delete Account
            success = self.delete_account(account_number)
        elif transaction_code == "07":  # Disable Account
            success = self.disable_account(account_number)
        elif transaction_code == "08":  # Change Plan
            success = self.changeplan(account_number, transaction["misc"])

        # Ensure transaction count increments on success
        if success and account_number in self.accounts:
            self.accounts[account_number]["total_transactions"] += 1  # Increment transaction count

        return success

    # withdrawals money from an account
    def withdrawal(self, account_number: str, amount: float) -> bool:
        if account_number not in self.accounts or self.accounts[account_number]["balance"] < amount:
            self.error_logger.log_constraint_error("Insufficient Funds", 
                f"Account {account_number} has {self.accounts[account_number]['balance']}, cannot withdraw {amount}.")
            return False
        
        self.accounts[account_number]["balance"] -= amount

        return True
    
    # Pays a bill from the account to an authorized company
    def paybill(self, account_number: str, company: str, amount: float) -> bool:
        if account_number not in self.accounts:
            return False

        if self.accounts[account_number]["balance"] < amount:
            self.error_logger.log_constraint_error("Insufficient Funds", 
                f"Account {account_number} has {self.accounts[account_number]['balance']}, cannot pay bill {amount}.")
            return False

        # Ensure the company is one of the allowed billers
        allowed_companies = ["EC", "CQ", "FI"]
        if company not in allowed_companies:
            self.error_logger.log_constraint_error("Invalid Payee", 
                f"Account {account_number} tried to pay an invalid company: {company}.")
            return False

        self.accounts[account_number]["balance"] -= amount

        return True

    # Deposits money into an account
    def deposit(self, account_number: str, amount: float) -> bool:
        if account_number not in self.accounts:
            return False

        self.accounts[account_number]["balance"] += amount
        return True

    # Creates a new bank account
    def create_account(self, transaction: dict) -> bool:
        # Find the highest current account number and increment it
        max_account_number = max(int(num) for num in self.accounts.keys()) if self.accounts else 10000
        new_account_number = str(max_account_number + 1).zfill(5)  # Ensure 5-digit format
        
        # Create the new account
        self.accounts[new_account_number] = {
            "account_number": new_account_number,
            "name": transaction["name"],
            "status": "A",  # Active status
            "balance": transaction["amount"],  # Initial deposit amount
            "total_transactions": 0,
            "plan": "NS",  # Default to Non-Student plan
        }

        print(f"✅ New account created: {new_account_number} for {transaction['name']}.")
        return True

    # Deletes a bank account
    def delete_account(self, account_number: str) -> bool:
        if account_number not in self.accounts:
            self.error_logger.log_constraint_error("Cannot delete account", 
                f"Account {account_number} does not exist.")
            return False

        del self.accounts[account_number]
        print(f"✅ Account {account_number} deleted successfully.")

        return True


    # Disables a bank account
    def disable_account(self, account_number: str) -> bool:
        if account_number in self.accounts:
            self.accounts[account_number]["status"] = "D"  # Change status to Disabled
            print(f"✅ Account {account_number} has been disabled.")
            return True
        self.error_logger.log_constraint_error("Cannot disable account", 
                f"Account {account_number} does not exist.")
        return False

    # Changes the account transaction plan
    def changeplan(self, account_number: str, new_plan: str) -> bool:
        if self.accounts[account_number]["plan"] == "NS" and new_plan == "SP":
            self.accounts[account_number]["plan"] = "SP"
            return True
        else:
            self.error_logger.log_constraint_error("Invalid Plan Change", 
                f"Account {account_number} cannot change from {self.accounts[account_number]['plan']} to {new_plan}.")
            return False




