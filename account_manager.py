class AccountManager:
    def __init__(self, accounts: dict):
        self.accounts = accounts
    
    # Processes a transaction and updates the account balances
    def process_transaction(self, transaction: dict) -> bool:
        account_number = transaction["account_number"]
        amount = transaction["amount"]
        transaction_code = transaction["code"]

        if account_number not in self.accounts:
            print(f"❌ ERROR: Account {account_number} does not exist.")
            return False

        success = False
        if transaction_code == "01":  # withdrawalal
            success = self.withdrawal(account_number, amount)
        elif transaction_code == "02":  # Transfer
            success = self.transfer(account_number, transaction["misc"], amount)
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
        if success:
            self.accounts[account_number]["transaction_count"] += 1  # Increment transaction count
            #print(f"🔄 UPDATED TRANSACTION COUNT: {self.accounts[account_number]['transaction_count']} for {account_number}")

        return success

    # withdrawals money from an account
    def withdrawal(self, account_number: str, amount: float) -> bool:
        if account_number not in self.accounts or self.accounts[account_number]["balance"] < amount:
            print(f"❌ ERROR: Insufficient Funds for withdrawal | Account: {account_number} | Balance: {self.accounts[account_number]['balance']} | Requested: {amount}")
            return False
        
        #print(f"💸 withdrawal: {amount} from {account_number} | Before: {self.accounts[account_number]['balance']}")
        self.accounts[account_number]["balance"] -= amount
        # print(f"✅ NEW BALANCE after {amount} for {account_number}: {self.accounts[account_number]['balance']}")

        return True

    # Transfers money between two accounts
    def transfer(self, from_account: str, to_account: str, amount: float) -> bool:
        if from_account not in self.accounts or to_account not in self.accounts:
            return False
        if self.accounts[from_account]["balance"] < amount:
            return False
        self.accounts[from_account]["balance"] -= amount
        self.accounts[to_account]["balance"] += amount
        return True
    
    # Pays a bill from the account to an authorized company
    def paybill(self, account_number: str, company: str, amount: float) -> bool:
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

        #print(f"📝 PAY BILL: {amount} from {account_number} | Before: {self.accounts[account_number]['balance']}")
        self.accounts[account_number]["balance"] -= amount
        #print(f"NEW BALANCE after {amount} for {account_number}: {self.accounts[account_number]['balance']}")

        return True

    # Deposits money into an account
    def deposit(self, account_number: str, amount: float) -> bool:
        if account_number not in self.accounts:
            return False

        #print(f"💰 DEPOSIT: {amount} to {account_number} | Before: {self.accounts[account_number]['balance']}")
        self.accounts[account_number]["balance"] += amount
        #print(f"✅ NEW BALANCE after {amount} for {account_number}: {self.accounts[account_number]['balance']}")

        return True

    # Creates a new bank account
    def create_account(self, account_info: dict) -> bool:
        
        account_number = account_info["account_number"]
        if account_number in self.accounts:
            return False
        self.accounts[account_number] = account_info
        return True

    # Deletes a bank account
    def delete_account(self, account_number: str) -> bool:
        """Deletes a bank account"""
        if account_number in self.accounts:
            del self.accounts[account_number]
            return True
        return False

    # Disables a bank account
    def disable_account(self, account_number: str) -> bool:
        """Disables a bank account"""
        if account_number in self.accounts:
            self.accounts[account_number]["status"] = "D"
            return True
        return False

    # Changes the account transaction plan
    def changeplan(self, account_number: str, new_plan: str) -> bool:
        if account_number in self.accounts:
            self.accounts[account_number]["plan"] = new_plan
            return True
        return False
    



