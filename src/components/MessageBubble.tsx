"use client";

import { useEffect, useRef } from "react";
import { User, Bot, Paperclip } from "lucide-react";
import type { Message } from "@/types";

interface MessageBubbleProps {
  message: Message;
  isNew?: boolean;
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
}

export default function MessageBubble({ message, isNew = false }: MessageBubbleProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isUser = message.role === "user";

  useEffect(() => {
    if (isNew && ref.current) {
      ref.current.classList.add("animate-fade-in-up");
    }
  }, [isNew]);

  return (
    <div
      ref={ref}
      className={`flex gap-3 w-full opacity-0 ${
        isUser ? "flex-row-reverse" : "flex-row"
      } animate-fade-in-up`}
    >
      {/* Avatar */}
      <div
        className={`shrink-0 w-8 h-8 rounded-xl flex items-center justify-center shadow-sm ${
          isUser ? "bg-slate-700" : "bg-blue-600"
        }`}
      >
        {isUser ? (
          <User size={15} className="text-white" />
        ) : (
          <Bot size={15} className="text-white" />
        )}
      </div>

      {/* Bubble */}
      <div className={`flex flex-col max-w-[75%] ${isUser ? "items-end" : "items-start"}`}>
        <div className={`flex items-center gap-2 mb-1 ${isUser ? "flex-row-reverse" : ""}`}>
          <span className="text-[10px] font-semibold text-slate-500">
            {isUser ? "You" : "Servio AI"}
          </span>
          <span className="text-[9px] text-slate-400">{formatTime(message.timestamp)}</span>
        </div>

        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
            isUser
              ? "bg-blue-600 text-white rounded-tr-sm"
              : "bg-white text-slate-700 border border-slate-200 rounded-tl-sm"
          }`}
        >
          {message.content}

          {message.attachments && message.attachments.length > 0 && (
            <div className="mt-2 space-y-1">
              {message.attachments.map((att) => (
                <div
                  key={att.id}
                  className={`flex items-center gap-2 text-[11px] px-2 py-1.5 rounded-lg ${
                    isUser ? "bg-blue-500/50 text-blue-100" : "bg-slate-100 text-slate-600"
                  }`}
                >
                  <Paperclip size={11} />
                  <span className="truncate">{att.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
