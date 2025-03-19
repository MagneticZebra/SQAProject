class AccountManager:
    def __init__(self, accounts: dict):
        self.accounts = accounts
    
    def process_transaction(self, transaction: dict) -> bool:
        """Processes transactions by updating accounts accordingly"""
        account_number = transaction["account_number"]
        amount = transaction["amount"]
        transaction_code = transaction["code"]

        # ✅ Debugging output to check account existence
        if account_number not in self.accounts:
            print(f"❌ ERROR: Account {account_number} does not exist.")
            return False

        # ✅ Debugging output to check balance before withdrawal
        print(f"🔹 Processing {transaction_code} for {account_number}: Current Balance: {self.accounts[account_number]['balance']}")

        if transaction_code == "01":  # Withdrawal
            return self.withdraw(account_number, amount)
        elif transaction_code == "02":  # Transfer
            return self.transfer(account_number, transaction["misc"], amount)
        elif transaction_code == "03":  # Paybill
            return self.pay_bill(account_number, transaction["misc"], amount)
        elif transaction_code == "04":  # Deposit
            return self.deposit(account_number, amount)
        elif transaction_code == "05":  # Create Account
            return self.create_account(transaction)
        elif transaction_code == "06":  # Delete Account
            return self.delete_account(account_number)
        elif transaction_code == "07":  # Disable Account
            return self.disable_account(account_number)
        elif transaction_code == "08":  # Change Plan
            return self.change_plan(account_number, transaction["misc"])

        return False


    def withdraw(self, account_number: str, amount: float) -> bool:
        """Withdraws money from an account"""
        if account_number not in self.accounts or self.accounts[account_number]["balance"] < amount:
            return False
        self.accounts[account_number]["balance"] -= amount
        return True

    def transfer(self, from_account: str, to_account: str, amount: float) -> bool:
        """Transfers money between two accounts"""
        if from_account not in self.accounts or to_account not in self.accounts:
            return False
        if self.accounts[from_account]["balance"] < amount:
            return False
        self.accounts[from_account]["balance"] -= amount
        self.accounts[to_account]["balance"] += amount
        return True
    
    def pay_bill(self, account_number: str, company: str, amount: float) -> bool:
        """Pays a bill from the account to an authorized company."""
        if account_number not in self.accounts:
            return False

        if self.accounts[account_number]["balance"] < amount:
            return False  # Not enough balance

        # Ensure the company is one of the allowed billers
        allowed_companies = ["EC", "CQ", "FI"]
        if company not in allowed_companies:
            return False  # Invalid company

        self.accounts[account_number]["balance"] -= amount
        return True

    def deposit(self, account_number: str, amount: float) -> bool:
        """Deposits money into an account"""
        if account_number not in self.accounts:
            return False
        self.accounts[account_number]["balance"] += amount
        return True

    def create_account(self, account_info: dict) -> bool:
        """Creates a new bank account"""
        account_number = account_info["account_number"]
        if account_number in self.accounts:
            return False
        self.accounts[account_number] = account_info
        return True

    def delete_account(self, account_number: str) -> bool:
        """Deletes a bank account"""
        if account_number in self.accounts:
            del self.accounts[account_number]
            return True
        return False

    def disable_account(self, account_number: str) -> bool:
        """Disables a bank account"""
        if account_number in self.accounts:
            self.accounts[account_number]["status"] = "D"
            return True
        return False

    def change_plan(self, account_number: str, new_plan: str) -> bool:
        """Changes the account transaction plan"""
        if account_number in self.accounts:
            self.accounts[account_number]["plan"] = new_plan
            return True
        return False
    



