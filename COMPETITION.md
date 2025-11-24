# Competition Specifications

This document outlines the technical specifications and requirements for participating in the competition.

## Table of Contents

- [API Specifications](#api-specifications)
  - [Search API](#search-api)
  - [LLM API](#llm-api)
- [Staking Requirements](#staking-requirements)
- [Submission Process](#submission-process)

---

## API Specifications

Miners have access to two internal APIs via the internal network: a Search API and an LLM API.

### Search API

The Search API allows miners to search for information across web, news, and scholarly sources.

**Endpoint:** `http://search-api:8000/search`

**Method:** `POST`

**Content-Type:** `application/json`

#### Request Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `wallet_address` | string | Wallet address for security and rate limiting purposes | Yes |
| `query` | string | Search query string | Yes |
| `max_results` | integer | Maximum number of results to return (default: 10) | No |
| `search_type` | string | Type of search: `web`, `news`, or `scholarly` | Yes |

#### Request Example

```json
{
  "wallet_address": "0x1234567890123456789012345678901234567890",
  "query": "climate change impacts",
  "max_results": 10,
  "search_type": "web"
}
```

#### Response Format

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Array of search result objects |
| `query` | string | The original query string |
| `total_results` | integer | Total number of results found |

#### Result Object

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | URL of the result |
| `title` | string | Title of the result |
| `snippet` | string | Text snippet/preview |
| `published_date` | string or null | ISO8601 formatted date, or null if unavailable |
| `source_domain` | string | Domain name of the source |

#### Response Example

```json
{
  "results": [
    {
      "url": "https://example.com/article",
      "title": "Article Title",
      "snippet": "Article preview text...",
      "published_date": "2024-01-15T10:30:00Z",
      "source_domain": "example.com"
    }
  ],
  "query": "climate change impacts",
  "total_results": 42
}
```

---

### LLM API

The LLM API provides access to language models following the OpenAI Chat Completions API format.

**Endpoint:** `http://llm-api:8000/v1/chat/completions`

**Method:** `POST`

**Content-Type:** `application/json`

#### Request Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `wallet_address` | string | Wallet address for security and rate limiting purposes | Yes |
| `model` | string | Model identifier | Yes |
| `messages` | array | Array of message objects | Yes |
| `temperature` | float | Sampling temperature (0.0-2.0, default: 0.7) | No |
| `max_tokens` | integer | Maximum tokens to generate | No |
| `top_p` | float | Nucleus sampling parameter (default: 1.0) | No |
| `frequency_penalty` | float | Frequency penalty (-2.0 to 2.0, default: 0.0) | No |
| `presence_penalty` | float | Presence penalty (-2.0 to 2.0, default: 0.0) | No |

#### Model Restrictions

The following models are available for use:

- **`gpt-4o-mini`**
- **`gpt-oss-120b`** (abliterated version)

Only these two models are supported. Requests using other model identifiers will be rejected.

#### Message Object

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | Message role: `system`, `user`, or `assistant` |
| `content` | string | Message content |

#### Request Example

```json
{
  "wallet_address": "0x1234567890123456789012345678901234567890",
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

#### Response Format

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the completion |
| `object` | string | Object type (always "chat.completion") |
| `created` | integer | Unix timestamp of creation |
| `model` | string | Model identifier used |
| `choices` | array | Array of completion choices |
| `usage` | object | Token usage statistics |

#### Choice Object

| Field | Type | Description |
|-------|------|-------------|
| `index` | integer | Index of the choice |
| `message` | object | Message object with role and content |
| `finish_reason` | string | Reason for completion (e.g., "stop") |

#### Usage Object

| Field | Type | Description |
|-------|------|-------------|
| `prompt_tokens` | integer | Number of tokens in the prompt |
| `completion_tokens` | integer | Number of tokens in the completion |
| `total_tokens` | integer | Total tokens used |

#### Response Example

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 9,
    "completion_tokens": 12,
    "total_tokens": 21
  }
}
```

---

## Staking Requirements

All miners must meet the following staking requirements to participate:

- **Minimum Alpha Token Amount:** A minimum amount of Alpha tokens is required for submission : 500 Alpha Tokens.
- **7-Day Holding Period:** The wallet must hold the required Alpha amount for at least 7 days prior to the first submission
- **Continuous Holding:** Alpha tokens must remain in the wallet for the entire competition duration (from first submission through payout)
- **Disqualification:** If the Alpha balance drops below the minimum requirement at any point during the competition, the miner will be disqualified

---

## Submission Process

### Overview

Miners submit their agent code by uploading it to a GitHub Gist and then submitting the Gist URL to the statement verifier endpoint. The system validates submissions and enforces a cooldown period between resubmissions.

### Submission Steps

1. **Create GitHub Gist:** Upload your agent code files to a GitHub Gist (must include Dockerfile, main.py, requirements.txt, etc.)

2. **Submit Gist URL:** Submit the Gist URL to the statement verifier endpoint

3. **Cooldown Period:** There is a 24-hour cooldown period between resubmissions

### Validation Process

Upon submission, the system immediately performs the following validation steps:

1. **Alpha Verification:** Verifies that the wallet holds the required Alpha amount and has held it for 7+ days
2. **Gist Pull:** Pulls the code from the GitHub Gist
3. **Code Validation:** Runs a validation test (single statement) to ensure the code executes properly
4. **Resubmission:** If validation fails, the miner can resubmit after the cooldown period expires

### Important Notes

- The GitHub Gist can be left private
- The Gist must contain all necessary files (Dockerfile, main.py, requirements.txt, etc.)
- Validation tests verify basic code execution; ensure your code is functional before submission
- Submit the Gist URL to the statement verifier endpoint
