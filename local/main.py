from models import ActiveAccount, PassiveAccount, BalanceSheet, Overdraft

Kreditoren = PassiveAccount("Kreditoren", "short-term")
Kreditoren.inflow(5000)
Kreditoren.outflow(2000)
print("Kreditoren Bilanz:", Kreditoren.end_balance())
print("Kreditoren Saldo:", Kreditoren.check_balance())
Kreditoren.outflow(3000)
print(Kreditoren.__dict__, Kreditoren.__class__.__name__)
print("Kreditoren Saldo:", Kreditoren.check_balance())
Kreditoren.outflow(100) #now creditors should be closed and become an active account
#Kreditoren-Guthaben, since we paid too much and this should be done by Overdraft class
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
Bank.outflow(7000)
BalanceSheet2025 = BalanceSheet("Balance Sheet 2025")
BalanceSheet2025.add_account(Kreditoren)
BalanceSheet2025.reclassify_account(Kreditoren)
BalanceSheet2025.add_account(Bank)
BalanceSheet2025.reclassify_account(Bank)
print(BalanceSheet2025.balance())
for acc in (
    BalanceSheet2025.current_assets
    + BalanceSheet2025.non_current_assets
    + BalanceSheet2025.short_term_liabilities
    + BalanceSheet2025.long_term_liabilities
    + BalanceSheet2025.equity
):
    print(acc)
print(Bank.__dict__, Bank.__class__.__name__)
print(Kasse.__dict__, Kasse.__class__.__name__)
