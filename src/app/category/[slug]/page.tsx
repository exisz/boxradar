import boxes from "@/data/boxes.json";
import type { Box } from "@/types/box";
import Link from "next/link";
import type { Metadata } from "next";

const allBoxes = boxes as Box[];

const slugify = (s: string) =>
  s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

const categories = Array.from(new Set(allBoxes.map((b) => b.category))).sort();

export function generateStaticParams() {
  return categories.map((c) => ({ slug: slugify(c) }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const cat = categories.find((c) => slugify(c) === slug);
  if (!cat) return { title: "Category Not Found — BoxRadar" };
  const count = allBoxes.filter((b) => b.category === cat).length;
  return {
    title: `Best ${cat} Subscription Boxes (${count}+ Compared) — BoxRadar`,
    description: `Compare the best ${cat.toLowerCase()} subscription boxes. Pricing, ratings, and reviews of ${count} ${cat.toLowerCase()} boxes side-by-side.`,
    openGraph: {
      title: `Best ${cat} Subscription Boxes — BoxRadar`,
      description: `Compare ${count} top ${cat.toLowerCase()} subscription boxes by price, rating, and frequency.`,
      type: "website",
    },
  };
}

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const cat = categories.find((c) => slugify(c) === slug);

  if (!cat) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Category Not Found</h1>
          <Link href="/" className="text-indigo-600 hover:underline">
            ← Back to all boxes
          </Link>
        </div>
      </main>
    );
  }

  const list = allBoxes
    .filter((b) => b.category === cat)
    .sort((a, b) => b.rating - a.rating);

  const itemListJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: `Best ${cat} Subscription Boxes`,
    numberOfItems: list.length,
    itemListElement: list.map((b, i) => ({
      "@type": "ListItem",
      position: i + 1,
      url: `https://boxradar-roller.vercel.app/box/${b.id}`,
      name: b.name,
    })),
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(itemListJsonLd) }}
      />

      <section className="bg-gradient-to-br from-indigo-600 to-purple-700 text-white py-12 px-4">
        <div className="max-w-5xl mx-auto">
          <Link href="/" className="text-white/80 hover:text-white text-sm">
            ← All Boxes
          </Link>
          <h1 className="text-3xl md:text-4xl font-bold mt-3 mb-2">
            Best {cat} Subscription Boxes
          </h1>
          <p className="text-lg opacity-90">
            {list.length} {cat.toLowerCase()} subscription boxes compared, ranked by user rating.
          </p>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-4 py-8">
        <ol className="space-y-4">
          {list.map((box, idx) => {
            const domain = (() => {
              try {
                return new URL(box.url).hostname;
              } catch {
                return "";
              }
            })();
            const logo = domain
              ? `https://www.google.com/s2/favicons?domain=${domain}&sz=128`
              : "";
            return (
              <li key={box.id}>
                <Link
                  href={`/box/${box.id}`}
                  className="flex items-start gap-4 bg-white rounded-xl shadow-sm border p-5 hover:shadow-md transition"
                >
                  <div className="text-2xl font-bold text-indigo-600 w-10 flex-shrink-0">
                    #{idx + 1}
                  </div>
                  {logo && (
                    <img
                      src={logo}
                      alt={`${box.name} logo`}
                      width={48}
                      height={48}
                      className="w-12 h-12 rounded-lg border bg-white flex-shrink-0"
                      loading="lazy"
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-baseline justify-between gap-2 mb-1">
                      <h2 className="text-lg font-semibold text-gray-900">
                        {box.name}
                      </h2>
                      <span className="text-sm font-medium text-indigo-600">
                        ${box.price}/{box.frequency.toLowerCase()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                      {box.description}
                    </p>
                    <div className="flex items-center gap-1 text-sm">
                      <span className="text-yellow-500">
                        {"★".repeat(Math.round(box.rating))}
                      </span>
                      <span className="text-gray-500">{box.rating}/5</span>
                    </div>
                  </div>
                </Link>
              </li>
            );
          })}
        </ol>

        <div className="mt-12 border-t pt-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Other Categories
          </h2>
          <div className="flex flex-wrap gap-2">
            {categories
              .filter((c) => c !== cat)
              .map((c) => (
                <Link
                  key={c}
                  href={`/category/${slugify(c)}`}
                  className="px-4 py-2 bg-white border rounded-lg text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-300 transition"
                >
                  {c}
                </Link>
              ))}
          </div>
        </div>
      </section>

      <footer className="bg-gray-900 text-gray-400 py-8 px-4 mt-16">
        <div className="max-w-5xl mx-auto text-center text-sm space-y-2">
          <p>
            © {new Date().getFullYear()} BoxRadar. Compare subscription boxes
            with confidence.
          </p>
          <p>
            A{" "}
            <a
              href="https://rollersoft.com.au"
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-400 hover:text-indigo-300"
            >
              Rollersoft
            </a>{" "}
            project.
          </p>
        </div>
      </footer>
    </main>
  );
}
