"use client";

import { Bot } from "lucide-react";

export default function TypingIndicator() {
  return (
    <div className="flex gap-3 w-full flex-row animate-fade-in-up opacity-0">
      <div className="shrink-0 w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center shadow-sm">
        <Bot size={15} className="text-white" />
      </div>
      <div className="flex flex-col items-start">
        <span className="text-[10px] font-semibold text-slate-500 mb-1">Servio AI</span>
        <div className="px-4 py-3 bg-white border border-slate-200 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-1">
          <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:0ms]" />
          <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:150ms]" />
          <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  );
}
