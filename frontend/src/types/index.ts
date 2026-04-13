export interface Transaction {
  id: string
  merchant: string
  category: string
  amount: number
  timestamp: string
  upi_ref: string
  flagged: boolean
  flag_reason?: string
}

export interface ChatMessage {
  role: "user" | "assistant"
  content: string
}

export type WsMessage =
  | { type: "transaction"; data: Transaction }
  | { type: "agent_insight"; transaction_id: string; message: string }
  | { type: "chat_response"; message: string }
  | { type: "typing"; value: boolean }
  | { type: "pong" }

export const CATEGORY_COLORS: Record<string, string> = {
  food: "#1D9E75",
  shopping: "#7F77DD",
  entertainment: "#EF9F27",
  transport: "#378ADD",
  health: "#D85A30",
  unknown: "#888780",
}

export function formatINR(n: number): string {
  return `₹${n.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`
}

export function parseTxnDate(iso: string): Date {
  const cleaned = iso.replace(/(\.\d{3})\d+/, "$1")
  const normalized = /([zZ]|[+-]\d{2}:\d{2})$/.test(cleaned) ? cleaned : `${cleaned}Z`
  return new Date(normalized)
}

export function timeAgo(iso: string): string {
  const date = parseTxnDate(iso)
  const ms = date.getTime()

  if (Number.isNaN(ms)) return "--"

  const diff = (Date.now() - ms) / 1000
  if (diff < 10) return "just now"
  if (diff < 60) return `${Math.floor(diff)}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}