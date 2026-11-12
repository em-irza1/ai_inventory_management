
# Stockwise — AI-Powered Inventory Management

A beginner-friendly Flask inventory app with OOP, JSON storage, responsive HTML/CSS/JavaScript, and optional Groq-powered inventory intelligence. The interface uses a dark maroon and warm beige palette.

## Features

- Product CRUD: add, view, edit and delete products.
- Search by product name, ID or category.
- `Product` and inherited `PerishableProduct` classes.
- Dashboard totals: product count, units, inventory value, low stock and out-of-stock.
- AI inventory analysis, reorder suggestions, natural-language assistant and description generation.
- AI is optional: normal inventory features work without a Groq key.
- Input validation and graceful API error messages.

## Requirements

- Python 3.10+
- A Groq API key only if you want to use AI features.

## Run locally (Windows PowerShell)

1. Extract the project ZIP and open the extracted `ai_inventory_management` folder in VS Code.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Create your private environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

   Open `.env` and replace `your_groq_api_key_here` with your own key. Keep the key private. You can leave the placeholder if you only want to use inventory features.

5. Start the app:

   ```powershell
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

If PowerShell blocks environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

## Groq configuration

The `.env` file supports:

```env
GROQ_API_KEY=your_private_key
GROQ_MODEL=llama-3.3-70b-versatile
FLASK_DEBUG=false
```

You may change `GROQ_MODEL` to a model currently available to your Groq account. Never paste a real API key into source code, screenshots, GitHub, or chat messages.

## Project structure

```text
ai_inventory_management/
├── app.py
├── models.py
├── inventory.py
├── ai_helper.py
├── requirements.txt
├── .env.example
├── .gitignore
├── vercel.json
├── README.md
├── data/
│   └── products.json
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## GitHub upload (VS Code)

1. Create an empty repository on GitHub (do not add a README if you already have this one).
2. Open this project folder in VS Code.
3. Confirm `.env` is not in the Source Control changes. `.gitignore` excludes it.
4. In Source Control, stage the project files, enter a message such as `Initial inventory management app`, and click Commit.
5. Choose **Publish Branch** or add your GitHub repository as the remote and push.

Command-line alternative:

```powershell
git init
git add .
git status
git commit -m "Initial inventory management app"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the repository URL with your own. Never use `git add .env`.

## Vercel deployment

1. Push the project to GitHub.
2. In Vercel, import the repository.
3. Add `GROQ_API_KEY` and `GROQ_MODEL` in **Project Settings → Environment Variables** (AI features only).
4. Deploy. The included `vercel.json` routes requests to the Flask app.

### Important storage note

The starter version deliberately uses `data/products.json` so it is easy to understand and run locally. Vercel functions use an ephemeral/read-only deployment filesystem; changes written to the JSON file are **not durable** and may disappear between function invocations or deployments. Use a persistent hosted database (for example PostgreSQL/Supabase) before using this as a real multi-user production inventory system. The current JSON adapter is a learning/demo implementation, not a production database.

## API routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/products` | List products; optional `?q=` search |
| POST | `/api/products` | Add product |
| PUT | `/api/products/<id>` | Update product |
| DELETE | `/api/products/<id>` | Delete product |
| POST | `/api/ai/analyze` | AI inventory analysis |
| POST | `/api/ai/reorder` | AI reorder suggestions |
| POST | `/api/ai/ask` | Ask inventory question |
| POST | `/api/ai/description` | Generate product description |
| GET | `/api/health` | Health/configuration check |

## Notes

- Currency labels are shown as PKR; change the `money()` function in `static/app.js` if you need another currency.
- Reorder suggestions are advisory estimates. Reliable demand planning requires sales history, supplier lead times and target service levels.
- Add authentication, role permissions, audit logs, database migrations, backups and request throttling before exposing this app to real business users.
