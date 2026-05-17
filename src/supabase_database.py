import streamlit as st

from src.supabase_client import get_supabase


def create_table():
    """
    Supabase table is created manually in SQL Editor.
    Keep this function for compatibility with app.py.
    """
    pass


def add_transaction(user_id, date, type_, category, amount, note=""):
    supabase = get_supabase()

    data = {
        "user_id": str(user_id),
        "date": str(date),
        "type": str(type_),
        "category": str(category),
        "amount": float(amount),
        "note": str(note),
    }

    supabase.table("transactions").insert(data).execute()


def get_all_transactions(user_id):
    supabase = get_supabase()

    response = (
        supabase
        .table("transactions")
        .select("id,date,type,category,amount,note")
        .eq("user_id", str(user_id))
        .order("date", desc=True)
        .execute()
    )

    rows = []

    for row in response.data:
        rows.append(
            (
                str(row["id"]),
                row.get("date", ""),
                row.get("type", ""),
                row.get("category", ""),
                float(row.get("amount", 0)),
                row.get("note", ""),
            )
        )

    return rows


def update_transaction(user_id, transaction_id, date, type_, category, amount, note):
    supabase = get_supabase()

    data = {
        "date": str(date),
        "type": str(type_),
        "category": str(category),
        "amount": float(amount),
        "note": str(note),
    }

    (
        supabase
        .table("transactions")
        .update(data)
        .eq("id", str(transaction_id))
        .eq("user_id", str(user_id))
        .execute()
    )


def delete_transaction(user_id, transaction_id):
    supabase = get_supabase()

    (
        supabase
        .table("transactions")
        .delete()
        .eq("id", str(transaction_id))
        .eq("user_id", str(user_id))
        .execute()
    )


def remove_all_transactions(user_id, reset_id: bool = True):
    supabase = get_supabase()

    (
        supabase
        .table("transactions")
        .delete()
        .eq("user_id", str(user_id))
        .execute()
    )