from models.transaction import Transaction
import sys


def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]  # current bank accounts
    output_file = sys.argv[2]  # bank account transaction file

    print("Welcome to the Banking System!")

    while True:  
        login_result = Transaction.login(input_file, output_file)
        if login_result == ("Error", None):
            continue 

        account_type, account_name = login_result

        while True:  # Keeps the user logged in until they log out
            print("Enter transaction type:")
            transaction_type = input().strip().lower()

            if transaction_type == "logout":
                transaction = Transaction()
                transaction.logout() 
                break

            elif transaction_type in ["withdrawal", "deposit", "transfer", "paybill", "create", "delete", "disable", "changeplan"]:
                transaction = Transaction()
                getattr(transaction, transaction_type)(account_type)
            else:
                print("Invalid transaction type. Try again.")

        break


if __name__ == "__main__":
    main()
