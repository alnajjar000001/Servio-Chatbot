"use client";

import { useState } from "react";
import {
  User,
  Phone,
  Hash,
  MapPin,
  Building2,
  FileText,
  ShoppingBag,
  Receipt,
  ChevronDown,
  ChevronUp,
  Layers,
} from "lucide-react";
import type { CustomerData, Contract, Order, Invoice } from "@/types";
import StatusBadge from "./StatusBadge";

interface SidebarProps {
  customer: CustomerData | null;
}

type TabKey = "contracts" | "orders" | "invoices";

function SectionToggle({
  label,
  icon: Icon,
  children,
  defaultOpen = true,
}: {
  label: string;
  icon: React.ElementType;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 hover:bg-slate-100 transition-colors"
      >
        <span className="flex items-center gap-2 text-xs font-semibold text-slate-600 uppercase tracking-wider">
          <Icon size={13} className="text-blue-500" />
          {label}
        </span>
        {open ? (
          <ChevronUp size={14} className="text-slate-400" />
        ) : (
          <ChevronDown size={14} className="text-slate-400" />
        )}
      </button>
      {open && <div className="divide-y divide-slate-100">{children}</div>}
    </div>
  );
}

function ContractItem({ item }: { item: Contract }) {
  return (
    <div className="px-4 py-3 flex items-start justify-between gap-3 hover:bg-slate-50 transition-colors">
      <div className="min-w-0">
        <p className="text-xs font-medium text-slate-700 truncate">Contract No: {item.title}</p>
        <p className="text-[10px] text-slate-400 mt-0.5">
          {item.startDate} → {item.endDate}
        </p>
      </div>
      <StatusBadge status={item.status} variant="contract" />
    </div>
  );
}

function OrderItem({ item }: { item: Order }) {
  return (
    <div className="px-4 py-3 flex items-start justify-between gap-3 hover:bg-slate-50 transition-colors">
      <div className="min-w-0">
        <p className="text-xs font-medium text-slate-700 truncate">{item.description}</p>
        <p className="text-[10px] text-slate-400 mt-0.5">{item.date}</p>
      </div>
      <StatusBadge status={item.status} variant="order" />
    </div>
  );
}

function InvoiceItem({ item }: { item: Invoice }) {
  return (
    <div className="px-4 py-3 flex items-start justify-between gap-3 hover:bg-slate-50 transition-colors">
      <div className="min-w-0">
        <p className="text-xs font-medium text-slate-700 truncate">Invoice #{item.id}</p>
        <p className="text-[10px] text-slate-400 mt-0.5">Due: {item.dueDate}</p>
      </div>
      <div className="flex flex-col items-end gap-1">
        <span className="text-xs font-semibold text-slate-700">
          {item.currency} {item.amount.toFixed(3)}
        </span>
        <StatusBadge status={item.status} variant="invoice" />
      </div>
    </div>
  );
}

const TABS: { key: TabKey; label: string; icon: React.ElementType }[] = [
  { key: "contracts", label: "Contracts", icon: FileText },
  { key: "orders", label: "Orders", icon: ShoppingBag },
  { key: "invoices", label: "Invoices", icon: Receipt },
];

export default function Sidebar({ customer }: SidebarProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("contracts");

  if (!customer) {
    return (
      <aside className="flex flex-col w-80 min-w-[280px] max-w-[320px] bg-white border-r border-slate-200 h-full">
        {/* Header */}
        <div className="px-5 py-5 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shrink-0">
              <Layers size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-slate-800 tracking-tight">Servio</h1>
              <p className="text-[10px] text-slate-400">Property & Maintenance</p>
            </div>
          </div>
        </div>

        {/* Empty state */}
        <div className="flex-1 flex flex-col items-center justify-center px-6 text-center">
          <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-4">
            <User size={28} className="text-slate-300" />
          </div>
          <h3 className="text-sm font-semibold text-slate-600 mb-1">No active session</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Please provide your <span className="font-medium text-blue-500">Phone Number</span> or{" "}
            <span className="font-medium text-blue-500">Customer Code</span> to begin.
          </p>
        </div>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-slate-200">
          <p className="text-[10px] text-slate-400 text-center">
            Customer Context Dashboard
          </p>
        </div>
      </aside>
    );
  }

  const { profile, contracts, orders, invoices } = customer;
  const loc = profile.location ?? {};

  const tabContent: Record<TabKey, React.ReactNode> = {
    contracts:
      contracts.length === 0 ? (
        <p className="text-xs text-slate-400 px-4 py-4 text-center">No contracts found.</p>
      ) : (
        contracts.map((c) => <ContractItem key={c.id} item={c} />)
      ),
    orders:
      orders.length === 0 ? (
        <p className="text-xs text-slate-400 px-4 py-4 text-center">No orders found.</p>
      ) : (
        orders.map((o) => <OrderItem key={o.id} item={o} />)
      ),
    invoices:
      invoices.length === 0 ? (
        <p className="text-xs text-slate-400 px-4 py-4 text-center">No invoices found.</p>
      ) : (
        invoices.map((i) => <InvoiceItem key={i.id} item={i} />)
      ),
  };

  return (
    <aside className="flex flex-col w-80 min-w-[280px] max-w-[320px] bg-white border-r border-slate-200 h-full overflow-hidden">
      {/* Header */}
      <div className="px-5 py-5 border-b border-slate-200 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shrink-0">
            <Layers size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-800 tracking-tight">Servio</h1>
            <p className="text-[10px] text-slate-400">Property & Maintenance</p>
          </div>
        </div>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-thin">
        {/* Profile card */}
        <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl px-4 py-4 text-white shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
              <User size={20} className="text-white" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-bold truncate">{profile.name}</p>
              <p className="text-[10px] text-blue-200">Verified Customer</p>
            </div>
            <div className="ml-auto">
              <span className="inline-flex items-center gap-1 bg-emerald-400/20 text-emerald-200 text-[9px] font-semibold px-2 py-0.5 rounded-full ring-1 ring-emerald-400/30 uppercase tracking-wide">
                ● Active
              </span>
            </div>
          </div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <Hash size={11} className="text-blue-300 shrink-0" />
              <span className="text-[11px] text-blue-100 font-mono">{profile.code}</span>
            </div>
            <div className="flex items-center gap-2">
              <Phone size={11} className="text-blue-300 shrink-0" />
              <span className="text-[11px] text-blue-100 font-mono">{profile.phone}</span>
            </div>
          </div>
        </div>

        {/* Location */}
        <SectionToggle label="Primary Location" icon={MapPin}>
          <div className="px-4 py-3 space-y-2">
            <div className="grid grid-cols-2 gap-2">
              <InfoCell label="Area" value={loc.areaName} />
              <InfoCell label="Governorate" value={loc.governorate} />
              <InfoCell label="Block" value={loc.block} />
              <InfoCell label="Street" value={loc.street} />
              <InfoCell label="Building" value={loc.building} />
              <InfoCell label="Apartment" value={loc.apartment} />
            </div>
          </div>
        </SectionToggle>

        {/* Tabs: Contracts / Orders / Invoices */}
        <div className="border border-slate-200 rounded-xl overflow-hidden">
          <div className="flex border-b border-slate-200 bg-slate-50">
            {TABS.map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`flex-1 flex flex-col items-center gap-0.5 py-2.5 text-[10px] font-semibold uppercase tracking-wider transition-colors ${
                  activeTab === key
                    ? "bg-white text-blue-600 border-b-2 border-blue-500 shadow-sm"
                    : "text-slate-400 hover:text-slate-600"
                }`}
              >
                <Icon size={13} />
                {label}
              </button>
            ))}
          </div>
          <div className="divide-y divide-slate-100 max-h-64 overflow-y-auto">
            {tabContent[activeTab]}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-slate-200 shrink-0">
        <div className="flex items-center gap-2">
          <Building2 size={12} className="text-slate-400" />
          <p className="text-[10px] text-slate-400">Customer Context Dashboard</p>
        </div>
      </div>
    </aside>
  );
}

function InfoCell({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-50 rounded-lg px-3 py-2">
      <p className="text-[9px] font-semibold text-slate-400 uppercase tracking-wide mb-0.5">{label}</p>
      <p className="text-xs text-slate-700 font-medium truncate">{value || "—"}</p>
    </div>
  );
}
