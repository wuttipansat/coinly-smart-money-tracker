from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config.yaml"

def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding='utf-8') as file:
        config = yaml.safe_load(file)

    return config
    
def load_categories() -> dict:
    config = load_config()
    return config['categories']

def get_all_category_names() -> list[str]:
    categories = load_categories()
    income_categories = list(categories['income'].keys())
    expense_categories = list(categories['expense'].keys())

    return income_categories + expense_categories

def format_categories_for_prompt() -> str:
    categories = load_categories()

    lines = []

    lines.append("Income categories:")
    for name, description in categories['income'].items():
        lines.append(f"- {name}: {description}")

    lines.append("")
    lines.append("Expense categories:")
    for name, description in categories['expense'].items():
        lines.append(f"- {name}: {description}")

    
    return "\n".join(lines)

