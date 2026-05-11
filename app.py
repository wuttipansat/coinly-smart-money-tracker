import streamlit as st
import plotly.graph_objects as go

from src.database import create_table, remove_all_transactions
from src.transaction_service import save_transaction
from src.report_service import (
    load_transactions_df,
    get_finance_summary,
    get_expense_by_category
)


st.set_page_config(
    page_title="Coinly",
    page_icon="🪙",
    layout="centered",
    initial_sidebar_state="collapsed"
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 2rem;
        max-width: 520px;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3rem;
        font-size: 1rem;
        font-weight: 600;
    }

    div[data-testid="stMetric"] {
        background-color: #f7f7f7;
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #e5e5e5;
    }

    textarea {
        border-radius: 12px !important;
    }

    input {
        border-radius: 12px !important;
    }

    
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    div.stButton > button {
        width: 100%;
        height: 2.8rem;
        border-radius: 12px;
        font-size: 1.2rem;
        font-weight: 600;
    }

    div[data-testid="stTextInput"] input {
        height: 2.8rem;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def pie_chart(df):
    total = df["amount"].sum()

    labels = df["category"].tolist() + [""]
    values = df["amount"].tolist() + [total]

    percentages = (df["amount"] / total * 100).tolist()

    text_labels = [
        f"{percent:.1f}%"
        for percent in percentages
    ] + [""]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                rotation=270,
                direction="clockwise",
                sort=False,
                text=text_labels,
                textinfo="text",
                hovertemplate="%{label}<br>Amount: ฿%{value:,.2f}<extra></extra>",
                marker=dict(
                    colors=[
                        None for _ in df["category"]
                    ] + ["rgba(0,0,0,0)"]
                )
            )
        ]
    )

    fig.update_traces(
        showlegend=True,
        textposition="inside"
    )

    fig.update_layout(
        height=320,
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )

    return fig


create_table()


with st.sidebar:
    st.title("🪙 Coinly")
    st.caption("Smart Personal Money Tracker")

    page = st.radio(
        "Navigation",
        ["Home", "History", "Settings"]
    )

    st.divider()
    st.caption("Powered by LangChain")
    st.caption("Developed by Wuttipan Satienpaisan")



st.title("🪙 Coinly")
st.caption("Smart Personal Money Tracker")
st.divider()


if page == "Home":
    summary = get_finance_summary()

    st.metric("Total Income", f"฿{summary['total_income']:,.2f}")
    st.metric("Total Expense", f"฿{summary['total_expense']:,.2f}")
    st.metric("Balance", f"฿{summary['balance']:,.2f}")

    st.divider()

    st.markdown("### Spending")

    expense_by_cat = get_expense_by_category()

    if expense_by_cat.empty:
        st.info("No expense data yet.")
    else:
        fig = pie_chart(expense_by_cat)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    st.markdown("### Add Transaction")

    with st.form("add_transaction_form", clear_on_submit=True):
        col_input, col_button = st.columns(
            [8, 1],
            gap="small",
            vertical_alignment="bottom"
        )

        with col_input:
            user_text = st.text_input(
                "Transaction",
                placeholder="Example: จ่ายค่าอาหาร 300 บาท",
                label_visibility="collapsed"
            )

        with col_button:
            submitted = st.form_submit_button(
                "➜",
                use_container_width=True
            )
    
    if submitted:
        if user_text.strip() == "":
            st.warning("Please enter a transaction.")
        else:
            try:
                with st.spinner("Processing transaction..."):
                    transaction = save_transaction(user_text)
                
                st.success("Transaction saved successfully!")

                st.markdown("### Extracted Result")
                st.write(f"**Date:** {transaction.date}")
                st.write(f"**Type:** {transaction.type}")
                st.write(f"**Category:** {transaction.category}")
                st.write(f"**Amount:** ฿{transaction.amount:,.2f}")
                st.write(f"**Note:** {transaction.note}")
                st.rerun()
            except Exception as e:
                st.error("Cannot save transaction.")
                st.exception(e)


elif page == "History":
    st.subheader("Transaction History")

    transaction_df = load_transactions_df()

    if transaction_df.empty:
        st.info("No transaction data yet.")
    else:
        transaction_type = st.selectbox(
            "Filter by type",
            ["all", "income", "expense"]
        )

        if transaction_type != "all":
            transaction_df = transaction_df[
                transaction_df["type"] == transaction_type
            ]

        st.dataframe(
            transaction_df,
            use_container_width=True,
            hide_index=True
        )


elif page == "Settings":
    st.subheader("Settings")

    st.warning("Danger Zone")

    with st.form("remove_all_form"):
        confirm_text = st.text_input(
            "Type DELETE to remove all transactions"
        )

        submitted = st.form_submit_button("Remove All Transactions")

    if submitted:
        if confirm_text == "DELETE":
            remove_all_transactions(reset_id=True)
            st.success("All transactions removed.")
            st.rerun()
        else:
            st.error("Please type DELETE exactly.")