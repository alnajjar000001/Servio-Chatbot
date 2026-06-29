export type MessageRole = "user" | "assistant";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  attachments?: Attachment[];
}

export interface Attachment {
  id: string;
  name: string;
  type: "image" | "document" | "other";
  url: string;
}

export interface CustomerLocation {
  areaName: string;
  governorate: string;
  block: string;
  street: string;
  building: string;
  apartment: string;
}

export interface CustomerProfile {
  name: string;
  code: string;
  phone: string;
  location: CustomerLocation;
}

export interface Contract {
  id: string;
  title: string;
  status: "active" | "pending" | "expired";
  startDate: string;
  endDate: string;
}

export interface Order {
  id: string;
  description: string;
  status: "open" | "in-progress" | "completed" | "cancelled";
  date: string;
}

export interface Invoice {
  id: string;
  amount: number;
  currency: string;
  status: "paid" | "unpaid" | "overdue";
  dueDate: string;
}

export interface CustomerData {
  profile: CustomerProfile;
  contracts: Contract[];
  orders: Order[];
  invoices: Invoice[];
}
