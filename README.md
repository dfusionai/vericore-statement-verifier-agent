# Vericore Statement Verifier Agent

A Bittensor subnet agent for statement verification, corroboration, and refutation with evidence-based analysis.

## Installation

### Step 1: Install Prerequisites

Install `uv` (Python package manager):
```bash
pip install uv
```

### Step 2: Install Dependencies

Synchronize all project dependencies:
```bash
uv sync
```

### Step 3: Install vericore_agent Package

Install the vericore_agent package in editable mode:
```bash
pip install -e .
```

This installs the `vericore_agent` package and makes the `neurons` CLI command available.

**Note:** The repository name is `vericore-statement-verifier-agent`, but the Python package name remains `vericore_agent` for consistency.

## Usage

### Pushing Agent Code to Blockchain

To push your agent code to the blockchain, use the `neurons push` command:

```bash
neurons push <FOLDER PATH from root> \
  --wallet-coldkey=bittensor \
  --wallet-hotkey=miner_perplexity_hotkey \
  --github-token=<your_github_token>
```

**Command Parameters:**
- `<FOLDER PATH from root>`: Path to the directory containing your agent code (defaults to `envs/verify` if not specified). The directory must include Dockerfile, main.py, requirements.txt, etc.
- `--wallet-coldkey`: Your Bittensor coldkey wallet name
- `--wallet-hotkey`: Your Bittensor hotkey wallet name  
- `--github-token`: Your GitHub personal access token (must have `gist` scope)

**Example:**
```bash
# Using default path (envs/verify)
neurons push --wallet-coldkey=bittensor --wallet-hotkey=miner_perplexity_hotkey --github-token=<your_github_token>

# Using custom path
neurons push my_agent_folder --wallet-coldkey=bittensor --wallet-hotkey=miner_perplexity_hotkey --github-token=<your_github_token>
```

**Important Notes:**
- Your wallet must be registered on the subnet before pushing. If not registered, register first:
  ```bash
  btcli subnet register --netuid <netuid> --wallet.name <coldkey> --wallet.hotkey <hotkey>
  ```
- The agent directory should contain:
  - `Dockerfile` - Container configuration (must expose port 8080)
  - `main.py` - FastAPI application with `/verify` endpoint
  - `requirements.txt` - Python dependencies
  - `.env` - Environment variables (optional)

### Getting GitHub Token

1. Go to https://github.com/settings/tokens/new
2. Generate a new token with `gist` scope
3. Copy the token and use it in the `--github-token` parameter

## Project Structure

```
vericore-statement-verifier-agent/
├── envs/
│   └── verify/          # Default agent code directory
│       ├── Dockerfile    # Docker container configuration
│       ├── main.py       # FastAPI application
│       ├── requirements.txt
│       └── .env
├── miner_agent/
│   └── run.py           # Script to pull and test agents
├── neurons/
│   └── __init__.py      # Blockchain interaction code
└── vericore_agent/
    └── __init__.py      # Core framework
```

## Development

### Testing Agents on the Blockchain

You can test agents that are already deployed on the blockchain using the miner agent:

```bash
python miner_agent/run.py <uid>
```

This will:
1. Pull agent code from blockchain for the specified UID
2. Build Docker image from the pulled code
3. Run the container
4. Call the API endpoint with test statements

### Running the Miner Locally Without Docker

To run the miner code from `envs/verify` locally without Docker:

#### Step 1: Navigate to the verify directory

```bash
cd envs/verify
```

#### Step 2: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Or if using `uv`:

```bash
uv pip install -r requirements.txt
```

#### Step 3: Set Up Environment Variables

For local development, you can use `.env.example` as a reference file for the environment variables needed. Copy the example file and configure it with your values:

```bash
# Copy the example file to create your local .env file
cp ../.env.example .env

# Then edit .env with your actual values
```

Alternatively, create a `.env` file in the `envs/verify` directory with your configuration:

```bash
# Create .env file with your configuration
# Example:
# PORT=8080
# HOST=0.0.0.0
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
```

#### Step 4: Run the FastAPI Application

Start the FastAPI server directly:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

The API will be available at `http://localhost:8080`.

#### Step 5: Test the API

You can test the `/verify` endpoint using curl or any HTTP client:

```bash
curl -X POST "http://localhost:8080/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "statement": "The sky is blue",
    "statement_id": "test_001",
    "timeout_seconds": 300
  }'
```

Or check the health endpoint:

```bash
curl http://localhost:8080/health
```

**Note:** When running locally without Docker, make sure:
- Python 3.8+ is installed
- All dependencies from `requirements.txt` are installed
- Port 8080 is available (or modify the port via `PORT` environment variable)
- Any required API keys or environment variables are properly configured in `.env` file