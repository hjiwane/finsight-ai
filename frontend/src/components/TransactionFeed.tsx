import type { Transaction } from "../types/index"
import { CATEGORY_COLORS, formatINR, timeAgo } from "../types/index"

interface Props {
  transactions: Transaction[]
  insights: Record<string, string>
}

function TransactionRow({ txn, insight }: { txn: Transaction; insight?: string }) {
  const color = CATEGORY_COLORS[txn.category] ?? CATEGORY_COLORS.unknown

  return (
    <div style={{
      borderLeft: `3px solid ${color}`,
      padding: "10px 14px",
      marginBottom: 8,
      background: "var(--surface)",
      borderRadius: "0 8px 8px 0",
      animation: "fadeIn .4s ease",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <span style={{ fontWeight: 500, fontSize: 14 }}>{txn.merchant}</span>
          {txn.flagged && (
            <span style={{
              marginLeft: 8, fontSize: 10, fontWeight: 600,
              background: "#FCEBEB", color: "#A32D2D",
              borderRadius: 4, padding: "2px 6px",
            }}>
              SUSPICIOUS
            </span>
          )}
          <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 2 }}>
            {txn.category} · {timeAgo(txn.timestamp)} · {txn.upi_ref}
          </div>
        </div>
        <span style={{
          fontWeight: 600, fontSize: 15,
          color: txn.flagged ? "#A32D2D" : "inherit",
          whiteSpace: "nowrap", marginLeft: 12,
        }}>
          {formatINR(txn.amount)}
        </span>
      </div>

      {insight && (
        <div style={{
          marginTop: 8, fontSize: 12, color: "var(--muted)",
          background: "var(--bg)", borderRadius: 6,
          padding: "6px 10px", borderLeft: "2px solid #7F77DD",
        }}>
           {insight}
        </div>
      )}
    </div>
  )
}

export function TransactionFeed({ transactions, insights }: Props) {
  if (transactions.length === 0) {
    return (
      <div style={{ color: "var(--muted)", fontSize: 13, textAlign: "center", paddingTop: 40 }}>
        Waiting for transactions...
      </div>
    )
  }

  return (
    <div>
      {transactions.map(t => (
        <TransactionRow key={t.id} txn={t} insight={insights[t.id]} />
      ))}
    </div>
  )
}