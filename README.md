# Gmail Automation

A Gmail Automation pipeline for insertion and retrieval that provides Gmail access for LLMs.

## Features

- Polls Gmail every 3 seconds for new emails from specified users.
- Processes email attachments (images, PDFs, CSVs, Excel files) and integrates with Supabase for storage and management.
- OAuth 2.0 authentication with Google's Gmail API.
- Ready for LLM-based processing and automated escalation logic.

## Prerequisites

- Python 3.10+
- Gmail account with API access
- `uv` for Python package management (recommended)

## Setup

### 1. Install dependencies

Install project dependencies (uv automatically creates and manages a virtual environment):

```bash
uv sync
```

### 2. Configure Gmail OAuth credentials

There are several steps required to use the Gmail API. This guide is based on the current API configuration as of October 2, 2025. Steps may change in the future.

#### Google Cloud Setup

**Create a Google Cloud Project**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown → "New Project"
3. Enter a project name (e.g., "Gmail Automation")
4. Click "Create" and select the project once created.

**Enable the Gmail API**

1. Go to "APIs & Services" > "Library"
2. Search for "Gmail API" and click "Enable"

**Configure OAuth Consent Screen**

1. Go to "APIs & Services" > "OAuth consent screen"
2. Fill in required application info:
   - App name: "Gmail Automation"
   - User support email: Your email
   - Audience: External (unless using Google Workspace)
3. Click "Save and Continue" → "Create"

**Create OAuth Credentials**

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Desktop app" and give it a name (e.g., "Gmail Desktop Client")
4. Download JSON and save as `credentials.json` in the project root.

**Add Scopes**

1. Go to "APIs & Services" > "OAuth consent screen" → "Data Access"
2. Add the scope `.../auth/gmail.modify` (read, compose, and send emails)
3. Click "Update" → "Save"

Verify the setup by checking usage metrics at:
https://console.cloud.google.com/apis/api/gmail.googleapis.com/metrics

## Development

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

```bash
pre-commit install
pre-commit run --all-files
```

## Usage

Run the Gmail automation script to start monitoring for new emails:

```bash
uv run python demo.py
```

The system will:

- Poll Gmail every 3 seconds
- Process new emails from configured users
- Extract attachments and store them temporarily for LLM processing
- Log all activity to the console and log files

## Environment Variables

(Optional: Add if your project uses env vars for credentials or config)

- `MCP_GMAIL_CREDENTIALS_PATH`: Path to credentials.json (default: "credentials.json")
- `MCP_GMAIL_TOKEN_PATH`: Path to store OAuth token (default: "token.json")


## License

MIT