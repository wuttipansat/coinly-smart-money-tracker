import sqlite3
import pandas as pd

from src.database import get_connection

def load_transactions_df() -> pd.DataFrame:
    
    conn =get_connection()

    df = pd.read_sql_query(
        """SELECT * FROM transactions ORDER BY date DESC""",
        conn
    )

    conn.close()

    return df


def get_finance_summary() -> dict:

    df = load_transactions_df()
    if df.empty:
        return {
            "total_income": 0,
            "total_expense": 0,
            "balance": 0,
            "transaction_count": 0
        }
    
    total_income = df[df['type'] == "income"]["amount"].sum()
    total_expense = df[df['type'] == "expense"]["amount"].sum()
    balance = total_income - total_expense

    return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "transaction_count": len(df)
        }

def get_expense_by_category() -> pd.DataFrame:
    
    df = load_transactions_df()
    if df.empty:
        return pd.DataFrame(columns=['category', 'amount'])
    
    expense_df = df[df['type'] == 'expense']

    if expense_df.empty:
        return pd.DataFrame(columns=['category', 'amount'])
    
    result = (
        expense_df
        .groupby('category', as_index=False)['amount']
        .sum()
        .sort_values("amount", ascending=False)
    )


    return result

