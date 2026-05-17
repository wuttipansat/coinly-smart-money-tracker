# 🪙 Coinly

Coinly is a smart personal tracker built with **Streamlit**, **Supabase**, and **LangChain/OpenAI**.
It helps users record income and expenses using natural language, confirm AI-parsed results, and analyze personal
spending.

![Image alt](https://github.com/wuttipansat/coinly-smart-money-tracker/blob/c5d3ae9b6a364edc4b5be88b712269e7e3b306df/snapshot1.png)

Example
```text
จ่ายค่าอาหาร 300 บาท
paid 120 baht for coffee
ได้รับเงินเดือน 30000 บาท
```

## Features

- User authentication with Supabase Auth
- Natural-language transaction input
- AI transaction parsing with editable confirmation
- CRUD process
- Dashboard analytics
- Supabase PostgreSQL cloud database
- Mobile-friendly Streamlit layout

## Tech Stack

- Python
- Streamlit
- Supabase
- PostgreSQL
- LangChain
- OpenAI API
- Pandas
- Plotly
- PyYAML

## Getting Started
### Repo Cloning & Virtual Environment Initiation

```bash
git clone https://github.com/wuttipansat/coinly-smart-money-tracker.git
cd coinly-smart-money-tracker
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create ```.env``` file:

```env
OPENAI_API_KEY=your_api_key_here
```

Create ```.streamlit/secrets.toml``` file:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_ANON_KEY = "your-supabase-anon-or-publishable-key"
```

### Supabase Setup

Create a `transactions` table in Supabase SQL Editor:

```sql
create table if not exists transactions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    date date not null,
    type text not null check (type in ('income', 'expense')),
    category text not null,
    amount numeric not null check (amount >= 0),
    note text,
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone
);

alter table transactions enable row level security;

create policy "Users can select own transactions"
on transactions
for select
to authenticated
using ((select auth.uid()) = user_id);

create policy "Users can insert own transactions"
on transactions
for insert
to authenticated
with check ((select auth.uid()) = user_id);

create policy "Users can update own transactions"
on transactions
for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

create policy "Users can delete own transactions"
on transactions
for delete
to authenticated
using ((select auth.uid()) = user_id);
```

### Run app
```bash
streamlit run app.py
```

## Future Improvements

- Manual input mode
- CSV export
- Budget tracking
- Recurring transactions
- AI financial insights
- **LangGraph Improvement**
- **Mobile app version**

## Author
Developed by Wuttipan Satienpaisan
