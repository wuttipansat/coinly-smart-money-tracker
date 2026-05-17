import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px


from src.supabase_database import (
    create_table,
    remove_all_transactions,
    delete_transaction,
    update_transaction,
    add_transaction
)

from src.transaction_service import save_transaction

from src.llm_parser import parse_transaction

from src.report_service import (
    load_transactions_df,
    get_finance_summary,
    get_expense_by_category
)

from src.config import (
    get_transaction_type_options,
    get_category_options
)

from src.auth_service import (
    init_auth_state,
    register_user,
    login_user,
    logout_user
)

st.set_page_config(
    page_title="Coinly",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="collapsed"
)



st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
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
        border-radius: 15px !important;
    }

    input {
        border-radius: 15px !important;
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

def normalize_type(value: str) -> str:
    type_options = get_transaction_type_options()

    value = str(value).lower().strip()

    if value in type_options:
        return value

    return type_options[0]

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

def prepare_analytics_df(df):
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    df = df.dropna(subset=["date"])

    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["day"] = df["date"].dt.date

    return df

init_auth_state()


def show_auth_page():
    st.title("🪙 Coinly")
    st.caption("Smart Personal Money Tracker")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if submitted:
            try:
                success, message = login_user(email, password)

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

            except Exception as e:
                st.error("Login failed.")
                st.exception(e)

    with register_tab:
        with st.form("register_form"):
            email = st.text_input("Email", key="register_email")
            password = st.text_input(
                "Password",
                type="password",
                key="register_password"
            )

            submitted = st.form_submit_button(
                "Create account",
                use_container_width=True
            )

        if submitted:
            try:
                success, message = register_user(email, password)

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.warning(message)

            except Exception as e:
                st.error("Registration failed.")
                st.exception(e)


if not st.session_state.authenticated:
    show_auth_page()
    st.stop()


user_id = st.session_state.user["id"]
create_table()

with st.sidebar:
    st.title("🪙 Coinly")
    st.caption("Smart Personal Money Tracker")

    st.caption(f"Logged in as {st.session_state.user['email']}")

    if st.button("Logout", use_container_width=True):
        logout_user()

    page = st.radio(
        "Navigation",
        ["Home", "Analytics", "History", "Settings"]
    )



st.title("🪙 Coinly")
st.caption("Smart Personal Money Tracker")
st.divider()


if "editing_transaction_id" not in st.session_state:
    st.session_state.editing_transaction_id = None

if "pending_transaction" not in st.session_state:
    st.session_state.pending_transaction = None

if page == "Home":
    summary = get_finance_summary(user_id)

    st.metric("Total Income", f"฿{summary['total_income']:,.2f}")
    st.metric("Total Expense", f"฿{summary['total_expense']:,.2f}")
    st.metric("Balance", f"฿{summary['balance']:,.2f}")

    st.divider()

    st.markdown("### Spending")

    expense_by_cat = get_expense_by_category(user_id)

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
                    transaction = parse_transaction(user_text)

                st.session_state.pending_transaction = {
                    "date": transaction.date,
                    "type": transaction.type,
                    "category": transaction.category,
                    "amount": transaction.amount,
                    "note": transaction.note,
                }

                st.rerun()

            except Exception as e:
                st.error("Cannot process transaction.")
                st.exception(e)
    
    if st.session_state.pending_transaction is not None:
        pending = st.session_state.pending_transaction

        with st.container(border=True):
            st.markdown("### Preview Transaction")

            with st.form("confirm_transaction_form"):
                edited_date = st.date_input(
                    "Date",
                    value=str(pending['date'])
                )

                type_options = get_transaction_type_options()

                edited_type = st.selectbox(
                    "Type",
                    type_options,
                    index=type_options.index(normalize_type(pending["type"]))
                )

                category_options = get_category_options(edited_type)

                original_category = str(pending["category"]).lower().strip()

                default_category = (
                    original_category
                    if original_category in category_options
                    else "other"
                    if "other" in category_options
                    else category_options[0]
                )

                edited_category = st.selectbox(
                    "Category",
                    category_options,
                    index=category_options.index(default_category)
                )

                edited_amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    value=float(pending['amount']),
                    step=1.0
                )

                edited_note = st.text_input(
                    "Note",
                    value=str(pending['note'])
                )

                save_col, cancel_col = st.columns(2)

                with save_col:
                    save_button = st.form_submit_button(
                        "✔",
                        use_container_width=True
                    )
                with cancel_col:
                    cancel_button = st.form_submit_button(
                        "✘",
                        use_container_width=True
                    )

                if save_button:
                    add_transaction(
                        user_id=user_id,
                        date=edited_date.isoformat() if hasattr(edited_date, "isoformat") else edited_date,
                        type_=edited_type,
                        category=edited_category,
                        amount=edited_amount,
                        note=edited_note
                    )

                    st.cache_data.clear()

                    st.session_state.pending_transaction = None
                    st.success("Transaction saved successfully!")
                    st.rerun()

                if cancel_button:
                    st.session_state.pending_transaction = None
                    st.rerun()

elif page == "Analytics":
    st.subheader("Dashboard Analytics")
    
    transaction_df = load_transactions_df(user_id)

    if transaction_df.empty:
        st.info("No transaction data yet.")

    else:
        transaction_df = prepare_analytics_df(transaction_df)

        if transaction_df.empty:
            st.warning("No valid date data found.")

        else:
            month_options = ['all'] + sorted(transaction_df['month'].unique().tolist())

            selected_month = st.selectbox(
                "Select month",
                month_options
            )

            if selected_month != 'all':
                filtered_df = transaction_df[
                    transaction_df['month'] == selected_month
                ]

            else:
                filtered_df = transaction_df.copy()

            income_df = filtered_df[filtered_df['type'] == 'income']
            expense_df = filtered_df[filtered_df['type'] == 'expense']

            total_income = income_df['amount'].sum()
            total_expense = expense_df['amount'].sum()
            balance = total_income - total_expense
            transaction_count = len(filtered_df)

            metric_col1, metric_col2 = st.columns(2)

            with metric_col1:
                st.metric("Income", f"฿{total_income:,.2f}")
                st.metric("Balance", f"฿{balance:,.2f}")

            with metric_col2:
                st.metric("Expense", f"฿{total_expense:,.2f}")
                st.metric("Transactions", transaction_count)

            st.divider()     

            monthly_summary = (
                transaction_df
                .groupby(['month', 'type'], as_index=False)['amount']
                .sum()
            )

            fig_monthly = px.bar(
                monthly_summary,
                x="month",
                y="amount",
                color="type",
                barmode="group",
                text_auto=".2s"
            )

            fig_monthly.update_layout(
                height=330,
                margin=dict(t=20, b=20, l=10, r=10),
                xaxis_title="Month",
                yaxis_title="Amount"
            )

            st.plotly_chart(fig_monthly, use_container_width=True)

            st.divider()

            st.markdown("### Daily Expense Trend")

            daily_expense = (
                expense_df
                .groupby("day", as_index=False)["amount"]
                .sum()
            )

            if daily_expense.empty:
                st.info("No expense data for this period.")

            else:
                fig_daily = px.line(
                    daily_expense,
                    x="day",
                    y="amount",
                    markers=True
                )

                fig_daily.update_layout(
                    height=300,
                    margin=dict(t=20, b=20, l=10, r=10),
                    xaxis_title="Date",
                    yaxis_title="Expense"
                )

                st.plotly_chart(fig_daily, use_container_width=True)

            st.divider()

            st.markdown("### Expense by Category")

            expense_by_category = (
                expense_df
                .groupby("category", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
            )

            if expense_by_category.empty:
                st.info("No expense category data for this period.")

            else:
                fig_category = px.bar(
                    expense_by_category,
                    x="amount",
                    y="category",
                    orientation="h",
                    text_auto=".2s"
                )

                fig_category.update_layout(
                    height=350,
                    margin=dict(t=20, b=20, l=10, r=10),
                    xaxis_title="Amount",
                    yaxis_title="Category",
                    yaxis=dict(autorange="reversed")
                )

                st.plotly_chart(fig_category, use_container_width=True)

            st.divider()

            st.markdown("### Top Spending Categories")

            if expense_by_category.empty:
                st.info("No spending data yet.")

            else:
                top_categories = expense_by_category.head(5)

                for _, row in top_categories.iterrows():
                    percent = (
                        row["amount"] / total_expense * 100
                        if total_expense > 0
                        else 0
                    )

                    st.write(
                        f"**{row['category']}** — ฿{row['amount']:,.2f} "
                        f"({percent:.1f}%)"
                    )

                    st.progress(percent / 100)

elif page == "History":
    st.subheader("Transaction History")

    transaction_df = load_transactions_df(user_id)

    if transaction_df.empty:
        st.info("No transaction data yet.")

    else:

        transaction_df['date_parsed'] = pd.to_datetime(
            transaction_df["date"],
            errors='coerce'
        )

        st.markdown("### Filters")

        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            type_options = ['all'] + sorted(
                transaction_df['type'].dropna().unique().tolist()
            )

            selected_type = st.selectbox(
                "Type",
                type_options
            )

        with filter_col2:
            category_options = ['all'] + sorted(
                transaction_df['category'].dropna().unique().tolist()
            )

            selected_category = st.selectbox(
                "Category",
                category_options
            )

        search_text = st.text_input(
            "Search note/category",
            placeholder="Example: coffee, salary, rent"
        )

        valid_dates = transaction_df['date_parsed'].dropna()

        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            selected_date_range = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

        else:
            selected_date_range = None

        
        filtered_df = transaction_df.copy()

        if selected_type != 'all':
            filtered_df = filtered_df[filtered_df['type'] == selected_type]

        if selected_category != 'all':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]

        if search_text.strip():
            keyword = search_text.lower().strip()

            filtered_df = filtered_df[
                filtered_df['note'].astype(str).str.lower().str.contains(keyword)
                | filtered_df['category'].astype(str).str.lower().str.contains(keyword)
                | filtered_df['type'].astype(str).str.lower().str.contains(keyword)
            ]

        if selected_date_range and len(selected_date_range) == 2:
            start_date, end_date = selected_date_range

            filtered_df = filtered_df[
                (filtered_df['date_parsed'].dt.date >= start_date)
                & (filtered_df['date_parsed'].dt.date <= end_date)
            ]

        st.caption(f"Showing {len(filtered_df)} of {len(transaction_df)} transactions")

        if filtered_df.empty:
            st.info("No transactions match your filters.")
        else:
            for _, row in filtered_df.iterrows():
                with st.container(border=True):
                    st.markdown(
                        f"""
                        **{row['category']}** · {row['type']}  
                        ฿{row['amount']:,.2f} · {row['date']}  
                        {row['note']}
                        """
                    )

                    edit_col, delete_col = st.columns(2)

                    with edit_col:
                        if st.button("✎", key=f"edit_{row['id']}", use_container_width=True):
                            st.session_state.editing_transaction_id = selected_date_range(row['id'])
                            st.rerun()
                    
                    with delete_col:
                        if st.button("🗑", key=f"delete_{row['id']}", use_container_width=True ):
                            delete_transaction(user_id, int(row['id']))
                            st.cache_data.clear()
                            st.success("Transaction deleted.")
                            st.rerun()
                if st.session_state.editing_transaction_id == str(row["id"]):

                    with st.form(key=f"edit_form_{row['id']}"):
                        new_date = st.text_input("Date", value=str(row["date"]))

                        new_type = st.selectbox(
                            "Type",
                            ["income", "expense"],
                            index=["income", "expense"].index(row["type"])
                        )

                        new_category = st.text_input("Category", value=str(row["category"]))

                        new_amount = st.number_input(
                            "Amount",
                            min_value=0.0,
                            value=float(row["amount"]),
                            step=1.0
                        )

                        new_note = st.text_input("Note", value=str(row["note"]))

                        save_button = st.form_submit_button("Save changes", use_container_width=True)
                        cancel_button = st.form_submit_button("Cancel", use_container_width=True)

                        if save_button:
                            update_transaction(
                                user_id=user_id,
                                transaction_id=int(row['id']),
                                date=new_date,
                                type_=new_type,
                                category=new_category,
                                amount=new_amount,
                                note=new_note
                            )

                            st.cache_data.clear()

                            st.session_state.editing_transaction_id = None
                            st.success("Transaction updated.")
                            st.rerun()

                        if cancel_button:
                            st.session_state.editing_transaction_id = None
                            st.rerun()


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
            remove_all_transactions(user_id, reset_id=True)
            st.cache_data.clear()
            st.success("All transactions removed.")
            st.rerun()
        else:
            st.error("Please type DELETE exactly.")