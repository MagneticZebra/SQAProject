class LimitManager:
    def __init__(self, limit_withdraw: float, limit_transfer: float, limit_paid: float, bank_account_limit: float):
        self.daily_withdrawn = 0.0
        self.daily_transferred = 0.0
        self.daily_paid = 0.0
        self.daily_deposit = 0.0  # These funds are locked and are unavaiable to withdraw, transfer or paybill. Add to those transaction to ensure enough funds are in the account
        self.limit_withdraw = limit_withdraw
        self.limit_transfer = limit_transfer
        self.limit_paid = limit_paid
        self.bank_account_limit = bank_account_limit
    
    def character_limit(self, characters: str) -> bool:
        return len(str(characters)) <= 20
    
    def max_amount(self, amount: float) -> bool:
        return amount <= self.bank_account_limit
    
    def non_negative_amount(self, amount: float) -> bool:
        return amount >= 0.0

    def check_withdrawal_limit(self, amount: float) -> bool:
        return (self.daily_withdrawn + amount) <= self.limit_withdraw
    
    def check_transfer_limit(self, amount: float) -> bool:
        return (self.daily_transferred + amount) <= self.limit_transfer
    
    def check_paybill_limit(self, amount: float) -> bool:
        return (self.daily_paid + amount) <= self.limit_paid
    
    def add_withdrawal(self, amount: float) -> None:
        if self.check_withdrawal_limit(amount):
            self.daily_withdrawn += amount
    
    def add_transfer(self, amount: float) -> None:
        if self.check_transfer_limit(amount):
            self.daily_transferred += amount
    
    def add_paybill(self, amount: float) -> None:
        if self.check_paybill_limit(amount):
            self.daily_paid += amount

    def add_deposit(self, amount: float) -> None:
        self.daily_deposit += amount

    def reset_limits(self):
        self.daily_withdrawn = 0.0
        self.daily_transferred = 0.0
        self.daily_paid = 0.0
        self.daily_deposit =0.0