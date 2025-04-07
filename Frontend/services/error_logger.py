from enum import Enum

# enum allows us to keep track of the sevarity of an error
# and keep the errors consistent
class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"

class Error:
    def __init__(self, message: str, log_level: LogLevel):
        self.message = message
        self.log_level = log_level
    
    def __str__(self):
        return f"[{self.log_level.value.upper()}] {self.message}"

class ErrorLogger:
    def __init__(self, log_level: LogLevel = LogLevel.ERROR):
        self.log_level = log_level
    
    def invalid_account_name(self, account_name: str, log_level: LogLevel) -> Error:
        return Error(f"Invalid account name: {account_name}", log_level)
    
    def invalid_account_name_input(self, account_name: str, log_level: LogLevel) -> Error:
        return Error(f"Invalid account name input (Only letters allowed): {account_name}", log_level)
    
    def invalid_account_number_format(self, account_number: str, log_level: LogLevel) -> Error:
        return Error(f"Invalid account number format (Only numbers allowed): {account_number}", log_level)
    
    def invalid_account_number(self, account_number: str, log_level: LogLevel) -> Error:
        return Error(f"Invalid account number: {account_number}", log_level)
    
    def invalid_amount_format(self, amount: str, log_level: LogLevel) -> Error:
        return Error(f"Invalid amount format: {amount}", log_level)

    def account_number_doesnt_match(self, account_name : str, account_number : str, log_level: LogLevel) -> Error:
        return Error(f"Account number: {account_number} Does not match current user's: {account_name} on file account number", log_level)

    def invalid_transaction_amount(self, amount: float, log_level: LogLevel) -> Error:
        return Error(f"Invalid transaction amount: {amount}", log_level)
    
    def deposit_error(self, amount: float, account_name: str, account_number: str) -> Error:
        return Error(f"Deposit error: {amount} for account {account_name} ({account_number})", LogLevel.ERROR)
    
    def withdraw_error(self, amount: float, account_name: str, account_number: str) -> Error:
        return Error(f"Withdraw error: {amount} for account {account_name} ({account_number})", LogLevel.ERROR)
    
    def transfer_error(self, amount: float, account_name: str, account_number: str) -> Error:
        return Error(f"Transfer error: {amount} for account {account_name} ({account_number})", LogLevel.ERROR)
    
    def paybill_error(self, amount: float, account_name: str, account_number: str, company_code: str) -> Error:
        return Error(f"Paybill error: {amount} for account {account_name} ({amount} payable to {company_code})", LogLevel.ERROR)
    
    def disabled_or_deleted_account(self) -> Error:
        return Error(f"Transactions cannot be performed on disabled or deleted accounts.", LogLevel.ERROR)