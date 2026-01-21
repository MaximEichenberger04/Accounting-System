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
    def __init__(self, name: str, account_type: str):
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
        self.saldo = sum_debit - sum_credit
        if self.saldo == 0:
            return {"status": "settled", "saldo": 0}
        elif self.saldo > 0:
            return {"status": "open", "saldo": self.saldo}
        else: #account overdraft
            self.account_type = "overdraft"
            overdraft = self.saldo
            return {"status": "overdraft", "saldo": overdraft}
        
class PassiveAccount(Account):
    def __init__(self, name: str, account_type: str):
        super().__init__(name)
        if account_type not in ["short-term", "long-term", "equity", "overdraft"]:
            raise ValueError("Invalid account type: Must be 'short-term', 'long-term', or 'equity' passive account.")
        self.account_type = account_type   
    
    def inflow(self, amount: float):
        self.credit.append(amount)

    def outflow(self, amount: float):
        self.debit.append(amount)

    def calculate_balance(self): #balance for balance sheet
        sum_credit = sum(self.credit)
        sum_debit = sum(self.debit)
        self.balance = sum_credit - sum_debit
        return self.balance
    
    def check_balance(self): #calculate saldo
        sum_credit = sum(self.credit)
        sum_debit = sum(self.debit)
        self.saldo = sum_credit - sum_debit
        if self.saldo == 0:
            return {"status": "settled", "saldo": 0}
        elif self.saldo > 0:
            return {"status": "open", "saldo": self.saldo}
        else: #account overdraft
            self.account_type = "overdraft"
            overdraft = self.saldo
            return {"status": "overdraft", "saldo": overdraft}

class Overdraft:
    def __init__(self, annual_rate_pct=5.0, overdraft_fee=25.0):
        self.annual_rate_pct = annual_rate_pct
        self.overdraft_fee = overdraft_fee

    def _annual_interest(self, amount): #calculate interest
        return amount * (self.annual_rate_pct / 100)

    def reclassify(self, account): #initial account set to 0
        bal = account.calculate_balance()
        if bal >= 0:
            return None

        amount = -bal  #overdraft
        interest = self._annual_interest(amount)

        #Case 1: Current Account (Bank) overdraft -> Short-term Account (Bank-Kontokorrent)
        if isinstance(account, ActiveAccount) and account.account_type == "current":
            account.debit = [0.0] #booking out
            account.credit = [0.0] #booking out

            kontokorrent = PassiveAccount(account.name + "-Kontokorrent", "short-term")
            kontokorrent.inflow(amount + interest + self.overdraft_fee)  #overdraft amount + interest + fee
            return kontokorrent

        #Case 2: Short-term Account (Kreditoren) overdraft -> Current Account (Kreditoren-Guthaben)
        if isinstance(account, PassiveAccount) and account.account_type == "short-term":
            account.debit = [0.0] #booking out
            account.credit = [0.0] #booking out

            guthaben = ActiveAccount(account.name + "-Guthaben", "current")
            guthaben.inflow(amount + interest)  #overpayment amount + interest
            return guthaben

        raise ValueError("Reclassification only implemented for: Active current, Passive short-term. Only current asset and short-term liabilites can have balance sheet overdraft amounts!")


Kreditoren = PassiveAccount("Kreditoren", "short-term")
Kreditoren.inflow(5000)
Kreditoren.outflow(2000)
print("Kreditoren Balance:", Kreditoren.calculate_balance())
print("Kreditoren Check Balance:", Kreditoren.check_balance())  
Kreditoren.outflow(3000)
print("Kreditoren Check Balance:", Kreditoren.check_balance())  
Kreditoren.outflow(100)
print("Kreditoren Check Balance:", Kreditoren.check_balance())  
