# 🪙 Coinly

Coinly is a smart income-expense tracker built with **Python**, **Streamlit**, **SQLite** and **LangChain**.
Users can add transactions using natural language.

![Image alt](https://github.com/wuttipansat/coinly-smart-money-tracker/blob/c5d3ae9b6a364edc4b5be88b712269e7e3b306df/snapshot1.png)

Example
```text
จ่ายค่าอาหาร 300 บาท
paid 120 baht for coffee
ได้รับเงินเดือน 30000 บาท
```

## Features
* Add income/expense using natural language
* Auto-detect type, category, amount, date, and note
* Store data in SQLite
* View total income, expense, and balance
* View transaction history
* Streamlit-based web application

## Getting Started
### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create Environment
Create ```.env``` file:

```env
OPENAI_API_KEY=your_api_key_here
```

### Run app
```bash
streamlit run app.py
```

## Future Improvements
- Edit transaction
- Delete a transaction
- Data filter
- Monthly report
- Export CSV
- Budget alert

## Author
Developed by Wuttipan Satienpaisan
