from typing import TypedDict, Optional
from datetime import date, datetime

from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

from src.config import format_categories_for_prompt, load_categories, get_transaction_type_options

class Transaction(BaseModel):
    date: str = Field(description="Transaction date in YYYY-MM-DD format")
    type: str = Field(description="Transaction type")
    category: str = Field(description="Transaction category")
    amount: float = Field(description="Transaction amount")
    note: str = Field(description="Short transaction note")

class ParserState(TypedDict):
    user_text: str
    categories_prompt: str
    transaction: Optional[Transaction]
    is_valid: bool
    error: Optional[str]

def parse_date(value: str) -> bool:
    try:
        datetime.strptime(str(value), "%Y-%m-%d")
        return True
    except ValueError:
        return False
    
def parse_transaction_node(state: ParserState) -> ParserState:
    model = ChatOpenAI(
        model="gpt-5.4-mini",
        temperature=0
    )

    structure_model = model.with_structured_output(Transaction)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a financial transaction parser for a personal money tracker app.

Extract exactly one transaction from the user text.

Rules:
- Date must be YYYY-MM-DD
- Type must match one of the allowed transaction types.
- Category must match one of the allowed categories.
- Amount must be a number greater than 0.
- Note should be short and clear.
- If the user writes in Thai, keep the note in Thai.
- Do not invent unrelated information.

Allowed transaction types and categories:
{categories_prompt}


"""
            ),
            ("human", "{user_text}")
        ]
    )
    
    chain = prompt | structure_model

    transaction = chain.invoke(
        {
            "user_text": state["user_text"],
            "categories_prompt": state["categories_prompt"]
        }
    )

    return {
        **state,
        "transaction": transaction,
        "is_valid": False,
        "error": None
    }

def validate_transaction_node(state: ParserState) -> ParserState:
    transaction = state['transaction']

    if transaction is None:
        return {
            **state,
            "is_valid": False,
            "error": "No transaction was parsed."
        }
    
    type_options = get_transaction_type_options()
    categories = load_categories()

    transaction_type = str(transaction.type).lower().strip()
    category = str(transaction.category).lower().strip()

    if transaction_type not in type_options:
        return {
            **state,
            "is_valid": False,
            "error": f"Invalid transaction type: {transaction.type}"
        }
    
    category_options = list(categories[transaction.type].keys())

    if category not in category_options:
        return {
            **state,
            "is_valid": False,
            "error": f"Invalid category: {transaction.category}"
        }
    
    if not parse_date(transaction.date):
        return {
            **state,
            "is_valid": False,
            "error": f"Invalid date format: {transaction.date}"
        }
    
    cleaned_transaction = Transaction(
        date=transaction.date,
        type=transaction_type,
        category=category,
        amount=transaction.amount,
        note=transaction.note
    )

    return {
        **state,
        "transaction": cleaned_transaction,
        "is_valid": True,
        "error": None
    }

def repair_transaction_node(state: ParserState) -> ParserState:
    transaction = state['transaction']

    if transaction is None:
        return state
    
    type_options = get_transaction_type_options()
    categories = load_categories()

    transaction_type = str(transaction.type).lower().strip()

    if transaction_type not in type_options:
        transaction_type = "expense" if "expense" in type_options else type_options[0]

    category_options = list(categories[transaction_type].keys())
    category = str(transaction.category).lower().strip()

    if category not in category_options:
        category = "other" if "other" in category_options else category_options[0]

    transaction_date = transaction.date
    
    if not parse_date(transaction_date):
        transaction_date = date.today().isoformat()

    amount = transaction.amount

    if amount <= 0:
        amount = 1.0

    repaired_transaction = Transaction(
        date=transaction_date,
        type=transaction_type,
        category=category,
        amount=amount,
        note=transaction.note
    )

    return {
        **state,
        "transaction": repaired_transaction,
        "is_valid": False,
        "error": None
    }


def route_after_validation(state: ParserState) -> ParserState:
    if state['is_valid']:
        return 'end'
    return 'repair'

def build_transaction_parser_graph():
    graph = StateGraph(ParserState)
    
    graph.add_node("parse", parse_transaction_node)
    graph.add_node("validate", validate_transaction_node)
    graph.add_node("repair", repair_transaction_node)

    graph.add_edge(START, "parse")
    graph.add_edge("parse", "validate")

    graph.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "end": END,
            "repair": "repair"
        }
    )

    graph.add_edge("repair", "validate")

    return graph.compile()

transaction_parser_graph = build_transaction_parser_graph()

def parse_transaction(user_text: str) -> Transaction:
    initial_state: ParserState = {
        "user_text": user_text,
        "categories_prompt": format_categories_for_prompt(),
        "transaction": None,
        "is_valid": False,
        "error": None
    }

    result = transaction_parser_graph.invoke(initial_state)

    if not result["is_valid"]:
        raise ValueError(result["error"] or "Transaction parsing failed.")
    
    return result["transaction"]