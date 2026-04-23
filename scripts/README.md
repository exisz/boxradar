# BoxRadar scrape scripts

Source: mysubscriptionaddiction.com (Crawl4AI L0, no auth, fast).

## Pipeline

1. **`discover_urls.py`** — crawls a curated set of MSA category + best-of pages,
   extracts `/b/<slug>` links, dedupes → `scripts/box_urls.txt`.
   Currently yields ~28 unique boxes (most category pages SSR only ~7
   boxes per call; deeper discovery will need pagination handling or
   rendered-DOM crawling with Playwright).

2. **`scrape_boxes.py`** — fetches each `/b/<slug>` URL, parses
   `__NEXT_DATA__` JSON for structured fields (name, image URL, rating,
   numRatings, buy link, content blocks). Falls back to JSON-LD Product
   schema for price.
   - Output: `data/raw_boxes.jsonl`
   - Built-in `--timeout`, per-page timeout, `--skip-existing` resume,
     `rate_limit_guard` integration.

3. **`merge_boxes.py`** — reads `data/raw_boxes.jsonl`, maps slugs to
   site categories via `SLUG_CATEGORY` table, generates short
   description from HTML, dedupes against existing
   `src/data/boxes.json`, backfills `image` for already-present boxes,
   writes alphabetized output.

## Run

```bash
# 1. discover
/opt/homebrew/bin/python3.13 scripts/discover_urls.py

# 2. scrape (180s budget, resume-safe)
/opt/homebrew/bin/python3.13 scripts/scrape_boxes.py \
  --urls scripts/box_urls.txt \
  --output data/raw_boxes.jsonl \
  --timeout 180 --skip-existing

# 3. merge into site data
python3 scripts/merge_boxes.py
```

## Coverage

- 2026-04-23 (scrape-34): 25 → 46 boxes (+21 new with real ratings + product images).
- Target: 500+ for 50% coverage; 1000+ ideal.
- Next sessions: extend `discover_urls.py` (paginate category pages,
  scrape best-of listicle bodies for additional `/b/<slug>` mentions, or
  switch to Playwright for client-rendered list expansion).
