import pandas as pd
import streamlit as st

from src.supabase_database import get_all_transactions


TRANSACTION_COLUMNS = [
    "id",
    "date",
    "type",
    "category",
    "amount",
    "note"
]


@st.cache_data(ttl=30)
def load_transactions_df(user_id):
    rows = get_all_transactions(user_id)

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


def get_finance_summary(user_id):
    df = load_transactions_df(user_id)

    if df.empty:
        return {
            "total_income": 0,
            "total_expense": 0,
            "balance": 0,
        }

    total_income = df.loc[
        df["type"] == "income",
        "amount"
    ].sum()

    total_expense = df.loc[
        df["type"] == "expense",
        "amount"
    ].sum()

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
    }


def get_expense_by_category(user_id):
    df = load_transactions_df(user_id)

    if df.empty:
        return pd.DataFrame(columns=["category", "amount"])

    expense_df = df[df["type"] == "expense"]

    if expense_df.empty:
        return pd.DataFrame(columns=["category", "amount"])

    return (
        expense_df
        .groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )