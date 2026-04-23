#!/usr/bin/env /opt/homebrew/bin/python3.13
"""
Scrape subscription box detail data from mysubscriptionaddiction.com /b/<slug> pages.
Uses __NEXT_DATA__ JSON for structured fields. Output: data/raw_boxes.jsonl
"""
import asyncio, json, re, time, argparse, os, sys

sys.path.insert(0, '/Users/c/starmap/scripts')
try:
    from rate_limit_guard import RateLimitGuard, RateLimitExit
    HAS_GUARD = True
except Exception:
    HAS_GUARD = False
    class RateLimitExit(Exception): pass

NEXT_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
TITLE_RE = re.compile(r'<title>(.*?)</title>', re.S)
DESC_RE = re.compile(r'<meta name="description" content="([^"]+)"')

def extract(url, html):
    rec = {"url": url, "slug": url.rstrip("/").split("/")[-1]}
    m = NEXT_RE.search(html)
    if m:
        try:
            data = json.loads(m.group(1))
            brand = data.get("props", {}).get("pageProps", {}).get("brand", {})
            if brand:
                rec["name"] = brand.get("name")
                rec["image"] = brand.get("imageUrl")
                rec["rating"] = brand.get("overallRating")
                rec["numRatings"] = brand.get("numRatings")
                rec["numReviews"] = brand.get("numReviews")
                rec["buyLink"] = brand.get("buyLink")
                rec["heading"] = brand.get("brandPageHeading")
                rec["subheading"] = brand.get("brandPageSubheading")
                rec["canonicalUrl"] = brand.get("canonicalUrl")
                # content blocks — text/HTML
                blocks = []
                for k in brand:
                    if k.startswith("brandPageContentBlock") and not k.endswith("Headers") and brand[k]:
                        blocks.append(brand[k])
                if blocks:
                    rec["content"] = "\n\n".join(b for b in blocks if isinstance(b, str))
        except Exception as e:
            rec["_parse_error"] = str(e)
    # JSON-LD fallback (Product schema)
    for ld in LD_RE.findall(html):
        try:
            obj = json.loads(ld)
            objs = obj if isinstance(obj, list) else [obj]
            for o in objs:
                t = o.get("@type")
                if t in ("Product", "Service"):
                    rec.setdefault("name", o.get("name"))
                    rec.setdefault("image", o.get("image"))
                    if "aggregateRating" in o:
                        ar = o["aggregateRating"]
                        rec.setdefault("rating", ar.get("ratingValue"))
                        rec.setdefault("numRatings", ar.get("ratingCount") or ar.get("reviewCount"))
                    rec.setdefault("description", o.get("description"))
                    if "offers" in o:
                        offers = o["offers"]
                        if isinstance(offers, dict):
                            rec.setdefault("price", offers.get("price"))
                            rec.setdefault("priceCurrency", offers.get("priceCurrency"))
        except Exception:
            pass
    mt = TITLE_RE.search(html)
    if mt: rec.setdefault("title", mt.group(1).strip())
    md_ = DESC_RE.search(html)
    if md_: rec.setdefault("description", md_.group(1).strip())
    return rec

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--urls", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--per-page-timeout", type=int, default=15)
    ap.add_argument("--skip-existing", action="store_true")
    args = ap.parse_args()

    with open(args.urls) as f:
        urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    done = set()
    if args.skip_existing and os.path.exists(args.output):
        with open(args.output) as f:
            for line in f:
                try: done.add(json.loads(line)["url"])
                except: pass
    remaining = [u for u in urls if u not in done]
    print(f"Total {len(urls)} | Done {len(done)} | Remaining {len(remaining)} | budget {args.timeout}s")

    if not remaining:
        print("Nothing to scrape.")
        return

    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
    cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    guard = RateLimitGuard(max_consecutive_failures=3, slowdown_factor=5.0) if HAS_GUARD else None
    start = time.time()
    ok = 0
    fail = 0

    out_f = open(args.output, "a")
    try:
        async with AsyncWebCrawler() as crawler:
            for url in remaining:
                elapsed = time.time() - start
                if args.timeout - elapsed < 5:
                    print(f"⏰ Time budget exhausted ({elapsed:.0f}s). Stopping.")
                    break
                if guard:
                    try: guard.before_request()
                    except RateLimitExit:
                        print("RATE_LIMITED_EXIT")
                        break
                t0 = time.time()
                try:
                    r = await asyncio.wait_for(crawler.arun(url=url, config=cfg), timeout=args.per_page_timeout)
                    if not r or not r.html:
                        fail += 1
                        if guard: guard.record_failure(error="no html")
                        print(f"  ✗ {url} (no html)")
                        continue
                    rec = extract(url, r.html)
                    out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    out_f.flush()
                    ok += 1
                    if guard: guard.record_success(elapsed=time.time() - t0)
                    print(f"  ✓ {url} → {rec.get('name','?')} (rating={rec.get('rating')}) [{ok}/{len(remaining)}]")
                except asyncio.TimeoutError:
                    fail += 1
                    if guard: guard.record_failure(error="timeout")
                    print(f"  ✗ {url} (timeout)")
                except RateLimitExit:
                    print("RATE_LIMITED_EXIT")
                    break
                except Exception as e:
                    fail += 1
                    if guard: guard.record_failure(error=str(e))
                    print(f"  ✗ {url} ({e})")
    finally:
        out_f.close()
        if guard: guard.print_summary()
        print(f"\nDone: ok={ok} fail={fail} in {time.time()-start:.0f}s → {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
