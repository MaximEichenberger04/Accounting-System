from abc import ABC, abstractmethod
class Account(ABC):
    def __init__(self, name: str):
        self.name = name
        self.credit = [] #list
        self.debit = [] #list

    @abstractmethod
    def inflow(self, amount: float):
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def outflow(self, amount: float):
        raise NotImplementedError("Abstract method")    
    
    @abstractmethod
    def calculate_balance(self):
        raise NotImplementedError("Abstract method")     

    @abstractmethod
    def check_balance(self):
        raise NotImplementedError("Abstract method")    

class ActiveAccount(Account):
    def __init__(self, account_type):
        super().__init__(name)
        if account_type not in ["current", "non-current", "overdraft"]:
            raise ValueError("Invalid account type: Must be 'current' or 'non-current' active account.")
        self.account_type = account_type
    
    def inflow(self, amount: float):
        self.debit.append(amount)

    def outflow(self, amount: float):
        self.credit.append(amount)

    def calculate_balance(self):
        sum_debit = sum(self.debit)
        sum_credit = sum(self.credit)
        self.balance = sum_debit - sum_credit
        return self.balance
    
    def check_balance(self):
        sum_debit = sum(self.debit)
        sum_credit = sum(self.credit)
        if sum_debit == sum_credit:
            return "The account is balanced."
        elif sum_debit > sum_credit:
            self.saldo = sum_debit - sum_credit
            self.credit.append(self.saldo)
            return self.saldo
        elif sum_debit < sum_credit: #account overdraft
            self.saldo = sum_credit - sum_debit
            self.debit.append(self.saldo)
            self.account_type = "overdraft"
            return self.saldo
        
class PassiveAccount(Account):
    def __init__(self, account_type):
        super().__init__(name)
        if account_type not in ["short-term", "long-term", "equity", "overdraft"]:
            raise ValueError("Invalid account type: Must be 'short-term', 'long-term', or 'equity' passive account.")
        self.account_type = account_type   
    
    def inflow(self, amount: float):
        self.credit.append(amount)

    def outflow(self, amount: float):
        self.debit.append(amount)

    def calculate_balance(self):
        sum_credit = sum(self.credit)
        sum_debit = sum(self.debit)
        self.balance = sum_credit - sum_debit
        return self.balance
    
    def check_balance(self):
        sum_credit = sum(self.credit)
        sum_debit = sum(self.debit)
        if sum_credit == sum_debit:
            return "The account is balanced."
        elif sum_credit > sum_debit:
            self.saldo = sum_credit - sum_debit
            self.debit.append(self.saldo)
            return self.saldo
        elif sum_credit < sum_debit: #account overdraft
            self.saldo = sum_debit - sum_credit
            self.credit.append(self.saldo)
            self.account_type = "overdraft"
            return self.saldo