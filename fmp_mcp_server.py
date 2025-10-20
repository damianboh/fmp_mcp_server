"""
FMP MCP Server (Python)

This version exposes **only** the endpoints you specified, with detailed docstrings
that incorporate your descriptions and examples.

Included APIs (FMP /stable):
  • Company Profile  -> /stable/profile
  • Income Statement -> /stable/income-statement
  • Balance Sheet    -> /stable/balance-sheet-statement
  • Cash Flow        -> /stable/cash-flow-statement
  • Financial Ratios -> /stable/ratios
  • Stock Price & Volume (EOD full) -> /stable/historical-price-eod/full
  • Earnings Transcript -> /stable/earning-call-transcript
  • Economic Indicators -> /stable/economic-indicators
  • Economic Calendar   -> /stable/economic-calendar
  • Stock News (latest) -> /stable/news/stock-latest
  • Search Stock News   -> /stable/news/stock
  • Latest Insider Trading -> /stable/insider-trading/latest

Run modes
---------
- stdio (default): `python fmp_mcp_server.py`
- SSE (streamable HTTP via FastMCP): `python fmp_mcp_server.py --transport sse`
- Streamable HTTP (Starlette/Uvicorn): `python fmp_mcp_server.py --transport streamable-http --host 127.0.0.1 --port 8000`

Auth
----
- Set `FMP_API_KEY` in your environment (falls back to "demo").
"""
import os
from typing import Any, Dict, Optional, Literal

import httpx
from mcp.server.fastmcp import FastMCP

FMP_BASE_URL = "https://financialmodelingprep.com/stable"
DEFAULT_API_KEY = os.environ.get("FMP_API_KEY", "demo")

# ---------------------------------------------------------------------------
# Core HTTP helper
# ---------------------------------------------------------------------------
async def fmp_api_request(endpoint: str, params: Optional[Dict] = None, api_key: Optional[str] = None) -> Dict:
    """Make a request to the Financial Modeling Prep API under /stable.

    Automatically appends the API key, returns parsed JSON, and surfaces errors
    as a small error dict so MCP clients receive an explainable result instead
    of raising.
    """
    url = f"{FMP_BASE_URL}/{endpoint.lstrip('/')}"
    params = params.copy() if params else {}
    params["apikey"] = api_key or DEFAULT_API_KEY

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=30.0)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error: {e.response.status_code}", "message": str(e)}
    except httpx.RequestError as e:
        return {"error": "Request error", "message": str(e)}
    except Exception as e:
        return {"error": "Unknown error", "message": str(e)}

# ---------------------------------------------------------------------------
# MCP instance (stdio by default)
# ---------------------------------------------------------------------------
mcp = FastMCP("fmp")

# ========================= RESOURCES & PROMPTS ==============================

@mcp.resource("fmp:readme")
def fmp_readme() -> str:
    """
    FMP MCP Server README

    Use this server when:
      • You need real financial data from Financial Modeling Prep (/stable):
        company profiles, income statements, balance sheets, cash flows,
        financial ratios, full daily OHLCV, earnings call transcripts,
        macro indicators, economic calendar, stock news, or insider trades.
      • The task mentions tickers (e.g., AAPL, MSFT, TSLA), fundamentals/valuation,
        earnings transcripts, macro/CPI/Fed calendar, or insider transactions.

    Not a fit when:
      • You need order execution, brokerage actions, Level II order book, or real-time ticks.
      • You need complete SEC filing documents beyond transcripts (use an SEC-focused tool).

    Authentication:
      • Set `FMP_API_KEY` (falls back to `demo` with tight limits).

    Quick start:
      • Try `company_profile(symbol="AAPL")` then `financial_ratios(symbol="AAPL")`.
    """
    return fmp_readme.__doc__


@mcp.prompt("how_to_use_fmp")
def how_to_use_fmp() -> str:
    return (
        "If the user asks for stock fundamentals, ratios, financial statements, "
        "earnings call transcripts, macro indicators, economic calendars, insider trades, "
        "or daily OHLCV, choose an FMP tool. Map user intent:\n"
        "- Snapshot/company facts → company_profile\n"
        "- Periodized P&L → income_statement\n"
        "- Balance sheet items → balance_sheet\n"
        "- Cash generation/free cash flow → cash_flow\n"
        "- Ratios/valuation/liquidity → financial_ratios\n"
        "- Daily price series → historical_price_eod_full\n"
        "- Earnings call text → earnings_call_transcript\n"
        "- Macro time series → economic_indicators\n"
        "- Release schedule → economic_calendar\n"
        "- Latest news / ticker-filtered news → stock_news_latest / stock_news_search\n"
        "- Insider transactions → insider_trading_latest\n"
        "Prefer the most specific tool; avoid calling multiple tools unless necessary."
    )

# ========================= TOOLS (ONLY YOUR ENDPOINTS) ======================

@mcp.tool()
async def company_profile(symbol: str) -> Any:
    """Company Profile Data API — detailed fundamentals for a single symbol.

    Use this when:
      • You need a company’s *current snapshot* (price, marketCap, beta, identifiers).
      • You’re building a profile card or prepping context before deeper statement pulls.

    Don’t use when:
      • You need periodized statements (use income_statement / balance_sheet / cash_flow).
      • You want multi-period ratios (use financial_ratios).

    Endpoint: `/stable/profile`

    What it provides (high-level):
      • **Stock Price & Market Cap**: Current `price` and `marketCap` for the symbol.
      • **Company Details**: `companyName`, long `description`, `CEO`, `industry`, `sector`, exchange info.
      • **Financial Metrics**: `beta`, `lastDividend`, trading `range` (e.g., 52-week), `volume`, `averageVolume`.
      • **Global Identifiers**: `cik`, `isin`, `cusip` to track the entity across platforms.
      • **Contact Information**: `address`, `city`, `state`, `zip`, `phone`, and `website`.
      • **IPO & Trading Flags**: `ipoDate`, `isActivelyTrading`, `isEtf`, `isAdr`, `isFund`.

    Typical uses:
      • Research a company’s **current financial snapshot** (e.g., Apple) and extract
        key metrics for investment due diligence or profile cards.

    Args:
      symbol: Ticker symbol (e.g., "AAPL").

    Returns:
      A 1-element list with the profile object as shown in your example.
    """
    return await fmp_api_request("profile", {"symbol": symbol})

Period = Literal["annual", "quarter", "Q1", "Q2", "Q3", "Q4", "FY"]

@mcp.tool()
async def income_statement(symbol: str, limit: int = 5, period: str = "annual") -> Any:
    """Income Statement API — real-time & historical profitability view.

    Use this when:
      • You need revenue, cost, margins, EPS across periods (annual/quarterly).
      • You’re computing profitability ratios or analyzing earnings trends.

    Don’t use when:
      • You need assets/liabilities/equity (use balance_sheet).
      • You want cash flow specifics/FCF (use cash_flow).

    Endpoint: `/stable/income-statement`

    What it provides:
      • **Profitability Tracking**: `revenue`, `costOfRevenue`, `grossProfit`, `operatingIncome`, `netIncome`,
        `eps`, `epsDiluted`, etc., by period.
      • **Trend Identification**: Pull multiple periods (`limit`) to observe changes in revenue and expenses
        (e.g., FY vs. Q1–Q4).
      • **Comparative Analysis**: Use with peers to compare margins and earnings power.

    Example use:
      • Compute ratios like **P/E**, **gross margin**, or analyze **surprise vs. trend**.

    Args:
      symbol: Ticker symbol (e.g., "AAPL").
      limit: Number of periods to return (max 1000 per request).
      period: One of `annual` / `quarter` or explicit tags like `Q1`..`Q4`, `FY`.

    Returns:
      A list of income statement rows as in your example (currency as reported).
    """
    return await fmp_api_request("income-statement", {"symbol": symbol, "limit": limit, "period": period})

@mcp.tool()
async def balance_sheet(symbol: str, limit: int = 5, period: str = "annual") -> Any:
    """Balance Sheet Statement API — assets, liabilities, and equity structure.

    Use this when:
      • You need capital structure, leverage, liquidity, or working-capital inputs.
      • You’re comparing balance sheet strength across peers/time.

    Don’t use when:
      • You want income/profitability flows (use income_statement).
      • You want cash generation/FCF (use cash_flow).

    Endpoint: `/stable/balance-sheet-statement`

    What it provides:
      • **Assets**: Current & noncurrent (e.g., `cashAndCashEquivalents`, `longTermInvestments`, `totalAssets`).
      • **Liabilities**: Short/long-term debts, `totalLiabilities`, deferred items.
      • **Equity**: `commonStock`, `retainedEarnings`, `totalStockholdersEquity`.
      • **Solvency/Liquidity Inputs**: Values to compute leverage and working-capital metrics.

    Example use:
      • Assess **liquidity & leverage** and compare structure across peers or over time.

    Args:
      symbol: Ticker symbol.
      limit: Number of periods to return.
      period: `annual` / `quarter` (also supports `Q1`..`Q4`, `FY`).

    Returns:
      A list of balance sheet rows (currency as reported).
    """
    return await fmp_api_request("balance-sheet-statement", {"symbol": symbol, "limit": limit, "period": period})

@mcp.tool()
async def cash_flow(symbol: str, limit: int = 5, period: str = "annual") -> Any:
    """Cash Flow Statement API — operating, investing, and financing cash flows.

    Use this when:
      • You need cash generation/usage details or to compute FCF.
      • You’re analyzing sustainability of dividends/buybacks or financing activity.

    Don’t use when:
      • You want margin/earnings lines (use income_statement).
      • You need capital structure snapshots (use balance_sheet).

    Endpoint: `/stable/cash-flow-statement`

    What it provides:
      • **Operating Cash Flow**: `netCashProvidedByOperatingActivities`, `operatingCashFlow`.
      • **Investing & Financing**: Capex, acquisitions, debt issuance/repayment, dividends, buybacks.
      • **Free Cash Flow**: `freeCashFlow` and components (`capitalExpenditure`).

    Example use:
      • Evaluate **cash generation** and **financial flexibility**, compare FCF across time.

    Args:
      symbol: Ticker symbol.
      limit: Number of periods to return.
      period: `annual` / `quarter` (also supports `Q1`..`Q4`, `FY`).

    Returns:
      A list of cash flow rows as in your example (currency as reported).
    """
    return await fmp_api_request("cash-flow-statement", {"symbol": symbol, "limit": limit, "period": period})

@mcp.tool()
async def financial_ratios(symbol: str, limit: int = 5, period: str = "annual") -> Any:
    """Financial Ratios API — profitability, liquidity, efficiency, leverage.

    Use this when:
      • You want ready-made valuation, liquidity, efficiency, and leverage ratios.
      • You need quick multi-period ratio comparison for screening/peer comps.

    Don’t use when:
      • You need raw statement lines (use income_statement / balance_sheet / cash_flow) to compute custom metrics.
      • You’re requesting intraday/realtime multiples (daily snapshots only).

    Endpoint: `/stable/ratios`

    What it provides:
      • **Profitability**: `grossProfitMargin`, `netProfitMargin`, `ROE` proxies via margins and equity metrics.
      • **Liquidity**: `currentRatio`, `quickRatio`, `cashRatio`.
      • **Efficiency**: `assetTurnover`, `inventoryTurnover`, `receivablesTurnover`.
      • **Valuation & Debt**: `priceToEarningsRatio`, `priceToBookRatio`, `debtToEquityRatio`, `enterpriseValueMultiple`.

    Example use:
      • Cross-company **ratio comparisons** within a sector to evaluate stability and efficiency.

    Args:
      symbol: Ticker symbol.
      limit: Number of periods to return.
      period: `annual` / `quarter` (also supports `Q1`..`Q4`, `FY`).

    Returns:
      A list of ratio snapshots per period.
    """
    return await fmp_api_request("ratios", {"symbol": symbol, "limit": limit, "period": period})

@mcp.tool()
async def historical_price_eod_full(symbol: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Any:
    """Stock Price & Volume Data API — full daily OHLCV + VWAP with changes.

    Use this when:
      • You need historical daily bars (OHLCV) and changes (with optional range).
      • You’re doing backtests, trend analysis, or liquidity studies.

    Don’t use when:
      • You need intraday/minute or realtime ticks (not provided here).
      • You’re asking for corporate actions/adjustment events (use other endpoints).

    Endpoint: `/stable/historical-price-eod/full`

    What it provides:
      • **Detailed Price Series**: `open`, `high`, `low`, `close` per trading day.
      • **Volume & Liquidity**: Daily `volume` values for activity analysis.
      • **Price Dynamics**: Day-over-day `change` and `changePercent`.
      • **VWAP**: `vwap` to contextualize intraday weighted average price.

    Example use:
      • Analyze trends and liquidity over multi-month ranges for a symbol.

    Args:
      symbol: Ticker symbol.
      date_from: Optional start date `YYYY-MM-DD` (<= 5000 records per request).
      date_to: Optional end date `YYYY-MM-DD`.

    Returns:
      A list of daily bars with OHLCV, change, changePercent, and vwap.
    """
    params: Dict[str, Any] = {"symbol": symbol}
    if date_from:
        params["from"] = date_from
    if date_to:
        params["to"] = date_to
    return await fmp_api_request("historical-price-eod/full", params)

@mcp.tool()
async def earnings_call_transcript(symbol: str, year: int, quarter: int, limit: Optional[int] = None) -> Any:
    """Earnings Transcript API — full text of a company’s earnings call.

    Use this when:
      • You need the prepared remarks + Q&A text to analyze tone/strategy/risks.
      • You’re extracting quotes or doing NLP on management commentary.

    Don’t use when:
      • You want numeric KPIs (use statements/ratios).
      • You need 10-K/10-Q filings (use an SEC filings tool).

    Endpoint: `/stable/earning-call-transcript`

    What it provides:
      • **Full Transcript Text**: `content` covering prepared remarks + Q&A.
      • **Context**: `date`, `year`, `period` (e.g., Q3), and `symbol`.

    Example use:
      • Analyze management’s tone, strategy, and risk disclosures beyond numeric filings.

    Args:
      symbol: Ticker symbol (e.g., "AAPL").
      year: Fiscal year (e.g., 2020).
      quarter: Fiscal quarter number `1..4`.
      limit: Optional number of records (API may support a single record; kept for parity).

    Returns:
      A list containing one or more transcript objects with `content` and metadata.
    """
    params: Dict[str, Any] = {"symbol": symbol, "year": year, "quarter": quarter}
    if limit is not None:
        params["limit"] = limit
    return await fmp_api_request("earning-call-transcript", params)

@mcp.tool()
async def economic_indicators(name: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Any:
    """Economic Indicators API — real-time & historical macro indicators.

    Use this when:
      • You need macro time series like GDP, CPI, unemployment, or industrial production.
      • You’re correlating macro with sector/stock performance.

    Don’t use when:
      • You need event timing/releases (use economic_calendar).
      • You need equity fundamentals (use company/statement tools).

    Endpoint: `/stable/economic-indicators`

    What it provides:
      • **Macro Series**: Values for indicators like `GDP`, `unemploymentRate`, `CPI`,
        `inflationRate`, `industrialProductionTotalIndex`, etc.
      • **Windowed Queries**: Restrict by `from` / `to` date (max 90-day range per request).

    Example use:
      • Monitor GDP changes over time to align portfolio positioning with macro cycles.

    Args:
      name: Indicator name (e.g., `GDP`, `unemploymentRate`, `CPI`, see docs’ list).
      date_from: Optional start date `YYYY-MM-DD` (<= 90-day span when combined with `to`).
      date_to: Optional end date `YYYY-MM-DD`.

    Returns:
      A list of {name, date, value} tuples.
    """
    params: Dict[str, Any] = {"name": name}
    if date_from:
        params["from"] = date_from
    if date_to:
        params["to"] = date_to
    return await fmp_api_request("economic-indicators", params)

@mcp.tool()
async def economic_calendar(date_from: Optional[str] = None, date_to: Optional[str] = None) -> Any:
    """Economic Data Releases Calendar API — schedule of upcoming releases.

    Use this when:
      • You want release times and details (country, impact, actual/estimate/previous).
      • You’re planning around market-moving events (CPI, NFP, rates).

    Don’t use when:
      • You need long macro time series values (use economic_indicators).
      • You’re asking for equity-specific fundamentals (use company/statement tools).

    Endpoint: `/stable/economic-calendar`

    What it provides:
      • **Event Timing & Details**: `date`, `country`, `event`, `currency`, and
        actual/estimate/previous values with `impact` level where provided.
      • **Planning**: Helps anticipate potential market reactions around releases.

    Args:
      date_from: Optional start date `YYYY-MM-DD` (max 90-day range with `to`).
      date_to: Optional end date `YYYY-MM-DD`.

    Returns:
      A list of upcoming/past events within the requested window.
    """
    params: Dict[str, Any] = {}
    if date_from:
        params["from"] = date_from
    if date_to:
        params["to"] = date_to
    return await fmp_api_request("economic-calendar", params)

@mcp.tool()
async def stock_news_latest(page: int = 0, limit: int = 20, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Any:
    """Stock News API — latest market/stock headlines and summaries.

    Use this when:
      • You want general/latest market or equity news (optionally date-bounded).
      • You need a scrolling feed for monitoring.

    Don’t use when:
      • You need ticker-filtered news (use stock_news_search with symbols).
      • You’re looking for transcripts or filings.

    Endpoint: `/stable/news/stock-latest`

    What it provides:
      • **Breaking & Recent Headlines**: `title`, `publisher`, `publishedDate`.
      • **Context**: `text` snippet, `image`, `url`, and sometimes mapped `symbol`.

    Args:
      page: Zero-based page index (max page typically 100).
      limit: Page size (max 250).
      date_from: Optional earliest date `YYYY-MM-DD`.
      date_to: Optional latest date `YYYY-MM-DD`.

    Returns:
      A list of news items; use paging to iterate.
    """
    params: Dict[str, Any] = {"page": page, "limit": limit}
    if date_from:
        params["from"] = date_from
    if date_to:
        params["to"] = date_to
    return await fmp_api_request("news/stock-latest", params)

@mcp.tool()
async def stock_news_search(symbols: str, page: int = 0, limit: int = 20, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Any:
    """Search Stock News API — company-specific news by symbols.

    Use this when:
      • You need news filtered for specific tickers (e.g., AAPL, MSFT).
      • You’re building a per-company news panel.

    Don’t use when:
      • You want broad/latest headlines without filter (use stock_news_latest).
      • You’re seeking transcripts/filings.

    Endpoint: `/stable/news/stock`

    What it provides:
      • **Targeted News** filtered by `symbols` (comma-separated tickers), including headline,
        publisher, snippet, URL, and publish timestamp.

    Args:
      symbols: Comma-separated tickers (e.g., "AAPL,MSFT").
      page: Zero-based page index (max page ~100).
      limit: Page size (max 250).
      date_from: Optional start date `YYYY-MM-DD`.
      date_to: Optional end date `YYYY-MM-DD`.

    Returns:
      A list of news items for the requested symbols.
    """
    params: Dict[str, Any] = {"symbols": symbols, "page": page, "limit": limit}
    if date_from:
        params["from"] = date_from
    if date_to:
        params["to"] = date_to
    return await fmp_api_request("news/stock", params)

@mcp.tool()
async def insider_trading_latest(page: int = 0, limit: int = 100, date: Optional[str] = None) -> Any:
    """Latest Insider Trading API — recent buys/sells by corporate insiders.

    Use this when:
      • You want recent insider buys/sells with roles, amounts, and forms.
      • You’re screening for notable insider activity.

    Don’t use when:
      • You need ownership cap tables or institutional holders (different endpoints).
      • You want price series or ratios.

    Endpoint: `/stable/insider-trading/latest`

    What it provides:
      • **Recent Transactions**: Insider purchases/sales with `transactionDate`, `formType` (e.g., 4),
        share counts, and prices.
      • **Actor & Role**: Insider’s name and role (e.g., director, officer), direct/indirect ownership.
      • **Regulatory Links**: Direct links to SEC filing pages where available.

    Args:
      page: Zero-based page index (max page ~100).
      limit: Number of records per page (max 1000).
      date: Optional specific date `YYYY-MM-DD` to filter.

    Returns:
      A list of recent insider transactions across the market.
    """
    params: Dict[str, Any] = {"page": page, "limit": limit}
    if date:
        params["date"] = date
    return await fmp_api_request("insider-trading/latest", params)

# ----------------------------- HEALTH ---------------------------------------
@mcp.tool()
async def ping() -> Dict[str, Any]:
    """Health check for this MCP server."""
    return {"ok": True, "base_url": FMP_BASE_URL}

# ---------------------------- ROUTER HINT -----------------------------------
@mcp.tool()
async def when_should_i_use_fmp() -> dict:
    """Guidance tool — returns when this server is appropriate vs. other data sources."""
    return {
        "use_when": [
            "You need fundamentals/ratios/statements for a ticker",
            "You need OHLCV daily prices",
            "You need earnings transcripts text",
            "You need macro indicators or economic calendar",
            "You need latest stock news or insider trades"
        ],
        "avoid_when": [
            "Trading/execution actions",
            "Full SEC filings beyond transcripts",
            "Realtime tick/quote level market data"
        ],
        "quick_map": {
            "snapshot": "company_profile",
            "pnl": "income_statement",
            "balance": "balance_sheet",
            "cash": "cash_flow",
            "ratios": "financial_ratios",
            "prices": "historical_price_eod_full",
            "transcript": "earnings_call_transcript",
            "macro": "economic_indicators",
            "calendar": "economic_calendar",
            "news": "stock_news_latest / stock_news_search",
            "insiders": "insider_trading_latest"
        }
    }

# ======================== STREAMABLE HTTP (OPTIONAL) ========================

def main() -> None:
    """Run the MCP server via stdio (default), SSE, or streamable HTTP.

    - `--transport stdio` : blocking stdio transport.
    - `--transport sse`   : FastMCP SSE transport (streaming HTTP); path is client-specific.
    - `--transport streamable-http` : Starlette/Uvicorn app from FastMCP.
    """
    import argparse
    import uvicorn
    from starlette.responses import JSONResponse

    parser = argparse.ArgumentParser(description="FMP MCP server")
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--stateless", action="store_true")
    parser.add_argument("--json-response", action="store_true")
    parser.add_argument("--path", default="/mcp/")
    args = parser.parse_args()

    if args.transport == "streamable-http":
        print(f"Starting FMP MCP Server (Streamable HTTP {'stateless' if args.stateless else 'stateful'}{' JSON' if args.json_response else ' SSE'} mode) on http://{args.host}:{args.port}")
        print(f"API Key configured: {'Yes' if os.environ.get('FMP_API_KEY') else 'No - using demo mode'}")
        print(f"Streamable HTTP endpoint (path hint): http://{args.host}:{args.port}{args.path}")
        print("Note: Some clients require a trailing slash in the endpoint URL.")

        # Build a fresh FastMCP configured for HTTP
        streamable_mcp = FastMCP(
            "fmp",
            dependencies=["httpx"],
            stateless_http=args.stateless,
            json_response=args.json_response,
        )

        # Register only the allowed tools on the HTTP instance
        streamable_mcp.tool()(company_profile)
        streamable_mcp.tool()(income_statement)
        streamable_mcp.tool()(balance_sheet)
        streamable_mcp.tool()(cash_flow)
        streamable_mcp.tool()(financial_ratios)
        streamable_mcp.tool()(historical_price_eod_full)
        streamable_mcp.tool()(earnings_call_transcript)
        streamable_mcp.tool()(economic_indicators)
        streamable_mcp.tool()(economic_calendar)
        streamable_mcp.tool()(stock_news_latest)
        streamable_mcp.tool()(stock_news_search)
        streamable_mcp.tool()(insider_trading_latest)
        streamable_mcp.tool()(ping)
        streamable_mcp.tool()(when_should_i_use_fmp)

        # Register resource & prompt so clients can see global guidance
        streamable_mcp.resource("fmp:readme")(fmp_readme)
        streamable_mcp.prompt("how_to_use_fmp")(how_to_use_fmp)

        # ASGI app & health route
        app = streamable_mcp.streamable_http_app()
        from starlette.routing import Route

        async def health_check(request):
            return JSONResponse({"status": "healthy", "service": "fmp-mcp-server"})

        app.router.routes.insert(0, Route("/health", health_check, methods=["GET"]))
        uvicorn.run(app, host=args.host, port=args.port)
        return

    if args.transport == "sse":
        print("[fmp-mcp] Transport: sse (streamable HTTP)")
        print("[fmp-mcp] Try connecting to one of these paths: /mcp/  /sse/  /events/")
        mcp.run(transport="sse")
        return

    print("[fmp-mcp] Transport: stdio")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
