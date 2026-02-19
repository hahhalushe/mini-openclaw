"use client";

import { useState } from "react";
import { ThoughtEvent } from "@/lib/store";
import RetrievalCard from "./RetrievalCard";

interface Props {
  events: ThoughtEvent[];
}

export default function ThoughtChain({ events }: Props) {
  const [isOpen, setIsOpen] = useState(false);

  if (!events || events.length === 0) return null;

  return (
    <div className="mb-2">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-600 transition-colors"
      >
        <svg
          className={`w-3 h-3 transition-transform ${isOpen ? "rotate-90" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span className="font-medium">Thought Chain</span>
        <span className="px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-500">
          {events.length}
        </span>
      </button>

      {isOpen && (
        <div className="mt-2 ml-3 border-l-2 border-gray-200 pl-3 space-y-2">
          {events.map((event, i) => (
            <ThoughtEventItem key={i} event={event} />
          ))}
        </div>
      )}
    </div>
  );
}

function ThoughtEventItem({ event }: { event: ThoughtEvent }) {
  const [expanded, setExpanded] = useState(false);

  if (event.type === "retrieval") {
    return <RetrievalCard results={event.results || []} />;
  }

  const isStart = event.type === "tool_start";
  const color = isStart ? "text-blue-600 bg-blue-50" : "text-green-600 bg-green-50";
  const icon = isStart ? "\u25B6" : "\u2713";
  const label = isStart ? "Call" : "Result";

  return (
    <div className={`rounded-lg p-2 text-xs ${color}`}>
      <div
        className="flex items-center gap-1.5 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <span>{icon}</span>
        <span className="font-medium">{label}: {event.tool}</span>
        {!isStart && (
          <span className="text-gray-400 ml-auto">{expanded ? "\u25BC" : "\u25B6"}</span>
        )}
      </div>

      {isStart && event.input && (
        <pre className="mt-1 text-xs bg-white/50 rounded p-1.5 overflow-x-auto whitespace-pre-wrap">
          {typeof event.input === "string" ? event.input : JSON.stringify(event.input, null, 2)}
        </pre>
      )}

      {!isStart && expanded && event.output && (
        <pre className="mt-1 text-xs bg-white/50 rounded p-1.5 overflow-x-auto whitespace-pre-wrap max-h-40 overflow-y-auto">
          {event.output}
        </pre>
      )}
    </div>
  );
}
