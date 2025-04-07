from models.transaction_logger import TransactionLogger
from models.limit_manager import LimitManager
import re
from services.error_logger import ErrorLogger, LogLevel

class Transaction:
    is_logged_in = False # flag to check if a user is logged in
    current_user = None  # stores the logged-in user's name
    input_file = None # Stores the current accounts file dynamically
    output_file = None # stores bank account transaction file
    limit_manager = LimitManager(500.0, 1000.0, 2000.0, 99999.99)
    
    #-------------------------------------------- Standard Transactions -----------------------------------------------------
    @staticmethod
    def login(input_file, output_file):
        if Transaction.is_logged_in:  # Check if someone is already logged in
            print("Error: A user is already logged in!")
            return None, None  # Prevent login attempt

        logged_in = False
        account_name = None

        valid_names, _, _, _ = Transaction.read_current_bank_accounts(input_file)
        error_logger = ErrorLogger()

        while not logged_in:
            print("Enter session type:")
            account_type = input().strip().lower()
            
            if account_type not in ["standard", "admin"]:
                print("session terminated")
                continue  

            if account_type == "standard":
                print("Enter account holder's name:")
                account_name = input().strip().lower()

                # ------ Name validator ------
                if account_name not in valid_names:
                    error = error_logger.invalid_account_name(account_name, LogLevel.ERROR)      
                    print(error)
                    
                    # Cancel transaction
                    return "Error", None

            logged_in = True
            Transaction.limit_manager.reset_limits()
            Transaction.is_logged_in = True  # Mark user as logged in
            Transaction.current_user = account_name
            Transaction.input_file = input_file
            Transaction.output_file = output_file

        return account_type, account_name

    def logout(self):
        if not Transaction.is_logged_in:  # Prevent logout if no one is logged in
            print("Error: No user is currently logged in!")
            return

        print(f"session terminated")
        Transaction.limit_manager.reset_limits() # Reset session limits
        Transaction.is_logged_in = False  # Reset login status
        Transaction.current_user = None   # Clear current user
        log_transaction = TransactionLogger(None, None, Transaction.output_file)
        log_transaction.write_end_of_session()  # Write end-of-session transaction

    @staticmethod
    def get_account_plan(account_number):
        try:
            with open(Transaction.input_file, "r") as file:
                for line in file:
                    if line.startswith(account_number):
                        # Assume fixed format: last two characters are the plan
                        plan = line[-2:].strip()
                        if plan in ["SP", "NP"]:
                            return plan
        except FileNotFoundError:
            print("Error: Current bank accounts file not found.")
        
        return "NP"  # Default to NP if not found or invalid

    # Withdraws money from a bank account 
    def withdrawal(self, account_type):
        valid_names, _, account_name_map, _ = Transaction.read_current_bank_accounts(Transaction.input_file)
        error_logger = ErrorLogger()    

        if account_type == "admin":
            print("Enter the account holder's name:")
            name = input().strip().lower()  # Get account holder's name
            
            # ------ Name validator ------
            if name not in valid_names:
                error = error_logger.invalid_account_name(name, LogLevel.ERROR)      
                print(error)
                return "Error", None
        else:
            name = Transaction.current_user

        print("Enter the account number:")
        account_number = input()  # Get account number

        if not Transaction.is_valid_number_format(account_number):
            error = error_logger.invalid_account_number_format(account_number, LogLevel.ERROR)
            print(error)
            return
        
        # ------ Validate Account Number Matches Name ------
        if account_number not in account_name_map or account_name_map[account_number] != name:
            error = error_logger.account_number_doesnt_match(name, account_number, LogLevel.ERROR)
            print(error)
            return
        
        print("Enter the amount to withdraw:")
        withdrawal_amount = input()  # Get amount to withdraw

        if not Transaction.is_valid_amount_format(str(withdrawal_amount)):
            error = error_logger.invalid_amount_format(withdrawal_amount, LogLevel.ERROR)
            print(error)
            return
        else: 
            withdrawal_amount = float(withdrawal_amount)

        if not Transaction.limit_manager.check_withdrawal_limit(withdrawal_amount) and account_type == "standard":
            error = error_logger.withdraw_error(withdrawal_amount, name, account_number)
            print(error)
            return
        
        # Cannot withdraw a negative amount
        if not Transaction.limit_manager.non_negative_amount(withdrawal_amount):
            print("Error: Withdrawal amount must be non-negative")
            return
        
        # Check if account is active
        if not Transaction.is_account_active(account_number):
            error = error_logger.disabled_or_deleted_account()
            print(error)
            return

        # Log transaction with the given details
        if account_type == "admin":
            log_transaction = TransactionLogger(name, withdrawal_amount, Transaction.output_file)
            log_transaction.log_transaction("01", name, account_number, withdrawal_amount, Transaction.get_account_plan(account_number))
        else:
            log_transaction = TransactionLogger(Transaction.current_user, withdrawal_amount, Transaction.output_file)
            log_transaction.log_transaction("01", Transaction.current_user, account_number, withdrawal_amount, Transaction.get_account_plan(account_number))
            Transaction.limit_manager.add_withdrawal(withdrawal_amount)

    # Deposits money into a bank account
    def deposit(self, account_type):
        valid_names, _, account_name_map, _ = Transaction.read_current_bank_accounts(Transaction.input_file)
        error_logger = ErrorLogger()

        if account_type == "admin":
            print("Enter the account holder's name:")
            name = input().strip().lower()  # Get account holder's name
            
            # ------ Name validator ------
            if name not in valid_names:
                error = error_logger.invalid_account_name(name, LogLevel.ERROR)
                print(error)
                return "Error", None
        else:
            name = Transaction.current_user

        print("Enter the account number:")
        account_number = input()  # Get account number

        if not Transaction.is_valid_number_format(account_number):
            error = error_logger.invalid_account_number_format(account_number, LogLevel.ERROR)
            print(error)
            return
        
        # ------ Validate Account Number Matches Name ------
        if account_number not in account_name_map or account_name_map[account_number] != name:
            error = error_logger.account_number_doesnt_match(name, account_number, LogLevel.ERROR)
            print(error)
            return
        
        print("Enter the amount to deposit:")
        to_deposit = input()  # Get amount to deposit

        if not Transaction.is_valid_amount_format(str(to_deposit)):
            error = error_logger.invalid_amount_format(to_deposit, LogLevel.ERROR)
            print(error)
            return
        else: 
            to_deposit = float(to_deposit)

        # Check if account is active
        if not Transaction.is_account_active(account_number):
            error = error_logger.disabled_or_deleted_account()
            print(error)
            return
        
        # Log transaction with the given details
        if account_type == "admin":
            log_transaction = TransactionLogger(name, to_deposit, Transaction.output_file)
            log_transaction.log_transaction("04", name, account_number, to_deposit, Transaction.get_account_plan(account_number))
        else:
            log_transaction = TransactionLogger(Transaction.current_user, to_deposit, Transaction.output_file)
            log_transaction.log_transaction("04", Transaction.current_user, account_number, to_deposit, Transaction.get_account_plan(account_number))


    # Transfers money between two accounts
    def transfer(self, account_type):
        valid_names, valid_accounts, account_name_map, _ = Transaction.read_current_bank_accounts(Transaction.input_file)
        error_logger = ErrorLogger()

        if account_type == "admin":
            print("Enter the account holder's name:")
            name = input().strip().lower()  # Get account holder's name
            
            # ------ Name validator ------
            if name not in valid_names:
                error = error_logger.invalid_account_name(name, LogLevel.ERROR)
                print(error)
                return "Error", None
        else:
            name = Transaction.current_user

        print("Enter the account number that money will be transferred from:")
        account_number_from = input()  # Get account number that money will be transferred from

        # ------ Validate Account Number Follows Formatting Rules ------
        if not Transaction.is_valid_number_format(account_number_from):
            error = error_logger.invalid_account_number_format(account_number_from, LogLevel.ERROR)
            print(error)
            return
        
        # ------ Validate Account Number Matches Name ------
        if account_number_from not in account_name_map or account_name_map[account_number_from] != name:
            error = error_logger.account_number_doesnt_match(name, account_number_from, LogLevel.ERROR)
            print(error)
            return
        
        # Check if account is active
        if not Transaction.is_account_active(account_number_from):
            error = error_logger.disabled_or_deleted_account()
            print(error)
            return
        
        print("Enter the account number that money will be transferred to:")
        account_number_to = input()  # Get account number that money will be transferred to

        if not Transaction.is_valid_number_format(account_number_to):
            error = error_logger.invalid_account_number_format(account_number_to, LogLevel.ERROR)
            print(error)
            return

        # ------ Account Number Validator ------
        if account_number_to not in valid_accounts:
            error = error_logger.invalid_account_number(account_number_to, LogLevel.ERROR)      
            print(error)
            return
        
        # Check if account is active
        if not Transaction.is_account_active(account_number_to):
            error = error_logger.disabled_or_deleted_account()
            print(error)
            return
        
        print("Enter the amount to transfer:")
        transfer_amount = input()  # Get amount to transfer

        if not Transaction.is_valid_amount_format(str(transfer_amount)):
            error = error_logger.invalid_amount_format(transfer_amount, LogLevel.ERROR)
            print(error)
            return
        else: 
            transfer_amount = float(transfer_amount)

        if not Transaction.limit_manager.check_transfer_limit(transfer_amount) and account_type == "standard":
            error = error_logger.transfer_error(transfer_amount, name, account_number_from)
            print(error)
            return
        
        # Cannot transfer a negative amount
        if not Transaction.limit_manager.non_negative_amount(transfer_amount):
            print("Error: Transfer amount must be non-negative")
            return

        # Create two logs. One for the account that money is being transferred from 
        # and one for the account that money is being transferred to (Withdrawal, Deposit)

        # Get recipient's name from account_number_to
        recipient_name = account_name_map.get(account_number_to, "unknown_user")
        if account_type == "admin":
            log_transaction = TransactionLogger(name, transfer_amount, Transaction.output_file)
            log_transaction.log_transaction("01", name, account_number_from, transfer_amount, Transaction.get_account_plan(account_number_from))
            log_transaction.log_transaction("04", recipient_name, account_number_to, transfer_amount, Transaction.get_account_plan(account_number_to))
        else:
            log_transaction = TransactionLogger(Transaction.current_user, transfer_amount, Transaction.output_file)
            log_transaction.log_transaction("01", Transaction.current_user, account_number_from, transfer_amount, Transaction.get_account_plan(account_number_from))
            log_transaction.log_transaction("04", recipient_name, account_number_to, transfer_amount, Transaction.get_account_plan(account_number_to)) 
            Transaction.limit_manager.add_transfer(transfer_amount)

    # Pays a bill from a bank account
    def paybill(self, account_type):
        valid_names, valid_accounts, account_name_map, _ = Transaction.read_current_bank_accounts(Transaction.input_file)
        error_logger = ErrorLogger()
        VALID_COMPANY_CODES = ["EC", "CQ", "FI"]

        if account_type == "admin":
            print("Enter the account holder's name:")
            name = input().strip().lower()  # Get account holder's name
            
            # ------ Name validator ------
            if name not in valid_names:
                error = error_logger.invalid_account_name(name, LogLevel.ERROR)
                print(error)
                return "Error", None
        else:
            name = Transaction.current_user

        print("Enter the account number:")
        account_number = input()  # Get account number

        if not Transaction.is_valid_number_format(account_number):
            error = error_logger.invalid_account_number_format(account_number, LogLevel.ERROR)
            print(error)
            return
        
        # ------ Account Number Validator ------
        if account_number not in valid_accounts:
            error = error_logger.invalid_account_number(account_number, LogLevel.ERROR)      
            print(error)
            return
        
        if account_number not in account_name_map or account_name_map[account_number] != name:
            error = error_logger.account_number_doesnt_match(name, account_number, LogLevel.ERROR)
            print(error)
            return
        
        print("Enter the company code:")
        company_code = input().strip().upper()  # Get company code
        
        if company_code not in VALID_COMPANY_CODES:
            print("Error: Invalid company code. Please enter a valid company code (EC, CQ, FI).")
            return

        print("Enter the amount to pay:")
        amount = input()  # Get amount to pay

        if not Transaction.is_valid_amount_format(str(amount)):
            error = error_logger.invalid_amount_format(amount, LogLevel.ERROR)
            print(error)
            return
        else: 
            amount = float(amount)

        if not Transaction.limit_manager.check_paybill_limit(amount) and account_type == "standard":
            error = error_logger.paybill_error(amount, name, account_number, company_code)
            print(error)
            return
        
        # Cannot pay a negative amount
        if not Transaction.limit_manager.non_negative_amount(amount):
            print("Error: Paybill amount must be non-negative")
            return
        
        # Check if account is active
        if not Transaction.is_account_active(account_number):
            error = error_logger.disabled_or_deleted_account()
            print(error)
            return
        
        # Log transaction with the given details
        if account_type == "admin":
            log_transaction = TransactionLogger(name, amount, Transaction.output_file)
            log_transaction.log_transaction("03", name, account_number, amount, company_code)
        else:
            log_transaction = TransactionLogger(Transaction.current_user, amount, Transaction.output_file)
            log_transaction.log_transaction("03", Transaction.current_user, account_number, amount, company_code)
            Transaction.limit_manager.add_paybill(amount)


    #-------------------------------------------------- Admin Transactions ------------------------------------------------------
    # Creates a new bank account
    def create(self, account_type):
        error_logger = ErrorLogger()

        if not account_type == "admin":
            print("Error: Only admins can create new accounts!")
            return
        else:
            print("Enter the new account holder's name:")
            new_name = input().strip().lower()  # Get new account holder's name

            if not Transaction.limit_manager.character_limit(new_name):
                print("Error: Name must be 20 characters or less.")
                return

            # ------ New Name Validator ------
            if not Transaction.is_valid_name(new_name):
                error = error_logger.invalid_account_name_input(new_name, LogLevel.ERROR)
                print(error)
                return

            while True:
                print("Enter the initial balance:")
                try:
                    initial_balance = float(input())  # Get initial balance
                    break
                except ValueError:
                    print("Error: Invalid amount. Please enter a numeric value.")
                    continue
                    
            # Cannot have a balance greater than $99999.99
            if not Transaction.limit_manager.max_amount(initial_balance):
                print("Error: Bank account balance must be less than or equal to $99999.99")
                return
            
            # Cannot have a negative balance
            if not Transaction.limit_manager.non_negative_amount(initial_balance):
                print("Error: Bank account balance must be non-negative")
                return

            # Get next account number
            bank_accounts = TransactionLogger(new_name, initial_balance, Transaction.output_file)
            new_account_number = TransactionLogger.next_account_number  # Use static variable

            # Log transaction with the given details
            bank_accounts.log_transaction("05", new_name, new_account_number, initial_balance, "NP")

            
    # Deletes a bank account 
    def delete(self, account_type):
        valid_names, _, account_name_map, _ = Transaction.read_current_bank_accounts(Transaction.input_file)
        error_logger = ErrorLogger()

        if not account_type == "admin":
            print("Error: Only admins can delete accounts!")
            return
        else:
            print("Enter the account holder's name:")
            name = input().strip().lower()  # Get account holder's name

            # ------ Name validator ------
            if name not in valid_names:
                error = error_logger.invalid_account_name(name, LogLevel.ERROR)
                print(error)
                return

            print("Enter the account number:")
            account_number = input()

            if not Transaction.is_valid_number_format(account_number):
                error = error_logger.invalid_account_number_format(account_number, LogLevel.ERROR)
                print(error)
                return

            # ------ Validate Account Number Matches Name ------
            if account_number not in account_name_map or account_name_map[account_number] != name:
                error = error_logger.account_number_doesnt_match(name, account_number, LogLevel.ERROR)
                print(error)
                return

            # Log transaction with the given details
            log_transaction = TransactionLogger(name, account_number, Transaction.output_file)
            log_transaction.log_transaction("06", name, account_number, 0, Transaction.get_account_plan(account_number))

    # Disables transactions for a bank account
    def disable(self, account_type):
        valid_names, _, account_name_map, _ = Transaction.read_current_bank_accounts(Transaction.input_file)
        error_logger = ErrorLogger()
        
        if not account_type == "admin":
            print("Error: Only admins can disable accounts!")
            return
        
        print("Enter the account holder's name:")
        name = input().strip().lower()  # Get account holder's name

        # ------ Name validator ------
        if name not in valid_names:
            error = error_logger.invalid_account_name(name, LogLevel.ERROR)
            print(error)
            return

        print("Enter the account number:")
        account_number = input()  # Get account number

        if not Transaction.is_valid_number_format(account_number):
            error = error_logger.invalid_account_number_format(account_number, LogLevel.ERROR)
            print(error)
            return
        
        # ------ Validate Account Number Matches Name ------
        if account_number not in account_name_map or account_name_map[account_number] != name:
            error = error_logger.account_number_doesnt_match(name, account_number, LogLevel.ERROR)
            print(error)
            return
        
        # Check if account is active
        if not Transaction.is_account_active(account_number):
            print("Error: Account is already disabled or deleted")
            return

        # Log transaction with the given details
        log_transaction = TransactionLogger(name, account_number, Transaction.output_file)
        log_transaction.log_transaction("07", name, account_number, 0, Transaction.get_account_plan(account_number))


    # Changes the account plan of a user
    def changeplan(self, account_type):
        valid_names, _, account_name_map, _ = Transaction.read_current_bank_accounts(Transaction.input_file)
        error_logger = ErrorLogger()

        if not account_type == "admin":
            print("Error: Only admins can change plan!")
            return

        print("Enter the account holder's name:")
        name = input().strip().lower()  # Get account holder's name

        # ------ Name validator ------
        if name not in valid_names:
            error = error_logger.invalid_account_name(name, LogLevel.ERROR)
            print(error)
            return

        print("Enter the account number:")
        account_number = input()  # Get account number

        if not Transaction.is_valid_number_format(account_number):
            error = error_logger.invalid_account_number_format(account_number, LogLevel.ERROR)
            print(error)
            return

        # ------ Validate Account Number Matches Name ------
        if account_number not in account_name_map or account_name_map[account_number] != name:
            error = error_logger.account_number_doesnt_match(name, account_number, LogLevel.ERROR)
            print(error)
            return

        # Check if account is active
        if not Transaction.is_account_active(account_number):
            error = error_logger.disabled_or_deleted_account()
            print(error)
            return

        # Log transaction with the given details
        log_transaction = TransactionLogger(name, account_number, Transaction.output_file)
        log_transaction.log_transaction("08", name, account_number, 0, Transaction.get_account_plan(account_number))

    # ------- Helper Function to load current bank accounts file -------
    @staticmethod
    def read_current_bank_accounts(current_bank_accounts):
        valid_names = set()
        valid_account_numbers = set()
        account_info_map = {}
        account_status_map = {}

        try:
            with open(current_bank_accounts, "r") as file:
                for line in file:
                    line = line.rstrip('\n')
                    if len(line) < 37:  # skip invalid lines
                        continue

                    account_number = line[0:5]
                    account_name = line[6:26].strip().lower()  # 20-char name, left-justified
                    account_status = line[27]  # A or D

                    # Optional: Stop parsing at END_OF_FILE
                    if account_name == "end_of_file":
                        break

                    valid_names.add(account_name)
                    valid_account_numbers.add(account_number)
                    account_info_map[account_number] = account_name
                    account_status_map[account_number] = account_status

        except FileNotFoundError:
            print("Error: Current bank accounts file not found")
            return set(), set(), {}, {}

        return valid_names, valid_account_numbers, account_info_map, account_status_map

    
    @staticmethod
    def is_valid_name(name):
        return bool(re.match(r"^[a-zA-Z_]+$", name))
    
    def is_valid_number_format(number):
        return bool(re.match(r"^[0-9]+$", number))
    
    def is_valid_amount_format(amount):
        return bool(re.match(r"^\d{0,5}[.]?\d{0,2}$", amount))
    
    @staticmethod
    def is_account_active(account_number):
        _, _, _, account_status_map = Transaction.read_current_bank_accounts(Transaction.input_file)
        return account_status_map.get(account_number) == 'A'