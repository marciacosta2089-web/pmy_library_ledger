# My Library Ledger

A personal library tracker built with Streamlit and SQLite.

## Features

- Track books across 5 statuses: Owned, Wishlist, Suggested, Borrowed, Lent
- Search and filter your library
- Quick actions to change book status
- Basic statistics dashboard

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
Install dependencies:
pip install -r requirements.txt
Run the app:
streamlit run app.py
Open your browser at http://localhost:8501
Data
The SQLite database (library.db) is created automatically in the project folder on first run.


---