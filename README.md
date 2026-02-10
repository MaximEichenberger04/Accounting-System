# Simple OOP-based Accounting System

This project is a simple accounting system that allows a user to create a closing balance sheet at the end of a financial year. It supports different types of balance sheet accounts (active and passive) and is based on Swiss accounting principles, which is why the user interface is in German.

The system calculates profit or loss based on the difference between the active and passive sides of the balance sheet and supports automatic account reclassification, for example when a bank account goes into overdraft (→ Bank-Kontokorrent).
## Motivation

I built this project since I firstly was involved with accounting in High School and took Financial Accounting at Uni again. I wanted to strengthen my skills in Object-Oriented Programming as well as build a small full-stack application that could help someone with basic accounting tasks. This application could, for example, be used by a teacher or students to create a balance sheet for exercises or exam purposes.

My goal was to:
- implement an OOP-based Accounting System
- be able to reclassify accounts if they happen to be in overdraft
- calculate & display profit/loss directly from the balance sheet

## Scope & Limitations

This project simply helps with creating a balance sheet. It does **not** generate and income or cashflow statement. There is no way to find how profit/loss is based on cost/economic output for which we would need an income statement. P/L is simply based on *Assets - (Liabilities+Equity)*. In the future I might extend this system with an Income Statement, and perhaps Cashflow functionality as well.

## Tech Stack

- **Python** - simple and well-suited for OOP
- **Flask** – lightweight backend framework
- **HTML/CSS** – create an input page & redirect to a final balance sheet
- (Optional in the future)**SQLite** - for storing old accounts/balance sheets in a local database

## Project Structure

- app.py: Flask web application entry point. Handles routing, processes user input, and renders HTML templates. Displays an input page for creating accounts and recording inflows/outflows. When viewing the balance sheet, it renders balance.html and computes profit or loss based on *Assets − (Liabilities + Equity)*.
- models.py: OOP based accounting system logic (Balance sheet, passive & active accounts, overdraft handling and automatic account reclassification)
- templates (frontend): index.html (+index.css) for user input and balance.html (+ balance.css) for presentation of balance sheet and profit/loss according to changes in assets
- local/main.py: for testing features locally and finding bugs
  
<img width="1189" height="511" alt="image" src="https://github.com/user-attachments/assets/9e47f2b9-1c62-422d-aaa8-fd3e40dedaaf" />
