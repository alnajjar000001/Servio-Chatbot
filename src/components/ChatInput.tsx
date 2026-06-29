"use client";

import { useRef, useState, useCallback } from "react";
import { Paperclip, Send, X, FileText, Image } from "lucide-react";
import type { Attachment } from "@/types";

interface ChatInputProps {
  onSend: (content: string, attachments: Attachment[]) => void;
  disabled?: boolean;
}

function fileToAttachment(file: File): Attachment {
  const isImage = file.type.startsWith("image/");
  return {
    id: Math.random().toString(36).slice(2),
    name: file.name,
    type: isImage ? "image" : "document",
    url: URL.createObjectURL(file),
  };
}

export default function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [text, setText] = useState("");
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files ?? []);
      setAttachments((prev) => [...prev, ...files.map(fileToAttachment)]);
      if (fileInputRef.current) fileInputRef.current.value = "";
    },
    []
  );

  const removeAttachment = useCallback((id: string) => {
    setAttachments((prev) => prev.filter((a) => a.id !== id));
  }, []);

  const handleSend = useCallback(() => {
    const trimmed = text.trim();
    if (!trimmed && attachments.length === 0) return;
    onSend(trimmed, attachments);
    setText("");
    setAttachments([]);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [text, attachments, onSend]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleTextChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
  }, []);

  const canSend = (text.trim().length > 0 || attachments.length > 0) && !disabled;

  return (
    <div className="px-4 pb-4 pt-3 bg-white border-t border-slate-200">
      {/* Attachment previews */}
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3 px-1">
          {attachments.map((att) => (
            <div
              key={att.id}
              className="flex items-center gap-1.5 bg-slate-100 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-600 group"
            >
              {att.type === "image" ? (
                <Image size={12} className="text-blue-500 shrink-0" />
              ) : (
                <FileText size={12} className="text-blue-500 shrink-0" />
              )}
              <span className="max-w-[140px] truncate">{att.name}</span>
              <button
                onClick={() => removeAttachment(att.id)}
                className="ml-1 text-slate-400 hover:text-red-500 transition-colors"
                aria-label="Remove attachment"
              >
                <X size={11} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input row */}
      <div className="flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-2xl px-3 py-2.5 shadow-sm focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
        {/* Attach button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="shrink-0 w-8 h-8 flex items-center justify-center rounded-xl text-slate-400 hover:text-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-40"
          aria-label="Attach file"
        >
          <Paperclip size={17} />
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={handleFileChange}
          accept="image/*,.pdf,.doc,.docx,.txt,.xlsx,.csv"
        />

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleTextChange}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
          placeholder="Type a message… (Shift+Enter for new line)"
          className="flex-1 bg-transparent resize-none text-sm text-slate-700 placeholder:text-slate-400 outline-none leading-relaxed max-h-[140px] scrollbar-thin disabled:opacity-50"
        />

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={!canSend}
          className={`shrink-0 w-8 h-8 flex items-center justify-center rounded-xl transition-all ${
            canSend
              ? "bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md active:scale-95"
              : "bg-slate-200 text-slate-400 cursor-not-allowed"
          }`}
          aria-label="Send message"
        >
          <Send size={15} className={canSend ? "" : ""} />
        </button>
      </div>

      <p className="text-center text-[10px] text-slate-400 mt-2">
        Servio AI may make mistakes. Always verify critical information.
      </p>
    </div>
  );
}
