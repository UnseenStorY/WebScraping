# 🏠 Group Accommodation Scraper

> A high-performance async web scraper for [groupaccommodation.com](https://www.groupaccommodation.com) — built with **Python + Playwright**.

---

## 📌 What It Does

This project scrapes the **Hen Party Houses** listing from `groupaccommodation.com`.

It extracts property data — title, facilities, and page URL — and saves everything to a clean **CSV file**.

---

## ⚙️ How It Works

The scraper runs in **two phases**:

### Phase 1 — Link Gathering
1. Opens the listing page
2. Auto-accepts cookie consent
3. Scrolls down fully to trigger lazy-loaded content
4. Collects all property card URLs from the page

### Phase 2 — Parallel Scraping
1. Spins up a **pool of 10 browser contexts**
2. Scrapes all collected URLs **concurrently** using `asyncio`
3. From each property page, extracts:
   - `Title` — Property name
   - `Facilities` — Amenities listed on the page
   - `Page` — Source URL
4. Writes all results to `GrAccommodation.csv`

> Concurrency is controlled via an `asyncio.Semaphore(10)` + a reusable context pool — keeping it fast without hammering the server.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `Python 3.10+` | Core language |
| `Playwright (async)` | Browser automation |
| `asyncio` | Concurrent scraping |
| `csv.DictWriter` | CSV output |

---

## 🚀 Setup & Run

**1. Install dependencies**
```bash
uv add playwright
uv run playwright install
uv sync
```

**2. Run the scraper**
```bash
uv run scraper.py
```

**3. Output**

Results saved to:
```
GrAccommodation.csv
```

---
