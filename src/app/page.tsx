"use client";

import { useState, useMemo } from "react";
import boxes from "@/data/boxes.json";
import type { Box } from "@/types/box";
import Link from "next/link";

const allBoxes = boxes as Box[];
const categories = Array.from(new Set(allBoxes.map((b) => b.category))).sort();

type SortKey = "name" | "price" | "rating";
type SortDir = "asc" | "desc";

export default function Home() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("rating");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  const filtered = useMemo(() => {
    let list = allBoxes;
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(
        (b) => b.name.toLowerCase().includes(q) || b.description.toLowerCase().includes(q)
      );
    }
    if (category) list = list.filter((b) => b.category === category);
    list.sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (typeof av === "string" && typeof bv === "string")
        return sortDir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
      return sortDir === "asc" ? (av as number) - (bv as number) : (bv as number) - (av as number);
    });
    return list;
  }, [search, category, sortKey, sortDir]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir(sortDir === "asc" ? "desc" : "asc");
    else { setSortKey(key); setSortDir(key === "price" ? "asc" : "desc"); }
  };

  const arrow = (key: SortKey) => sortKey === key ? (sortDir === "asc" ? " ↑" : " ↓") : "";

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Hero */}
      <section className="bg-gradient-to-br from-indigo-600 to-purple-700 text-white py-16 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">📦 BoxRadar</h1>
          <p className="text-xl opacity-90 mb-8">
            Compare subscription boxes across {categories.length}+ categories. Find your perfect box.
          </p>
          <div className="max-w-xl mx-auto">
            <input
              type="text"
              placeholder="Search boxes..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-4 py-3 rounded-lg text-gray-900 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>
        </div>
      </section>

      {/* Filters & Results */}
      <section className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex flex-wrap gap-2 mb-6">
          <button
            onClick={() => setCategory("")}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition ${
              !category ? "bg-indigo-600 text-white" : "bg-white text-gray-700 hover:bg-gray-100 border"
            }`}
          >
            All ({allBoxes.length})
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition ${
                category === cat ? "bg-indigo-600 text-white" : "bg-white text-gray-700 hover:bg-gray-100 border"
              }`}
            >
              {cat} ({allBoxes.filter((b) => b.category === cat).length})
            </button>
          ))}
        </div>

        <div className="flex gap-4 mb-4 text-sm">
          <button onClick={() => toggleSort("name")} className="font-medium text-gray-600 hover:text-indigo-600">
            Name{arrow("name")}
          </button>
          <button onClick={() => toggleSort("price")} className="font-medium text-gray-600 hover:text-indigo-600">
            Price{arrow("price")}
          </button>
          <button onClick={() => toggleSort("rating")} className="font-medium text-gray-600 hover:text-indigo-600">
            Rating{arrow("rating")}
          </button>
        </div>

        <p className="text-sm text-gray-500 mb-4">{filtered.length} boxes found</p>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((box) => (
            <Link
              key={box.id}
              href={`/box/${box.id}`}
              className="bg-white rounded-xl shadow-sm border p-5 hover:shadow-md transition block"
            >
              <div className="flex justify-between items-start mb-2">
                <h2 className="text-lg font-semibold text-gray-900">{box.name}</h2>
                <span className="text-sm font-medium text-indigo-600">${box.price}</span>
              </div>
              <div className="flex gap-2 mb-2">
                <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full">
                  {box.category}
                </span>
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                  {box.frequency}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">{box.description}</p>
              <div className="flex items-center gap-1">
                <span className="text-yellow-500">{"★".repeat(Math.round(box.rating))}</span>
                <span className="text-sm text-gray-500">{box.rating}/5</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-8 px-4 mt-16">
        <div className="max-w-5xl mx-auto text-center text-sm">
          <p>© {new Date().getFullYear()} BoxRadar. Compare subscription boxes with confidence.</p>
        </div>
      </footer>
    </main>
  );
}
