class AccountManager:
    def __init__(self, accounts: dict):
        self.accounts = accounts
    

    def process_transaction(self, transaction: dict) -> bool:
        """Processes transactions and updates accounts accordingly"""
        account_number = transaction["account_number"]
        amount = transaction["amount"]
        transaction_code = transaction["code"]

        if account_number not in self.accounts:
            print(f"❌ ERROR: Account {account_number} does not exist.")
            return False

        success = False
        if transaction_code == "01":  # Withdrawal
            success = self.withdraw(account_number, amount)
        elif transaction_code == "02":  # Transfer
            success = self.transfer(account_number, transaction["misc"], amount)
        elif transaction_code == "03":  # Paybill
            success = self.pay_bill(account_number, transaction["misc"], amount)
        elif transaction_code == "04":  # Deposit
            success = self.deposit(account_number, amount)
        elif transaction_code == "05":  # Create Account
            success = self.create_account(transaction)
        elif transaction_code == "06":  # Delete Account
            success = self.delete_account(account_number)
        elif transaction_code == "07":  # Disable Account
            success = self.disable_account(account_number)
        elif transaction_code == "08":  # Change Plan
            success = self.change_plan(account_number, transaction["misc"])

        # ✅ Ensure transaction count increments on success
        if success:
            self.accounts[account_number]["transaction_count"] += 1  # ✅ Increment transaction count
            print(f"🔄 UPDATED TRANSACTION COUNT: {self.accounts[account_number]['transaction_count']} for {account_number}")

        return success



    def withdraw(self, account_number: str, amount: float) -> bool:
        """Withdraws money from an account"""
        if account_number not in self.accounts or self.accounts[account_number]["balance"] < amount:
            print(f"❌ ERROR: Insufficient Funds for Withdrawal | Account: {account_number} | Balance: {self.accounts[account_number]['balance']} | Requested: {amount}")
            return False
        
        print(f"💸 WITHDRAW: {amount} from {account_number} | Before: {self.accounts[account_number]['balance']}")
        self.accounts[account_number]["balance"] -= amount
        print(f"✅ NEW BALANCE: {self.accounts[account_number]['balance']}")

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
            print(f"❌ ERROR: Insufficient funds for Pay Bill | Account: {account_number} | Balance: {self.accounts[account_number]['balance']} | Bill: {amount}")
            return False

        # Ensure the company is one of the allowed billers
        allowed_companies = ["EC", "CQ", "FI"]
        if company not in allowed_companies:
            print(f"❌ ERROR: Invalid Payee '{company}' for {account_number}")
            return False

        print(f"📝 PAY BILL: {amount} from {account_number} | Before: {self.accounts[account_number]['balance']}")
        self.accounts[account_number]["balance"] -= amount
        print(f"✅ NEW BALANCE: {self.accounts[account_number]['balance']}")

        return True


    def deposit(self, account_number: str, amount: float) -> bool:
        """Deposits money into an account"""
        if account_number not in self.accounts:
            return False

        print(f"💰 DEPOSIT: {amount} to {account_number} | Before: {self.accounts[account_number]['balance']}")
        self.accounts[account_number]["balance"] += amount
        print(f"✅ NEW BALANCE: {self.accounts[account_number]['balance']}")

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
    



