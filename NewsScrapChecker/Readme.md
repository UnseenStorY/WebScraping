# 📰 EINPresswire Media Directory Scraper

> Scrapes multiple news site pages from [einpresswire.com](https://www.einpresswire.com) World Media Directory, checks each site's scraping permission via `robots.txt`, and generates a **CSV report**.

---

## 📌 What It Does

- Crawls **multiple pages** of the EINPresswire World Media Directory
- Extracts all listed news site profile links
- Visits each profile to get site details
- Checks every site's `robots.txt` to determine if scraping is allowed
- Outputs a clean **CSV report** — one row per news site

---

## ⚙️ How It Works

### Phase 1 — Link Gathering (Multi-Page)
1. Iterates through **multiple directory pages**
2. Scrapes all news site profile URLs from Column 1 and Column 2 on each page
3. Builds a complete list of all profile URLs

### Phase 2 — Parallel Detail Scraping
1. Concurrently visits each profile URL using **3 parallel browser contexts** (`asyncio.Semaphore(3)`)
2. Uses spoofed Chrome headers to avoid bot detection
3. Extracts from each profile:
   - `Location` — Location of the news site
   - `Website` — Name of the news site
   - `Front_Page_URL` — Homepage link

### Phase 3 — robots.txt Scraping Check
1. Fetches `/robots.txt` for every extracted site
2. Checks if wildcard agent (`*`) is permitted
3. Tags each site: `Yes` (allowed) or `No` (blocked)

### Phase 4 — CSV Report
- Saves the final report to `news_sites_report.csv`

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `Python 3.10+` | Core language |
| `Playwright (async)` | Browser automation |
| `asyncio` | Concurrent scraping |
| `urllib.robotparser` | robots.txt compliance check |
| `csv` | CSV report output |

---

## 🚀 Setup & Run

**1. Install `uv`** (if not already installed)
```bash
curl -Lsf https://astral.sh/uv/install.sh | sh
```

**2. Create project & virtual environment**
```bash
uv init einpresswire-scraper
cd einpresswire-scraper
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

**3. Install dependencies**
```bash
uv add playwright openpyxl
uv run playwright install
```

**4. Run the scraper**
```bash
uv run scraper.py
```

**5. Output**
```
news_sites_report.csv
```

---

## 📁 CSV Report Format

| Column | Description |
|---|---|
| `State` | Location of the news outlet |
| `Website` | Name of the news site |
| `Front_Page_URL` | Homepage link |
| `Allow Scraping` | `Yes` or `No` based on robots.txt |

---

## 📝 Notes

- Runs **headless** — no browser window opens
- Semaphore set to `3` — keeps requests conservative to avoid bans
- Sites with missing/broken `robots.txt` are assumed **scrapable** by default
- Change `base_url` or page range to target other states or pages

---
