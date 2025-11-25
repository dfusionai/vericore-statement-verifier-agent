# Competition Specifications

This document outlines the technical specifications and requirements for participating in the competition.

**Prize:** 30,000 Alpha tokens to the winner

**Technical Specifications:** See GitHub: https://github.com/dfusionai/vericore-statement-verifier-agent

## Table of Contents

- [API Specifications](#api-specifications)
  - [Search API](#search-api)
  - [LLM API](#llm-api)
  - [Miner Verification API](#miner-verification-api)
- [Competition Scoring](#competition-scoring)
- [Staking Requirements](#staking-requirements)
- [Submission Process](#submission-process)

---

## API Specifications

Miners have access to two internal APIs via the internal network: a Search API and an LLM API.

### Search API

The Search API allows miners to search for information across web, news, and scholarly sources.
The endpoint URL will be provided via an environment variable at runtime. The example endpoint below is for reference only - miners should use the environment variable in their implementation. Below is the expected request and response format.

**Endpoint (Example):** `https://example-search-api:8000/search`

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
The endpoint URL will be provided via an environment variable at runtime. The example endpoint below is for reference only - miners should use the environment variable in their implementation. The request and response formats follow the OpenAI Chat Completions API specifications.

**Endpoint (Example):** `http://example-llm-api:8000/v1/chat/completions`

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
- **`gpt-oss-20b`** (abliterated version)

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

Response will be the same as the Open AI response dependent on the model provided.

---

### Miner Verification API

The Miner Verification API is the endpoint that miners must implement to verify statements. Miners receive verification requests and must return structured responses with evidence and reasoning.

**Endpoint:** `/verify`

**Method:** `POST`

**Content-Type:** `application/json`

#### Request Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `statement` | string | The statement to verify | Yes |
| `statement_id` | string | Unique identifier for the statement | Yes |
| `timeout_seconds` | integer | Maximum time allowed for processing (default: 300) | No |

#### Request Example

```json
{
  "statement": "The capital of France is Paris",
  "statement_id": "stmt_1234567890",
  "timeout_seconds": 300
}
```

#### Response Format

| Field | Type | Description |
|-------|------|-------------|
| `statement_id` | string | The statement ID from the request |
| `overall_score` | float | Score from 0.0-1.0 where 0.0 = strongly refutes, 0.5 = neutral, 1.0 = strongly corroborates |
| `overall_verdict` | string | One of: `"corroborates"`, `"refutes"`, or `"neutral"` |
| `reasoning` | string | Detailed reasoning (100-500 words) |
| `evidence` | array | Array of evidence items (1-10 sources) |
| `response_metadata` | object | Metadata about the processing |

#### Evidence Item Object

| Field | Type | Description |
|-------|------|-------------|
| `source_url` | string | URL of the evidence source |
| `extracted_text` | string | Extracted text from the source (max 500 chars) |
| `relevance_score` | float | Relevance score from 0.0-1.0 |
| `corroboration_score` | float | Corroboration score from 0.0-1.0 |
| `timestamp_retrieved` | string | ISO8601 formatted timestamp when the evidence was retrieved |

#### Response Metadata Object

| Field | Type | Description |
|-------|------|-------------|
| `processing_time_seconds` | float | Total processing time in seconds |
| `search_queries_used` | integer | Number of search queries executed |
| `llm_tokens_used` | integer | Total LLM tokens consumed |

#### Response Example

```json
{
  "statement_id": "stmt_1234567890",
  "overall_score": 0.9,
  "overall_verdict": "corroborates",
  "reasoning": "The statement 'The capital of France is Paris' is strongly corroborated by multiple authoritative sources. Paris has been the capital of France since 987 AD, when Hugh Capet became King of France and established his court in Paris. This fact is consistently documented across encyclopedias, government sources, and historical records. The city serves as the political, economic, and cultural center of France, housing the French government, the National Assembly, and the Senate. Multiple verification sources confirm this established fact without contradiction.",
  "evidence": [
    {
      "source_url": "https://example.com/france-capital",
      "extracted_text": "Paris is the capital and most populous city of France. It has been the capital since the Middle Ages and serves as the country's political, economic, and cultural center.",
      "relevance_score": 0.95,
      "corroboration_score": 0.9,
      "timestamp_retrieved": "2024-01-15T10:30:00Z"
    }
  ],
  "response_metadata": {
    "processing_time_seconds": 12.5,
    "search_queries_used": 3,
    "llm_tokens_used": 1250
  }
}
```

---

## Competition Scoring

The competition scoring system evaluates miner performance based on accuracy, speed, and submission timing.

### Competition Format

- **Total Statements:** The competition consists of **20 statements** from a hidden test set that each miner must verify
- **Score Aggregation:** Scores are calculated by adding up performance across all 20 statements
- Each statement is evaluated independently, and the total score determines the final ranking


### Scoring Criteria

#### Primary Scoring: Accuracy

The primary scoring criterion is **accuracy** - whether the miner's `overall_verdict` matches the correct answer for each statement.

- **Correct Verdict:** Miners receive 1 point when their `overall_verdict` matches the expected answer for a statement
- **Incorrect Verdict:** Miners receive 0 points for incorrect verdicts
- **Total Score:** Points are summed across all 20 statements (maximum possible score: 20 points)
- The verdict must be one of: `"corroborates"`, `"refutes"`, or `"neutral"`

#### Tiebreaker 1: Processing Speed

When multiple miners have the same total accuracy score (same number of correct verdicts), the tiebreaker is **processing speed** (faster is better).

- Speed is measured by summing `response_metadata.processing_time_seconds` across all 20 statements
- Lower total processing time (faster overall responses) ranks higher
- Processing time must be within the `timeout_seconds` limit specified in each request

#### Tiebreaker 2: Submission Time

If miners are still tied after accuracy and speed, the final tiebreaker is **submission time** (earlier is better).

- Submission time refers to when the miner's code was first successfully submitted to the competition
- Earlier submissions rank higher
- This encourages early participation and testing

### Scoring Summary

1. **Primary:** Total number of correct `overall_verdict` matches across all 20 statements (maximum: 20 points)
2. **Tiebreaker 1:** Lower total `processing_time_seconds` summed across all 20 statements (faster overall responses)
3. **Tiebreaker 2:** Earlier code submission timestamp

### Example Scoring Scenario

| Miner | Correct Statements | Total Score | Total Processing Time | Submission Time | Rank |
|-------|-------------------|-------------|----------------------|-----------------|------|
| Miner A | 18/20 | 18 | 210.0s | Day 1, 10:00 AM | 1st |
| Miner B | 18/20 | 18 | 210.0s | Day 1, 11:00 AM | 2nd |
| Miner C | 18/20 | 18 | 304.0s | Day 1, 9:00 AM | 3rd |
| Miner D | 17/20 | 17 | 160.0s | Day 1, 8:00 AM | 4th |

In this example:
- Miners A, B, and C all have 18 correct statements, so they rank above Miner D (17 correct)
- Miners A and B have the same total processing time (210.0s), so Miner A wins due to earlier submission
- Miner C has slower total processing time (304.0s) than A and B, so ranks third
- Miner D has the fastest total processing time but fewer correct statements, so ranks last

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

The submission process starts from **December 1st, 2025**.

**Final submission deadline:** January 15th, 2025

**Evaluations:** Ongoing throughout competition period

Miners must build a containerized fact-verification system that processes statements from the test set. Miners submit their agent code by uploading it to a GitHub Gist and then submitting the Gist URL to the statement verifier endpoint. The system validates submissions and enforces a cooldown period between resubmissions.

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
- **Winning implementation subject to manual code inspection**
