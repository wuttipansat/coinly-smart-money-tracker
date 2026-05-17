import pandas as pd

from src.mongodb_database import get_all_transactions


TRANSACTION_COLUMNS = [
    "id",
    "date",
    "type",
    "category",
    "amount",
    "note"
]


def load_transactions_df():
    rows = get_all_transactions()

    df = pd.DataFrame(
        rows,
        columns=TRANSACTION_COLUMNS
    )

    if df.empty:
        return df

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    ).fillna(0)

    return df


def get_finance_summary():
    df = load_transactions_df()

    if df.empty:
        return {
            "total_income": 0,
            "total_expense": 0,
            "balance": 0
        }

    total_income = df.loc[
        df["type"] == "income",
        "amount"
    ].sum()

    total_expense = df.loc[
        df["type"] == "expense",
        "amount"
    ].sum()

    balance = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    }


def get_expense_by_category():
    df = load_transactions_df()

    if df.empty:
        return pd.DataFrame(
            columns=["category", "amount"]
        )

    expense_df = df[df["type"] == "expense"]

    if expense_df.empty:
        return pd.DataFrame(
            columns=["category", "amount"]
        )

    return (
        expense_df
        .groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )