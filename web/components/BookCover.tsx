"use client";

import { useState } from "react";

const PALETTES = [
  "from-emerald-700 to-emerald-900",
  "from-sky-700 to-indigo-900",
  "from-amber-600 to-orange-800",
  "from-rose-700 to-rose-900",
  "from-violet-700 to-violet-900",
  "from-teal-600 to-cyan-900",
];

type Props = {
  id: number;
  title: string;
  author: string;
  coverUrl?: string | null;
  /** "card" for the shelf, "detail" for the book page, "thumb" for the cart */
  size?: "card" | "detail" | "thumb";
};

export default function BookCover({ id, title, author, coverUrl, size = "card" }: Props) {
  const [failed, setFailed] = useState(false);
  const box =
    size === "thumb" ? "h-20 w-14 text-[8px]" : size === "detail" ? "aspect-[2/3] w-full max-w-[16rem] text-base" : "aspect-[2/3] w-full text-sm";

  // Medium images are plenty for shelves and the cart; the book page uses the large one.
  const src = coverUrl && size !== "detail" ? coverUrl.replace("-L.jpg", "-M.jpg") : coverUrl;

  if (!src || failed) {
    // Styled placeholder cover (used when a book has no picture or the picture cannot load)
    return (
      <div
        role="img"
        aria-label={`${title} by ${author}`}
        className={`${box} flex shrink-0 flex-col items-center justify-center overflow-hidden rounded bg-gradient-to-br ${PALETTES[id % PALETTES.length]} p-2 text-center text-white shadow`}
      >
        <span className="line-clamp-4 font-semibold leading-tight">{title}</span>
        {size !== "thumb" && <span className="mt-2 line-clamp-2 text-[0.7em] opacity-90">{author}</span>}
      </div>
    );
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={`Cover of ${title} by ${author}`}
      loading="lazy"
      onError={() => setFailed(true)}
      className={`${box} shrink-0 rounded bg-stone-100 object-cover shadow`}
    />
  );
}
