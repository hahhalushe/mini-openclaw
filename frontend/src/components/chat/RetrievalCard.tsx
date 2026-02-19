"use client";

import { useState } from "react";

interface Props {
  results: Array<{
    text: string;
    score?: number;
  }>;
}

export default function RetrievalCard({ results }: Props) {
  const [isOpen, setIsOpen] = useState(false);

  if (!results || results.length === 0) return null;

  return (
    <div className="rounded-lg bg-purple-50 p-2 text-xs">
      <div
        className="flex items-center gap-1.5 cursor-pointer text-purple-600"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="font-medium">RAG Retrieval</span>
        <span className="px-1.5 py-0.5 rounded-full bg-purple-100 text-purple-500 ml-1">
          {results.length} results
        </span>
        <span className="ml-auto">{isOpen ? "\u25BC" : "\u25B6"}</span>
      </div>

      {isOpen && (
        <div className="mt-2 space-y-2">
          {results.map((result, i) => (
            <div
              key={i}
              className="bg-white/60 rounded-md p-2 border border-purple-100"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-purple-700">Result {i + 1}</span>
                {result.score !== undefined && (
                  <span className="text-purple-400">
                    Score: {(result.score * 100).toFixed(1)}%
                  </span>
                )}
              </div>
              <p className="text-gray-600 whitespace-pre-wrap line-clamp-3">
                {result.text}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
