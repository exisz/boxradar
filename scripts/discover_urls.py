#!/usr/bin/env /opt/homebrew/bin/python3.13
"""
Discover subscription box detail URLs from mysubscriptionaddiction.com.
Crawls a few directory/category pages and extracts /boxes/<slug> style links.
Output: scripts/box_urls.txt (one URL per line, deduped)
"""
import asyncio, re, os, sys, time

SEEDS = [
    "https://www.mysubscriptionaddiction.com/category/all-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/best-monthly-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/best-food-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/best-coffee-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/best-clothing-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/best-pet-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/best-dog-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/best-baby-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/best-vitamin-supplement-subscriptions",
    "https://www.mysubscriptionaddiction.com/best-beer-month-clubs",
    "https://www.mysubscriptionaddiction.com/best-plus-size-clothing-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/the-best-tea-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/plant-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/self-care-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/clothing-rental-subscriptions",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-boxes-for-women",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-boxes-for-men",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-boxes-for-kids",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-boxes-for-teens",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-boxes-for-cats",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-meal-kit-delivery-services",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-snack-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-wine-clubs",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-personal-styling-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-womens-clothing-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-mens-fashion-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-kids-clothing-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-beauty-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-makeup-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-skincare-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-jewelry-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-home-decor-and-supplies-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-book-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-craft-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-fitness-boxes",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/best-wellness-subscription-boxes-readers-choice",
    "https://www.mysubscriptionaddiction.com/best-subscription-boxes/the-top-10-tech-subscription-boxes-for-home-gadgets-in-2023",
    "https://www.mysubscriptionaddiction.com/category/subscription-boxes-for-women",
    "https://www.mysubscriptionaddiction.com/category/subscription-boxes-for-men-2",
    "https://www.mysubscriptionaddiction.com/category/subscription-boxes-for-kids",
    "https://www.mysubscriptionaddiction.com/category/beauty-subscription-boxes-2",
    "https://www.mysubscriptionaddiction.com/category/clothing-subscription-boxes",
    "https://www.mysubscriptionaddiction.com/category/food-subscription-boxes-2",
]

OUT = os.path.join(os.path.dirname(__file__), "box_urls.txt")
TIMEOUT = 150  # seconds total

# Pattern for box detail pages on MSA: typically /boxes/<slug>/
# Box detail pages live under /b/<slug> (no further path segments). Exclude /b/<slug>/spoilers etc.
URL_RE = re.compile(r'https?://(?:www\.)?mysubscriptionaddiction\.com/b/[a-z0-9][a-z0-9-]*/?(?=["\s<])', re.I)

async def main():
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
    cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    found = set()
    start = time.time()

    async with AsyncWebCrawler() as crawler:
        for seed in SEEDS:
            if time.time() - start > TIMEOUT:
                print("⏰ Timeout while discovering")
                break
            try:
                result = await asyncio.wait_for(
                    crawler.arun(url=seed, config=cfg), timeout=20
                )
                html = (result.html or "") + " " + (result.markdown or "")
                hits = URL_RE.findall(html)
                for h in hits:
                    h = h.rstrip('/')
                    # only single-segment /b/slug
                    tail = h.split('/b/', 1)[1]
                    if '/' in tail:
                        continue
                    found.add(h)
                print(f"  {seed} → {len(hits)} hits, total {len(found)}")
            except Exception as e:
                print(f"  {seed} → ERROR {e}")

    with open(OUT, "w") as f:
        for u in sorted(found):
            f.write(u + "\n")
    print(f"\n✅ Saved {len(found)} unique box URLs → {OUT}")

if __name__ == "__main__":
    asyncio.run(main())
