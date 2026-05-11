from datetime import date
from typing import Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, field_validator, model_validator

from src.config import load_categories, get_all_category_names, format_categories_for_prompt

load_dotenv()

ALL_CATEGORIES = get_all_category_names()
CATEGORY_TEXT = format_categories_for_prompt()

CATEGORY_TYPE = Literal.__getitem__(tuple(ALL_CATEGORIES))

class Transaction(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    type: Literal['income', 'expense'] = Field(description="Transaction type")
    category: str = Field(description='Exact transaction category from config')
    amount: float = Field(description="Amount of money")
    note: str = Field(description="Short note")

    @field_validator("category")
    @classmethod
    def validate_category(cls, value):
        if value not in ALL_CATEGORIES:
            raise ValueError(f"Invalid category: {value}")
        return value
    
    @model_validator(mode='after')
    def check_category_matches_type(self):
        categories = load_categories()
        income_categories = set(categories['income'].keys())
        expense_categories = set(categories['expense'].keys())

        if self.type == 'income' and self.category not in income_categories:
            raise ValueError("Income transaction must use an income category.")
        
        if self.type == 'expense' and self.category not in expense_categories:
            raise ValueError("Expense transaction must use an expense category.")
        
        return self
        

def parse_transaction(user_text: str) -> Transaction:
    today = date.today().isoformat()

    model = ChatOpenAI(
        model="gpt-5.4-mini",
        temperature=0
    )

    structured_model = model.with_structured_output(Transaction, method='function_calling')

    prompt = f"""
    You are an income-expense transaction extractor.

    Today's date is {today}

    Extract exactly one transaction from the user's text.

    User text:

    {user_text}

    You must classify the transaction into exactly one category.

    Available categories:
    {CATEGORY_TEXT}

    Rules:
    - If the user spent, paid, bought, used money, classify as expense.
    - If the user received, got salary, earned money, classify as income.
    - Use YYYY-MM-DD date format.
    - If no date is mentioned, use today's date.
    - Category must be exactly one from the config category list.
    - Do not create a new category.
    - Amount must be numeric.
    - Note should be short.
    """

    result = structured_model.invoke(prompt)

    return result
