# Financial Modeling Prep (FMP) MCP Server

> A lightweight, production-ready **Model Context Protocol (MCP)** server that brings **real financial data** directly to AI agents or LLM Apps — fundamentals, ratios, price data, transcripts, macro indicators, and more.

## Overview

The **Financial Modeling Prep MCP Server** acts as a bridge between AI agents or LLM Apps and the **Financial Modeling Prep (FMP)** API, offering a structured and safe interface to query real-world market and company data.

This server gives you a single MCP endpoint your AI tools can call for:

- **Fundamentals** – Income statements, balance sheets, cash flows  
- **Valuation Metrics** – P/E, P/B, ROE, margins, leverage  
- **News** – Latest market or ticker-specific headlines  
- **Earnings Transcripts** – Full text of company calls  
- **Macro Data** – CPI, GDP, employment, and event calendars  
- **Insider Trades** – Real-time Form-4 style transactions  

<img height="600" alt="image" src="https://github.com/user-attachments/assets/d9396afe-4edd-4ca2-a9e3-5c74a5d85920" />

---

## Requirements

| Requirement | Version | Notes |
|--------------|----------|-------|
| Python | 3.9+ | Recommended: 3.10 or higher |
| Dependencies | `httpx`, `mcp`, `uvicorn`, `starlette` | Install via `pip install -r requirements.txt` |
| Environment | Set `FMP_API_KEY` | Defaults to `"demo"` with rate limits |

---

## You Would Need a Financial Modeling Prep (FMP) API Key

To use this MCP server with full access (beyond the limited `demo` key), you’ll need your own **FMP API key**.

1. Go to the official registration page:  
   [https://site.financialmodelingprep.com/register](https://site.financialmodelingprep.com/register)
2. Create a free account using your email.
3. After registration, navigate to your **Dashboard → API Key** section to get the API Key.
   
Note that some FMP API endpoints may not work if you are using the free version of FMP API.

---

## Installation

```bash
git clone https://github.com/damianboh/fmp_mcp_server.git
cd fmp-mcp-server
pip install -r requirements.txt
```

Then set your API key:

```bash
export FMP_API_KEY=your_fmp_api_key_here  # macOS/Linux
setx FMP_API_KEY your_fmp_api_key_here    # Windows
```

---

## Running the Server

The script supports **3 launch modes** via the `--transport` flag in your cmd command:

### **1️. STDIO Mode (Default)**

For local development and direct MCP use via CLI or ChatGPT desktop app.

```bash
python src/fmp_mcp_server.py
```

Equivalent to:
```bash
python src/fmp_mcp_server.py --transport stdio
```

This mode just communicates over standard input/output — ideal for embedding in local AI environments.

---

### **2️. SSE Mode (Server-Sent Events)**

For streaming output via **FastMCP’s SSE transport**.

```bash
python src/fmp_mcp_server.py --transport sse
```

This is used by frameworks like **LangChain MCP** or **OpenDevin** that consume event streams.

---

### **3️. Streamable HTTP Mode**

Runs a **Starlette / Uvicorn** HTTP server for remote access (ideal for ChatGPT or cloud tunnels).

```bash
python src/fmp_mcp_server.py --transport streamable-http --host 127.0.0.1 --port 8000
```

You’ll see:
```
Starting FMP MCP Server (Streamable HTTP mode) on http://127.0.0.1:8000
API Key configured: Yes
Streamable HTTP endpoint (path hint): http://127.0.0.1:8000/mcp/
```

Then test:
```bash
curl http://127.0.0.1:8000/health
```

Expected:
```json
{"status": "healthy", "service": "fmp-mcp-server"}
```

---

## Exposing the Server to the Web

You need to do this if you want to expose the server to other LLMs hosted on the web, e.g. ChatGPT.

### **Option A: Cloudflare Tunnel (Recommended)**

Cloudflare is fast, free, and doesn’t require installing ngrok.

1. [Install Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)
2. Authenticate:
   ```bash
   cloudflared login
   ```
3. Run tunnel:
   ```bash
   cloudflared tunnel --url http://127.0.0.1:8000
   ```
   Output example:
   ```
   https://fmp-mcp-server-sg.trycloudflare.com
   ```

Copy this URL and use it as your **MCP server endpoint** inside ChatGPT or any MCP-capable client.

---

### **Option B: Ngrok**

```bash
ngrok http 8000
```

Then use the forwarded URL in your MCP config, e.g.:

```
https://1234-56-78-90-123.ngrok-free.app/mcp/
```

---


## Example: Using with ChatGPT (Custom MCP Server) (Paid Plan Required)

1. Open **ChatGPT → Settings → Apps & Connectors → Developer Mode On**. You would need a paid (ChatGPT Plus) account for turning developer mode on.
   And you need this mode for creating and connecting to your own custom MCP server.
   
   <img height="400" alt="image" src="https://github.com/user-attachments/assets/8d5cb0b8-6abc-48f9-b2d1-37f528e06eda" />
   
3. Go back to Apps & Connectors and click **Create**
4. Paste your tunnel URL:
   ```
   https://whatever-subdomain-assigned-to-you.trycloudflare.com/mcp/
   ```
   
  <img height="600" alt="image" src="https://github.com/user-attachments/assets/c48a4c4d-cd55-4e64-a5c8-8bcabfc6f618" />
   
4. ChatGPT will now auto-discover all available tools and resources:
   - `/stable/profile` → Company profile  
   - `/stable/ratios` → Financial ratios  
   - `/stable/earning-call-transcript` → Earnings transcript  
   - `/stable/news` → Stock news  

You can now ask questions like these (yay!): 

<img height="600" alt="image" src="https://github.com/user-attachments/assets/6bee7d34-42a4-4083-9cab-b8f16139d623" /><br><br>

When ChatGPT tries to call a tool for the first time, you will need to click "Confirm" as shown below.

<img height="600" alt="image" src="https://github.com/user-attachments/assets/2b1b340b-2da2-449a-b598-186b1e2a1846" /><br><br>

### Examples of tool calls:

<img height="600" alt="image" src="https://github.com/user-attachments/assets/78977129-7d3b-4b7f-b5cc-c0df5f5a71b6" /><br><br>
<img height="600" alt="image" src="https://github.com/user-attachments/assets/dbec8eee-227a-4c9a-bcef-5a5f0d65df19" />

ChatGPT knows and can now call the correct FMP MCP tools.

---

## Included Tools

| Category | Tool | Description |
|-----------|------|-------------|
| Company Fundamentals | `company_profile` | Overview: price, market cap, CEO, sector, identifiers |
| Statements | `income_statement`, `balance_sheet`, `cash_flow` | Financials across periods |
| Ratios | `financial_ratios` | P/E, ROE, margins, leverage, etc. |
| Price Data | `historical_price_eod_full` | Full OHLCV daily bars |
| Transcripts | `earnings_call_transcript` | Management Q&A and remarks |
| Macroeconomics | `economic_indicators`, `economic_calendar` | GDP, CPI, NFP, and calendar events |
| News | `stock_news_latest`, `stock_news_search` | General and ticker-specific headlines |
| Insider Trades | `insider_trading_latest` | Form-4 type recent insider transactions |
| Utilities | `ping`, `when_should_i_use_fmp` | Health check and routing hint |

---


## When to Use This Server

- You need **factual** stock or macro data  
- You’re analyzing **fundamentals or transcripts**  
- You’re building **RAG** or **agentic pipelines** that rely on finance data  
---

## 🧪 Health Check

Verify the server is running:

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{"status": "healthy", "service": "fmp-mcp-server"}
```

---

## Advanced Options

| Flag | Description | Default |
|------|--------------|----------|
| `--host` | Host interface | `127.0.0.1` |
| `--port` | Server port | `8000` |
| `--path` | HTTP path prefix | `/mcp/` |
| `--stateless` | Run in stateless HTTP mode | `False` |
| `--json-response` | Use JSON responses (instead of SSE) | `False` |

Example:

```bash
python src/fmp_mcp_server.py --transport streamable-http --stateless --json-response
```

---

## Quick Reference

| Purpose | Command |
|----------|----------|
| Run locally | `python src/fmp_mcp_server.py` |
| Stream SSE | `python src/fmp_mcp_server.py --transport sse` |
| HTTP endpoint | `python src/fmp_mcp_server.py --transport streamable-http` |
| Health check | `curl http://127.0.0.1:8000/health` |
| Expose via Cloudflare | `cloudflared tunnel --url http://127.0.0.1:8000` |
| Connect to ChatGPT | Use the Cloudflare URL as MCP endpoint |

---

Have fun!

Cheers,
Damian
