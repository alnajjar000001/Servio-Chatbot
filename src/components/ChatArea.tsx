"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Bot, MoreHorizontal, RefreshCw, Sparkles } from "lucide-react";
import type { Message, Attachment } from "@/types";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import ChatInput from "./ChatInput";

const WELCOME_SUGGESTIONS = [
  "Check my active contracts",
  "Show my pending invoices",
  "Report a maintenance issue",
  "Update my contact information",
];

interface ChatAreaProps {
  messages: Message[];
  isTyping: boolean;
  onSend: (content: string, attachments: Attachment[]) => void;
  onReset: () => void;
  customerName?: string;
}

export default function ChatArea({
  messages,
  isTyping,
  onSend,
  onReset,
  customerName,
}: ChatAreaProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [newMessageId, setNewMessageId] = useState<string | null>(null);

  useEffect(() => {
    if (messages.length > 0) {
      const last = messages[messages.length - 1];
      setNewMessageId(last.id);
    }
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSuggestion = useCallback(
    (text: string) => {
      onSend(text, []);
    },
    [onSend]
  );

  return (
    <div className="flex flex-col flex-1 h-full overflow-hidden bg-slate-50">
      {/* Top bar */}
      <header className="flex items-center justify-between px-5 py-4 bg-white border-b border-slate-200 shrink-0">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shadow-sm">
              <Bot size={18} className="text-white" />
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-400 rounded-full border-2 border-white" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-800">
              Servio AI Assistant
              {customerName && (
                <span className="ml-2 text-xs font-normal text-slate-400">
                  — chatting with{" "}
                  <span className="text-blue-500 font-medium">{customerName}</span>
                </span>
              )}
            </h2>
            <p className="text-[10px] text-emerald-500 font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full inline-block animate-pulse" />
              Online · Ready to help
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={onReset}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            title="Reset conversation"
          >
            <RefreshCw size={15} />
          </button>
          <button className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
            <MoreHorizontal size={15} />
          </button>
        </div>
      </header>

      {/* Message feed */}
      <div className="flex-1 overflow-y-auto px-5 py-6 space-y-5 scrollbar-thin">
        {messages.length === 0 ? (
          <WelcomeScreen onSuggestion={handleSuggestion} />
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} isNew={msg.id === newMessageId} />
            ))}
            {isTyping && <TypingIndicator />}
          </>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={onSend} disabled={isTyping} />
    </div>
  );
}

function WelcomeScreen({ onSuggestion }: { onSuggestion: (text: string) => void }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-8 py-12 gap-6">
      <div className="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-200">
        <Sparkles size={28} className="text-white" />
      </div>
      <div>
        <h3 className="text-lg font-bold text-slate-800 mb-1">Hello! I'm Servio AI</h3>
        <p className="text-sm text-slate-500 leading-relaxed max-w-sm">
          Your intelligent assistant for property and maintenance management. Ask me anything or pick
          a suggestion below.
        </p>
      </div>
      <div className="grid grid-cols-2 gap-2 w-full max-w-md">
        {WELCOME_SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onSuggestion(s)}
            className="text-left px-4 py-3 bg-white border border-slate-200 rounded-xl text-xs text-slate-600 font-medium hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700 transition-all shadow-sm"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
