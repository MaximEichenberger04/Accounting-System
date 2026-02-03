from abc import ABC, abstractmethod

class BalanceSheet():
    def __init__(self, name: str):
        self.name = name
        #active side
        self.current_assets = []
        self.non_current_assets = []
        #passive side
        self.short_term_liabilities = []
        self.long_term_liabilities = []
        self.equity = []
        #overdraft accounts
        self.overdrafts = []

    def add_account(self, account):
        if isinstance(account, ActiveAccount):
            if account.account_type == "current":
                self.current_assets.append(account)
                return
            elif account.account_type == "non-current":
                self.non_current_assets.append(account)
                return
            raise ValueError("ActiveAccount type not supported in Balance Sheet: " + account.account_type)

        elif isinstance(account, PassiveAccount):
            if account.account_type == "short-term":
                self.short_term_liabilities.append(account)
                return
            elif account.account_type == "long-term":
                self.long_term_liabilities.append(account)
                return
            elif account.account_type == "equity":
                self.equity.append(account)
                return
            raise ValueError("PassiveAccount type not supported in Balance Sheet: " + account.account_type)
        raise TypeError("Balance Sheet only supports: ActiveAccount or PassiveAccount")
    
    def reclassify_account(self, account):
        account.check_balance()
        if account.saldo < 0: #Overdraft -> Reclassify Account
            new_account = Overdraft().reclassify(account)

            if new_account is not None:
                self.add_account(new_account)
            return
        self.add_account(account)

    def balance(self):
        if not hasattr(self, "_overdraft_checked"):
            self._overdraft_checked = True

            for acc in list(self.current_assets) + list(self.short_term_liabilities):
                acc.check_balance()

                if acc.saldo < 0: #check for overdraft
                    new_acc = Overdraft().reclassify(acc)

                    #remove origin accounts
                    if isinstance(acc, ActiveAccount) and acc.account_type == "current":
                        self.current_assets.remove(acc)
                    elif isinstance(acc, PassiveAccount) and acc.account_type == "short-term":
                        self.short_term_liabilities.remove(acc)

                    #create new account on other side
                    if new_acc is not None:
                        if isinstance(new_acc, PassiveAccount):
                            self.short_term_liabilities.append(new_acc)
                        elif isinstance(new_acc, ActiveAccount):
                            self.current_assets.append(new_acc)

        self.non_current_assets = [acc for acc in self.non_current_assets if acc.name != "Verlust"]
        self.equity = [acc for acc in self.equity if acc.name != "Gewinn"]

        active = ( sum(acc.end_balance() for acc in self.current_assets) + 
                        sum(acc.end_balance() for acc in self.non_current_assets) )
        
        passive = ( sum(acc.end_balance() for acc in self.short_term_liabilities) +
                         sum(acc.end_balance() for acc in self.long_term_liabilities) + 
                         sum(acc.end_balance() for acc in self.equity) )
                
        earnings = active - passive
        self.equity = [acc for acc in self.equity if acc.name not in ["Gewinn", "Verlust"]]
        Jahresergebnis = PassiveAccount("Jahresergebnis", "equity")

        if earnings > 0:
            Jahresergebnis.name = "Gewinn"
            Jahresergebnis.inflow(earnings)
        elif earnings < 0:
            Jahresergebnis.name = "Verlust"
            Jahresergebnis.outflow(abs(earnings))
        if earnings != 0:
            self.equity.append(Jahresergebnis)

        return earnings

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

    def end_balance(self): #balance for balance sheet
        return sum(self.debit) - sum(self.credit)

    def check_balance(self): #calculate saldo
        sum_debit = sum(self.debit)
        sum_credit = sum(self.credit)
        self.saldo = sum_debit - sum_credit
        if self.saldo == 0:
            return {"status": "settled", "saldo": 0}
        elif self.saldo > 0:
            return {"status": "open", "saldo": self.saldo}
        else: #account overdraft
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

    def end_balance(self): #balance for balance sheet
        return sum(self.credit) - sum(self.debit)
    
    def check_balance(self): #calculate saldo
        sum_credit = sum(self.credit)
        sum_debit = sum(self.debit)
        self.saldo = sum_credit - sum_debit
        if self.saldo == 0:
            return {"status": "settled", "saldo": 0}
        elif self.saldo > 0:
            return {"status": "open", "saldo": self.saldo}
        else: #account overdraft
            overdraft = self.saldo
            return {"status": "overdraft", "saldo": overdraft}

class Overdraft:
    def __init__(self, annual_rate_pct=5.0, overdraft_fee=0.0):
        self.annual_rate_pct = annual_rate_pct
        self.overdraft_fee = overdraft_fee

    def _annual_interest(self, amount): #calculate interest
        return amount * (self.annual_rate_pct / 100)

    def reclassify(self, account): #initial account set to 0
        bal = account.end_balance()
        if bal >= 0:
            return None

        amount = abs(bal)  #overdraft amount, abs(-100) = 100
        interest = self._annual_interest(amount)

        #Case 1: Current Account (Bank) overdraft -> Short-term Account (Bank-Kontokorrent)
        if isinstance(account, ActiveAccount) and account.account_type == "current":
            kontokorrent = PassiveAccount(account.name + "-Kontokorrent", "short-term")
            kontokorrent.inflow(amount + interest + self.overdraft_fee)  #overdraft amount + interest + fee
            return kontokorrent

        #Case 2: Short-term Account (Kreditoren) overdraft -> Current Account (Kreditoren-Guthaben)
        if isinstance(account, PassiveAccount) and account.account_type == "short-term":
            guthaben = ActiveAccount(account.name + "-Guthaben", "current")
            guthaben.inflow(amount + interest)  #overpayment amount + interest
            return guthaben

        raise ValueError("Reclassification only implemented for: Active current, Passive short-term. Only current asset and short-term liabilites can have balance sheet overdraft amounts!")


Kreditoren = PassiveAccount("Kreditoren", "short-term")
Kreditoren.inflow(5000)
Kreditoren.outflow(2000)
print("Kreditoren Bilanz:", Kreditoren.end_balance())
print("Kreditoren Saldo:", Kreditoren.check_balance())
Kreditoren.outflow(3000)
print(Kreditoren.__dict__, Kreditoren.__class__.__name__)
print("Kreditoren Saldo:", Kreditoren.check_balance())  
Kreditoren.outflow(100)
print("Kreditoren Bilanz:", Kreditoren.end_balance())
print("Kreditoren Saldo:", Kreditoren.check_balance())  
print(Kreditoren.__dict__, Kreditoren.__class__.__name__)
Hypothek = PassiveAccount("Hypothek", "long-term")
Hypothek.inflow(10000)
print("Hypothek Bilanz:", Hypothek.end_balance())
print(Hypothek.__dict__, Hypothek.__class__.__name__)
Bank = ActiveAccount("Bank", "current")
Bank.inflow(6000)
Kasse = ActiveAccount("Kasse", "current")
Kasse.inflow(3000)
print(Bank.__dict__, Bank.__class__.__name__)
print(Kasse.__dict__, Kasse.__class__.__name__)
BalanceSheet2025 = BalanceSheet("Balance Sheet 2025")
BalanceSheet2025.add_account(Kreditoren)
print(BalanceSheet2025.balance())