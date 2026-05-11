from src.database import create_table, add_transaction
from src.llm_parser import parse_transaction

def save_transaction(text: str):
    create_table()

    transaction = parse_transaction(text)

    add_transaction(
        date = transaction.date,
        type_ = transaction.type,
        category = transaction.category,
        amount = transaction.amount,
        note = transaction.note
    )

    return transaction

