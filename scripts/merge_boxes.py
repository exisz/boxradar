#!/usr/bin/env python3
"""
Merge raw scraped boxes (data/raw_boxes.jsonl) with existing src/data/boxes.json.
- Map MSA categories to project categories (via slug heuristics + manual map).
- Keep existing boxes; add new ones (deduped by id/slug).
- Output: src/data/boxes.json (rewritten, deduped).
"""
import json, os, re, sys
from html import unescape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "data", "raw_boxes.jsonl")
DEST = os.path.join(ROOT, "src", "data", "boxes.json")

# Allowed categories (must match site's filter list)
CATEGORIES = ['Beauty','Books','Coffee & Tea','Fashion','Food & Meal Kits','Games & Puzzles','Geek & Gaming','Home & Garden','Kids','Lifestyle','Outdoor & Fitness','Pets','Self-Care','Snacks','Wine & Spirits']

# Manual category for the slugs we scraped from MSA
SLUG_CATEGORY = {
    "adore-me": "Fashion",
    "book-of-the-month": "Books",
    "bookroo": "Books",
    "boxycharm": "Beauty",
    "cate-chloe": "Fashion",  # jewelry → Fashion
    "causebox": "Lifestyle",
    "craft-beer-club": "Wine & Spirits",
    "curology": "Self-Care",
    "fabfitfun-vip-box": "Lifestyle",
    "glamour-jewelry-box": "Fashion",
    "hangsquad": "Lifestyle",
    "home-chef": "Food & Meal Kits",
    "hum-nutrition": "Self-Care",
    "hunt-a-killer": "Games & Puzzles",
    "ipsy": "Beauty",
    "ipsy-glam-bag-x": "Beauty",
    "kiwi-crate": "Kids",
    "kiwico-maker-crate": "Kids",
    "monthly-jewelry-tree": "Fashion",
    "once-upon-a-book-club": "Books",
    "owlcrate": "Books",
    "penny-grace": "Fashion",
    "stitch-fix": "Fashion",
    "wantable-fitness": "Outdoor & Fitness",
    "wantable-intimates": "Fashion",
    "wantable-style-edit": "Fashion",
    "we-craft-box": "Kids",
    "winc": "Wine & Spirits",
}

def strip_html(s):
    if not s: return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def short_desc(text, n=240):
    text = strip_html(text)
    if len(text) <= n: return text
    cut = text[:n]
    sp = cut.rfind(". ")
    if sp > 100: cut = cut[: sp + 1]
    return cut.strip()

def parse_price(p):
    if p is None or p == "": return None
    try: return float(p)
    except: return None

def main():
    existing = json.load(open(DEST))
    by_id = {b["id"]: b for b in existing}
    print(f"Existing: {len(existing)} boxes")

    added = 0
    updated_image = 0
    with open(RAW) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            r = json.loads(line)
            slug = r.get("slug")
            if not slug: continue
            name = r.get("name") or slug.replace("-", " ").title()
            category = SLUG_CATEGORY.get(slug, "Lifestyle")
            price = parse_price(r.get("price"))
            rating = r.get("rating") or 0
            try: rating = float(rating)
            except: rating = 0.0
            desc = short_desc(r.get("description") or r.get("subheading") or "")

            # external link: use MSA URL (they have affiliate buyLink but external buylink is too long; keep brand page)
            url = r.get("buyLink") or r.get("url")
            image = r.get("image")

            if slug in by_id:
                # backfill image / rating where missing
                b = by_id[slug]
                changed = False
                if not b.get("image") and image:
                    b["image"] = image; changed = True
                if (not b.get("description")) and desc:
                    b["description"] = desc; changed = True
                if changed: updated_image += 1
                continue

            box = {
                "id": slug,
                "name": name,
                "category": category,
                "price": price if price else 20,
                "frequency": "Monthly",
                "description": desc or f"{name} is a curated subscription box.",
                "rating": round(rating, 1) if rating else 0,
                "url": url,
            }
            if image:
                box["image"] = image
            by_id[slug] = box
            added += 1

    final = list(by_id.values())
    # sort by name for stable diffs
    final.sort(key=lambda b: b["name"].lower())
    with open(DEST, "w") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    print(f"Added: {added} | Updated existing: {updated_image} | Total now: {len(final)}")
    # category breakdown
    from collections import Counter
    print("Categories:", dict(Counter(b["category"] for b in final)))

if __name__ == "__main__":
    main()
