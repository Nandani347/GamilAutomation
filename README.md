# 📧 Gmail Automation Pipeline

> An automated system that connects with Gmail, processes incoming emails & attachments, and integrates with external services like Supabase and LLMs for intelligent escalation and response.

---

## ✨ Features

- 🔁 **Real-time Email Monitoring** – Polls Gmail every 3 seconds for new emails from specified users
- 📎 **Attachment Processing** – Handles common file types including:
  - 🖼️ Images (JPG, PNG, etc.)
  - 📄 PDFs
  - 📊 Excel / CSV files
- 🧠 **LLM Integration** – Ready for LLM-based content analysis and automated escalation logic
- 🗂️ **Supabase Integration** – Store and manage email data and attachments
- 🔐 **OAuth 2.0 Authentication** – Secure authentication with Google's Gmail API
- 📝 **Structured Logging** – Comprehensive activity logging to console and log files

---

## 🏗️ Project Structure

```
GmailAutomation/
├── GmailAutomation/
│   ├── InsertionPipeline/
│   ├── LLM/
│   ├── RetrievalPipeline/
│   ├── auth.py
│   ├── db.py
│   └── ...
├── demo.py               # Main entry point
├── logger.py             # Central logging
├── pyproject.toml        # Dependencies & project config
├── credentials.json      # ⚠️ OAuth credentials (DO NOT COMMIT)
├── token.json            # ⚠️ OAuth token (DO NOT COMMIT)
├── README.md             # 📄 You are here!
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Gmail account with API access
- `uv` for Python package management (recommended)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Nandani347/GamilAutomation.git
cd GamilAutomation
```

### 2️⃣ Install Dependencies

Install project dependencies (uv automatically creates and manages a virtual environment):

```bash
uv sync
```

Or using traditional pip:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🔐 Gmail API Setup

There are several steps required to use the Gmail API. This guide is based on the current API configuration as of October 2, 2025. Steps may change in the future.

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown → **"New Project"**
3. Enter a project name (e.g., "Gmail Automation")
4. Click **"Create"** and select the project once created

### Step 2: Enable the Gmail API

1. Go to **"APIs & Services"** > **"Library"**
2. Search for **"Gmail API"** and click **"Enable"**

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** > **"OAuth consent screen"**
2. Fill in required application info:
   - **App name**: "Gmail Automation"
   - **User support email**: Your email
   - **Audience**: External (unless using Google Workspace)
3. Click **"Save and Continue"** → **"Create"**

### Step 4: Create OAuth Credentials

1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Choose **"Desktop app"** and give it a name (e.g., "Gmail Desktop Client")
4. Click **"Create"**
5. Download the JSON file and save it as `credentials.json` in the project root

> ⚠️ **Important**: Never commit `credentials.json` or `token.json` to Git! Ensure they're listed in your `.gitignore` file.

### Step 5: Add Required Scopes

1. Go to **"APIs & Services"** > **"OAuth consent screen"** → **"Data Access"**
2. Add the scope: `.../auth/gmail.modify` (read, compose, and send emails)
3. Click **"Update"** → **"Save"**

**Verify Setup**: Check usage metrics at:
https://console.cloud.google.com/apis/api/gmail.googleapis.com/metrics

---

## 🚦 Usage

### Run the Automation

Start the Gmail automation script to begin monitoring for new emails:

```bash
uv run python demo.py
```

The system will:

- ✅ Poll Gmail every 3 seconds
- ✅ Process new emails from configured users
- ✅ Extract and process attachments
- ✅ Store data temporarily for LLM processing
- ✅ Log all activity to console and log files

### Expected Output

```
[INFO] Polling Gmail...
[INFO] Found 2 new emails
[INFO] Processing attachment: invoice.pdf
[INFO] Email processed successfully
```

---

## ⚙️ Configuration

### Environment Variables

You can control various settings through environment variables (recommended via a `.env` file):

| Variable                      | Description                                      | Default            |
| ----------------------------- | ------------------------------------------------ | ------------------ |
| `MCP_GMAIL_CREDENTIALS_PATH`  | Path to credentials.json                         | "credentials.json" |
| `MCP_GMAIL_TOKEN_PATH`        | Path to store OAuth token                        | "token.json"       |
| `SUPABASE_URL`                | URL of your Supabase instance                    | -                  |
| `SUPABASE_KEY`                | API key for Supabase                             | -                  |
| `POLL_INTERVAL`               | Interval in seconds for polling Gmail            | 3                  |
| `LOG_LEVEL`                   | Logging level (`INFO`, `DEBUG`, `ERROR`)         | INFO               |

### Example `.env` File

```env
MCP_GMAIL_CREDENTIALS_PATH=credentials.json
MCP_GMAIL_TOKEN_PATH=token.json
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=YOUR_KEY_HERE
POLL_INTERVAL=3
LOG_LEVEL=INFO
```

---

## 🧪 Development

### Linting and Testing

```bash
# Format code
uv run ruff format .

# Lint code with auto-fixes
uv run ruff check --fix .

# Run tests
uv run pytest tests/
```

### Pre-commit Hooks

Set up pre-commit hooks to ensure code quality:

```bash
pre-commit install
pre-commit run --all-files
```

---

## 📈 Roadmap

- [ ] ✅ Improve token refresh handling
- [ ] 🔔 Replace polling with Gmail Push Notifications (Pub/Sub)
- [ ] 📊 Add metrics & monitoring (Prometheus / Sentry)
- [ ] 🧠 Enhance LLM integration with more response templates
- [ ] 🧰 Add plugin architecture for additional file types
- [ ] 🔄 Implement retry logic for failed operations

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. 🍴 Fork the repository
2. 🌿 Create a new branch (`git checkout -b feature/amazing-feature`)
3. 💡 Make your changes
4. ✅ Ensure tests pass and code is linted
5. 📨 Submit a Pull Request

Make sure your code passes linting and tests:

```bash
uv run ruff check .
uv run pytest tests/
```

---

## 🛡️ Security Notes

- 🔐 **Never commit** `credentials.json` or `token.json` to version control
- 🔑 Store API keys and secrets in environment variables or a secret manager
- 🔒 Use Gmail's **OAuth2** with secure token refresh handling
- 👥 Limit OAuth scope permissions to only what's necessary
- 🔍 Regularly audit API access and rotate credentials

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🌟 Acknowledgements

- [Gmail API](https://developers.google.com/gmail/api) - Email automation
- [Google Auth Library](https://google-auth.readthedocs.io) - OAuth authentication
- [Supabase](https://supabase.com) - Database and storage
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

---

## 💬 Feedback & Support

If you encounter bugs 🐛 or have suggestions 💡:
- [Open an issue](https://github.com/Nandani347/GamilAutomation/issues)
- [Start a discussion](https://github.com/Nandani347/GamilAutomation/discussions)

---

Made with ❤️ by [Nandani](https://github.com/Nandani347)