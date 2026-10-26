# Pytch MCP Server 🚀

[![MCP Standard](https://img.shields.io/badge/MCP-2.0-blue.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Official **Model Context Protocol (MCP)** server for [Pytch](https://pytch.cc) — the autonomous AI PR & Journalist Outreach platform.

Connect Pytch natively to **Claude Desktop**, **Cursor**, **Claude Code**, **Antigravity**, or your custom AI agents to automate media outreach, run email deliverability audits, track AI brand visibility across LLMs, and find relevant tech journalists.

---

## 🌟 Key Features

* **🛡️ F6 Deliverability Health & DNS Checker:** Full live DNS check for SPF (including RFC 7208 10-lookup limit), DMARC (`p=reject`/`quarantine`/`none`), DKIM selectors, MX providers, and DNSBL spam blacklists. Provides a 0–100 Deliverability Health Score and an automated 14-day safe warmup ramp schedule.
* **👁️ F9 AI Visibility Audit (GEO):** Evaluates how LLMs (ChatGPT, Perplexity, Claude, Gemini) see your brand, measures AI Share of Voice (SOV), extracts cited media sources, and matches them to journalists for targeted pitching.
* **📰 Journalist Discovery:** Search verified journalists and editors across tech and business publications by beat, topic, and media outlet.
* **✉️ PR Pitch Generation:** Generate concise, editorially calibrated pitch emails with concrete news hooks.
* **📊 Campaign Management:** Monitor live campaign statuses, email sends, replies, and deliverability metrics directly from your AI assistant.

---

## ⚡ Quickstart

### 1. Claude Desktop Setup

Add to your `claude_desktop_config.json`:

* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pytch": {
      "command": "uvx",
      "args": ["pytch-mcp"],
      "env": {
        "PYTCH_API_KEY": "pytch_live_your_secret_key_here",
        "PYTCH_API_URL": "https://api.pytch.cc"
      }
    }
  }
}
```

### 2. Cursor IDE Setup

In Cursor Settings → **Features** → **MCP** → **Add New MCP Server**:

* **Name:** `pytch`
* **Type:** `command`
* **Command:** `uvx pytch-mcp`
* **Env:**
  * `PYTCH_API_KEY`: `pytch_live_your_key`

Or configure `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "pytch": {
      "command": "uvx",
      "args": ["pytch-mcp"],
      "env": {
        "PYTCH_API_KEY": "pytch_live_your_secret_key_here"
      }
    }
  }
}
```

### 3. Claude Code Setup

Run directly in terminal:
```bash
claude mcp add pytch -- uvx pytch-mcp
```

### 4. Smithery (1-Click Install)

```bash
npx -y @smithery/cli install pytch-mcp --client claude
```

---

## 🛠️ Available MCP Tools

| Tool | Description | Parameters |
| :--- | :--- | :--- |
| `check_domain_deliverability` | Deep DNS check for SPF, DMARC, DKIM, MX, DNSBL, domain score (0–100), and warmup ramp plan | `domain` (required), `selector` (optional) |
| `check_ai_brand_visibility` | Run GEO / AI Visibility audit across LLMs, measure AI SOV, find cited outlets and journalists | `brand_name` (required), `category` (required), `website`, `competitors` |
| `search_journalists` | Find verified journalists by beat, topic or publication | `topic` (required), `outlet` (optional), `limit` (optional) |
| `list_pr_projects` | List user's active PR campaigns in Pytch | None |
| `get_project_results` | Get contacts and outreach stats for a project | `project_id` (required), `limit` (optional) |

---

## 🔑 Authentication

To obtain your Pytch API Key:
1. Log in to your [Pytch Dashboard](https://pytch.cc).
2. Go to **Settings** → **API Keys** (or call `GET /users/me/api-key`).
3. Copy your key (starts with `pytch_live_...`).
4. Set the `PYTCH_API_KEY` environment variable.

---

## 🐳 Docker Usage

```bash
docker build -t pytch-mcp .
docker run -i --rm -e PYTCH_API_KEY="pytch_live_..." pytch-mcp
```

---

## 🇷🇺 Документация на русском языке

Официальный MCP-сервер для платформы **Pytch** (автономный ИИ-агент для связей с общественностью и медиа-аутрича).

### Возможности:
1. **Проверка доставляемости (F6 Доставляемость):**
   * Мгновенный DNS-аудит SPF (с лимитом 10 DNS lookups RFC 7208), DMARC (`reject`/`quarantine`/`none`), DKIM-селекторов, MX-серверов и баз спама (DNSBL).
   * Расчет Health Score (0–100) и 14-дневного расписания плавного прогрева (Warmup Ramp Schedule).
2. **Видимость бренда в ИИ (F9 Видимость в ИИ / GEO):**
   * Проверка присутствия компании в ответах ChatGPT, Perplexity и Gemini.
   * Анализ источников (какие СМИ цитирует ИИ) и прямая подборка профилей журналистов из этих СМИ для питчинга.
3. **Поиск журналистов:**
   * Поиск по базе Pytch по теме, нише или конкретному изданию (TechCrunch, Forbes, Bloomberg и др.).
4. **Управление кампаниями:**
   * Получение статистики кампаний, статуса питчей и ответов журналистов прямо в окне Claude или Cursor.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
