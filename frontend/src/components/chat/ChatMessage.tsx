"use client";

import { ChatMessage as ChatMessageType } from "@/lib/store";
import ThoughtChain from "./ThoughtChain";

interface Props {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white rounded-br-md"
            : "glass rounded-bl-md"
        }`}
      >
        {/* Message content with basic markdown rendering */}
        <div className={`text-sm leading-relaxed whitespace-pre-wrap ${isUser ? "" : "prose prose-sm max-w-none"}`}>
          {message.content || (
            <span className="inline-flex items-center gap-1 text-gray-400">
              <span className="animate-pulse">●</span>
              <span className="animate-pulse" style={{ animationDelay: "0.2s" }}>●</span>
              <span className="animate-pulse" style={{ animationDelay: "0.4s" }}>●</span>
            </span>
          )}
        </div>

        {/* Thought chain for assistant messages */}
        {!isUser && message.thoughtChain && message.thoughtChain.length > 0 && (
          <div className="mt-2 border-t border-gray-200/30 pt-2">
            <ThoughtChain events={message.thoughtChain} />
          </div>
        )}
      </div>
    </div>
  );
}
