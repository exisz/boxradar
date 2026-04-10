import boxes from "@/data/boxes.json";
import type { Box } from "@/types/box";
import Link from "next/link";
import type { Metadata } from "next";

const allBoxes = boxes as Box[];

export function generateStaticParams() {
  return allBoxes.map((b) => ({ id: b.id }));
}

export function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  return params.then(({ id }) => {
    const box = allBoxes.find((b) => b.id === id);
    if (!box) return { title: "Box Not Found — BoxRadar" };
    return {
      title: `${box.name} Review & Pricing — BoxRadar`,
      description: `${box.description} Starting at $${box.price}/${box.frequency.toLowerCase()}.`,
    };
  });
}

export default async function BoxPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const box = allBoxes.find((b) => b.id === id);

  if (!box) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Box Not Found</h1>
          <Link href="/" className="text-indigo-600 hover:underline">← Back to all boxes</Link>
        </div>
      </main>
    );
  }

  const similar = allBoxes.filter((b) => b.category === box.category && b.id !== box.id).slice(0, 3);
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: box.name,
    description: box.description,
    url: box.url,
    aggregateRating: { "@type": "AggregateRating", ratingValue: box.rating, bestRating: 5, ratingCount: 100 },
    offers: { "@type": "Offer", price: box.price, priceCurrency: "USD", availability: "https://schema.org/InStock" },
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <div className="bg-gradient-to-br from-indigo-600 to-purple-700 text-white py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <Link href="/" className="text-white/80 hover:text-white text-sm">← All Boxes</Link>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 -mt-8">
        <div className="bg-white rounded-xl shadow-sm border p-8">
          <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{box.name}</h1>
              <div className="flex gap-2">
                <span className="text-sm bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full">{box.category}</span>
                <span className="text-sm bg-gray-100 text-gray-600 px-3 py-1 rounded-full">{box.frequency}</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-indigo-600">${box.price}</div>
              <div className="text-sm text-gray-500">per {box.frequency.toLowerCase()}</div>
              <div className="flex items-center gap-1 mt-1 justify-end">
                <span className="text-yellow-500">{"★".repeat(Math.round(box.rating))}</span>
                <span className="text-sm text-gray-500">{box.rating}/5</span>
              </div>
            </div>
          </div>

          <p className="text-gray-700 text-lg mb-6">{box.description}</p>

          <a
            href={box.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition"
          >
            Visit {box.name} →
          </a>
        </div>

        {similar.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Similar Boxes in {box.category}</h2>
            <div className="grid gap-4 md:grid-cols-3">
              {similar.map((s) => (
                <Link key={s.id} href={`/box/${s.id}`} className="bg-white rounded-xl shadow-sm border p-4 hover:shadow-md transition block">
                  <h3 className="font-semibold text-gray-900">{s.name}</h3>
                  <p className="text-sm text-indigo-600 font-medium">${s.price}/{s.frequency.toLowerCase()}</p>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">{s.description}</p>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      <footer className="bg-gray-900 text-gray-400 py-8 px-4 mt-16">
        <div className="max-w-5xl mx-auto text-center text-sm">
          <p>© {new Date().getFullYear()} BoxRadar. Compare subscription boxes with confidence.</p>
        </div>
      </footer>
    </main>
  );
}
