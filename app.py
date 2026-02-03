from flask import Flask, request, redirect, render_template, send_from_directory
from models import ActiveAccount, PassiveAccount, BalanceSheet

app = Flask(__name__)

balance_sheet = BalanceSheet("Balance Sheet 2025")

@app.get("/style.css")
def style(): #style for frontend
    return send_from_directory("templates", "style.css")

@app.get("/balance")
def show_balance(): #show final balance sheet
    balance_sheet.balance() #calculate profit/loss
    return render_template("balance.html", bs=balance_sheet)

@app.get("/")
def index(): #show frontend to user
    return render_template("index.html")

@app.post("/add-account")
def add_account(): #add account (name, side, type) & amount to accounting system
    name = request.form["name"]
    side = request.form["side"]
    account_type = request.form["type"]
    amount = float(request.form["amount"])
    flow = request.form["flow"]

    all_accounts = ( #tuple of all accounts
        balance_sheet.current_assets
        + balance_sheet.non_current_assets
        + balance_sheet.short_term_liabilities
        + balance_sheet.long_term_liabilities
        + balance_sheet.equity
    )

    account = None
    for acc in all_accounts: #check if account (name) already exists 
        if acc.name == name:
            account = acc
            break

    if account is None: #if does not exist, initialize a new account
        if side == "active":
            account = ActiveAccount(name, account_type)
        else:
            account = PassiveAccount(name, account_type)

        balance_sheet.add_account(account)

    if flow == "inflow":
        account.inflow(amount)
    else:
        account.outflow(amount)

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
