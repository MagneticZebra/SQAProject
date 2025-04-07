import os

class TransactionLogger:
    next_account_number = None  # Static variable for all instances

    def __init__(self, account_name, amount, output_file, current_accounts_file=None):
        self.account_name = account_name
        self.amount = amount
        self.output_file = output_file
        self.current_accounts_file = current_accounts_file

        if TransactionLogger.next_account_number is None:
            TransactionLogger.next_account_number = (
                self.get_next_account_number_from_accounts()
                if current_accounts_file else 1000
            )

    # Finds the next available account number by checking the transaction log file (output_file)
    def get_next_account_number_from_accounts(self):
        if not os.path.exists(self.current_accounts_file):
            return 1000

        used_numbers = set()
        with open(self.current_accounts_file, "r") as file:
            for line in file:
                if len(line) < 5:
                    continue
                acct_num = line[0:5]
                if acct_num.isdigit():
                    used_numbers.add(int(acct_num))

        new_number = 1000
        while new_number in used_numbers:
            new_number += 1

        return new_number


    # Logs a transaction into the provided transaction log file (output_file).
    def log_transaction(self, code, name, account_number, amount, plan_or_company_code):
        transaction_code = code.zfill(2)
        account_holder_name = name.ljust(20)[:20]
        account_number = str(account_number).zfill(5)
        formatted_amount = "{:08.2f}".format(amount)

        misc_field = plan_or_company_code.ljust(2)[:2]

        # Format the full transaction line
        transaction_line = f"{transaction_code} {account_holder_name} {account_number} {formatted_amount} {misc_field}"

        with open(self.output_file, "a") as file:
            file.write(transaction_line + "\n")


    # Writes the end-of-session transaction to the output file
    def write_end_of_session(self):
        end_of_session_line = "00" + " " * 22 + "00000" + " " + "00000.00" + " 00"

        with open(self.output_file, "a") as file:
            file.write(end_of_session_line + "\n")  # Append newline for proper formatting
        
        # print(f"Logged end-of-session transaction: {end_of_session_line}")