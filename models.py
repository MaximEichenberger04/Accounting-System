from abc import ABC, abstractmethod

class Account(ABC):
    def __init__(self, name: str):
        self.name = name
        self.credit = [] #list
        self.debit = [] #list
        self.closed = False

    def __str__(self):
        self.check_balance()
        return (
            f"{self.__class__.__name__} | {self.name} | {getattr(self, 'account_type', '-')} | Saldo {self.saldo}"
        )

    @abstractmethod
    def inflow(self, amount: float):
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def outflow(self, amount: float):
        raise NotImplementedError("Abstract method")    

    @abstractmethod
    def check_balance(self):
        raise NotImplementedError("Abstract method")    
    
    @abstractmethod
    def end_balance(self):
        pass
       
    @abstractmethod
    def check_balance(self):
        pass 

    def close(self):
        saldo = self.end_balance()
        if saldo > 0:
            self.credit.append(saldo)
        elif saldo < 0:
            self.debit.append(abs(saldo))
        self.closed = True

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

    def reclassify(self, account: Account): #initial account set to 0
        saldo = account.end_balance()
        if saldo >= 0:
            return None

        amount = abs(saldo)  #overdraft amount, abs(-100) = 100
        interest = self._annual_interest(amount)

        #Case 1: Current Account (Bank) overdraft -> Short-term Account (Bank-Kontokorrent)
        if isinstance(account, ActiveAccount) and account.account_type == "current":
            kontokorrent = PassiveAccount(account.name + "-Kontokorrent", "short-term")
            kontokorrent.inflow(amount + interest + self.overdraft_fee)  #overdraft amount + interest + fee
            account.close() #close the old account
            return kontokorrent

        #Case 2: Short-term Account (Kreditoren) overdraft -> Current Account (Kreditoren-Guthaben)
        if isinstance(account, PassiveAccount) and account.account_type == "short-term":
            guthaben = ActiveAccount(account.name + "-Guthaben", "current")
            guthaben.inflow(amount + interest)  #overpayment amount + interest
            account.close() #close the old account
            return guthaben

        raise ValueError("Reclassification only implemented for: Active current, Passive short-term. Only current asset and short-term liabilites can have balance sheet overdraft amounts!")

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
            elif account.account_type == "non-current":
                self.non_current_assets.append(account)
            else:
                raise ValueError("ActiveAccount type not supported in Balance Sheet: " + account.account_type)

        elif isinstance(account, PassiveAccount):
            if account.account_type == "short-term":
                self.short_term_liabilities.append(account)
            elif account.account_type == "long-term":
                self.long_term_liabilities.append(account)
            elif account.account_type == "equity":
                self.equity.append(account)
            else:
                raise ValueError("PassiveAccount type not supported in Balance Sheet: " + account.account_type)
        
        else:
            raise TypeError("Balance Sheet only supports: ActiveAccount or PassiveAccount")
    
    def reclassify_account(self, account: Account):
        od = Overdraft()
        new_account = od.reclassify(account)
        if new_account is not None:
            if isinstance(account, ActiveAccount) and account.account_type == "current":
                self.current_assets.remove(account)
            elif isinstance(account, PassiveAccount) and account.account_type == "short-term":
                self.short_term_liabilities.remove(account)
            self.add_account(new_account)

    def balance(self):
        if not hasattr(self, "_overdraft_checked"):
            self._overdraft_checked = True
            #make a list of all current/short-term accounts
            accounts_to_check = list(self.current_assets) + list(self.short_term_liabilities)
            
            for acc in accounts_to_check:
                acc.check_balance()
                if acc.saldo < 0: #check for overdraft
                    new_acc = Overdraft().reclassify(acc)

                    #remove origin accounts
                    if isinstance(acc, ActiveAccount) and acc.account_type == "current":
                        if acc in self.current_assets: #Check if still in list
                            self.current_assets.remove(acc)
                    elif isinstance(acc, PassiveAccount) and acc.account_type == "short-term":
                        if acc in self.short_term_liabilities: #Check if still in list
                            self.short_term_liabilities.remove(acc)

                    #create new account on other side
                    if new_acc is not None:
                        if isinstance(new_acc, PassiveAccount):
                            self.short_term_liabilities.append(new_acc)
                        elif isinstance(new_acc, ActiveAccount):
                            self.current_assets.append(new_acc)
        active = ( sum(acc.end_balance() for acc in self.current_assets) + 
                   sum(acc.end_balance() for acc in self.non_current_assets) )
        
        passive = ( sum(acc.end_balance() for acc in self.short_term_liabilities) +
                    sum(acc.end_balance() for acc in self.long_term_liabilities) + 
                    sum(acc.end_balance() for acc in self.equity) )
                
        earnings = active - passive #assets - (liabilities + equity)
        annual_result = None
        for acc in self.equity:
            if acc.name in ["Gewinn", "Verlust", "annual_result"]:
                annual_result = acc
                break
        if annual_result is None: #if account does not yet exist, create one
            annual_result = PassiveAccount("annual_result", "equity")
            self.equity.append(annual_result)
        
        #Update the annual_result account based on current earnings (profit and loss)
        annual_result.credit = [] #reset !!
        annual_result.debit = [] #reset !!
        if earnings > 0:
            annual_result.name = "Gewinn"
            annual_result.inflow(earnings)
        elif earnings < 0:
            annual_result.name = "Verlust"
            annual_result.outflow(abs(earnings))
        else:
            annual_result.name = "annual_result"

        return earnings
