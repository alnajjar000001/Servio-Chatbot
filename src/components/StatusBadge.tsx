"use client";

interface StatusBadgeProps {
  status: string;
  variant?: "contract" | "order" | "invoice";
}

const contractColors: Record<string, string> = {
  active: "bg-emerald-100 text-emerald-700 ring-1 ring-emerald-200",
  pending: "bg-amber-100 text-amber-700 ring-1 ring-amber-200",
  expired: "bg-slate-100 text-slate-500 ring-1 ring-slate-200",
};

const orderColors: Record<string, string> = {
  open: "bg-blue-100 text-blue-700 ring-1 ring-blue-200",
  "in-progress": "bg-violet-100 text-violet-700 ring-1 ring-violet-200",
  completed: "bg-emerald-100 text-emerald-700 ring-1 ring-emerald-200",
  cancelled: "bg-red-100 text-red-600 ring-1 ring-red-200",
};

const invoiceColors: Record<string, string> = {
  paid: "bg-emerald-100 text-emerald-700 ring-1 ring-emerald-200",
  unpaid: "bg-amber-100 text-amber-700 ring-1 ring-amber-200",
  overdue: "bg-red-100 text-red-600 ring-1 ring-red-200",
};

export default function StatusBadge({ status, variant = "contract" }: StatusBadgeProps) {
  const colorMap =
    variant === "order" ? orderColors : variant === "invoice" ? invoiceColors : contractColors;
  const classes = colorMap[status] ?? "bg-slate-100 text-slate-500 ring-1 ring-slate-200";

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wide ${classes}`}>
      {status.replace("-", " ")}
    </span>
  );
}
