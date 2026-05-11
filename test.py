from src.llm_parser import parse_transaction
from src.transaction_service import save_transaction
from src.database import get_all_transactions, remove_all_transactions
from src.report_service import get_finance_summary, get_expense_by_category

text = input("Transaction: ")

transaction = save_transaction(text)

print("\nSaved transaction:")
print("Date:", transaction.date)
print("Type:", transaction.type)
print("Category:", transaction.category)
print("Amount:", transaction.amount)
print("Note:", transaction.note)

print("\n All transactions:")
rows = get_all_transactions()

for row in rows:
    print(row)

summary = get_finance_summary()
print(summary)

expense_summary = get_expense_by_category()
print(expense_summary)

