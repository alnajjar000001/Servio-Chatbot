"use client";

import { useState, useCallback } from "react";
import Sidebar from "@/components/Sidebar";
import ChatArea from "@/components/ChatArea";
import type { Message, Attachment, CustomerData } from "@/types";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

function makeId() {
  return Math.random().toString(36).slice(2, 10);
}

// ─── Session context (mirrors backend SessionContext) ─────────────────────────
interface SessionContext {
  customer_id: string;
  customer_name: string;
  primary_location_id: string;
  customer_phone: string;
}

const EMPTY_SESSION: SessionContext = {
  customer_id: "",
  customer_name: "",
  primary_location_id: "",
  customer_phone: "",
};

interface BackendResponse {
  response: string;
  tool_calls: unknown[];
  customer_data: CustomerData | null;
  session_context: SessionContext;
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function Page() {
  const [customer, setCustomer] = useState<CustomerData | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<
    Array<{ role: string; content: string }>
  >([]);
  const [sessionContext, setSessionContext] = useState<SessionContext>(EMPTY_SESSION);

  const addMessage = useCallback(
    (role: "user" | "assistant", content: string, attachments: Attachment[] = []): Message => {
      const msg: Message = {
        id: makeId(),
        role,
        content,
        timestamp: new Date(),
        attachments,
      };
      setMessages((prev) => [...prev, msg]);
      return msg;
    },
    []
  );

  const handleSend = useCallback(
    async (content: string, attachments: Attachment[]) => {
      if (!content.trim() && attachments.length === 0) return;

      addMessage("user", content, attachments);
      setIsTyping(true);

      try {
        const res = await fetch(`${BACKEND_URL}/api/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: content,
            conversation_history: conversationHistory,
            session_context: sessionContext,
          }),
        });

        if (!res.ok) {
          const errorText = await res.text();
          throw new Error(`Backend returned ${res.status}: ${errorText}`);
        }

        const data: BackendResponse = await res.json();

        // Always persist the updated session context for the next request
        if (data.session_context) {
          setSessionContext(data.session_context);
        }

        // Smart merge: only replace a field if the new response has real content for it
        if (data.customer_data) {
          setCustomer((prev) => {
            if (!prev) return data.customer_data;
            const next = data.customer_data!;
            return {
              // Only swap profile if the new one has an actual name (avoids empty-object overwrite)
              profile: next.profile?.name ? next.profile : prev.profile,
              contracts: next.contracts?.length > 0 ? next.contracts : prev.contracts,
              orders: next.orders?.length > 0 ? next.orders : prev.orders,
              invoices: next.invoices?.length > 0 ? next.invoices : prev.invoices,
            };
          });
        }

        setConversationHistory((prev) => [
          ...prev,
          { role: "user", content },
          { role: "assistant", content: data.response },
        ]);

        setIsTyping(false);
        addMessage("assistant", data.response);
      } catch (err) {
        console.error("Chat error:", err);
        setIsTyping(false);
        addMessage(
          "assistant",
          "I'm having trouble connecting to the server right now. Please make sure the backend is running on port 8000 and try again."
        );
      }
    },
    [sessionContext, conversationHistory, addMessage]
  );

  const handleReset = useCallback(() => {
    setMessages([]);
    setCustomer(null);
    setIsTyping(false);
    setConversationHistory([]);
    setSessionContext(EMPTY_SESSION);
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-100">
      <Sidebar customer={customer} />
      <ChatArea
        messages={messages}
        isTyping={isTyping}
        onSend={handleSend}
        onReset={handleReset}
        customerName={customer?.profile.name}
      />
    </div>
  );
}
