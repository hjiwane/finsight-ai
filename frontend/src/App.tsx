import { useState } from "react"
import { useFeedSocket } from "./hooks/useFeedSocket"
import { useChatSocket } from "./hooks/useChatSocket"
import { TransactionFeed } from "./components/TransactionFeed"
import { SpendingChart } from "./components/SpendingChart"
import { ChatPanel } from "./components/ChatPanel"
import { formatINR, parseTxnDate } from "./types/index"

export default function App() {
  const [activeTab, setActiveTab] = useState<"feed" | "chat">("feed")

  const { transactions, insights, connected } = useFeedSocket()
  const { messages, isTyping, sendMessage } = useChatSocket()

  const today = new Date().toDateString()

  const totalToday = transactions
    .filter(t => parseTxnDate(t.timestamp).toDateString() === today)
    .reduce((sum, t) => sum + t.amount, 0)

  const suspiciousCount = transactions.filter(t => t.flagged).length

  return (
    <>
      <style>{`
        :root {
          --bg:      #f5f5f0;
          --surface: #ffffff;
          --border:  #e5e5e0;
          --muted:   #888780;
        }
        @media (prefers-color-scheme: dark) {
          :root {
            --bg:      #1a1a1a;
            --surface: #242424;
            --border:  #333333;
            --muted:   #888888;
          }
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, sans-serif; }
        body { background: var(--bg); }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; } }
        @keyframes bounce { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
      `}</style>

      <div style={{ maxWidth: 960, margin: "0 auto", padding: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <div>
            <h1 style={{ fontSize: 20, fontWeight: 600, color: "#7F77DD" }}>FinSight AI</h1>
            <div style={{ fontSize: 12, color: "var(--muted)" }}>UPI transaction monitor</div>
          </div>
          <div
            style={{
              fontSize: 11,
              fontWeight: 500,
              padding: "4px 10px",
              borderRadius: 20,
              background: connected ? "#E1F5EE" : "#FCEBEB",
              color: connected ? "#0F6E56" : "#A32D2D",
            }}
          >
            {connected ? "● Live" : "○ Disconnected"}
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 16 }}>
          {[
            { label: "Today's spend", value: formatINR(totalToday) },
            { label: "Transactions", value: String(transactions.length) },
            { label: "Flagged", value: String(suspiciousCount), warn: suspiciousCount > 0 },
          ].map(s => (
            <div
              key={s.label}
              style={{
                background: "var(--surface)",
                borderRadius: 10,
                padding: "12px 16px",
                border: "1px solid var(--border)",
              }}
            >
              <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 4 }}>{s.label}</div>
              <div style={{ fontSize: 22, fontWeight: 600, color: s.warn ? "#A32D2D" : "inherit" }}>
                {s.value}
              </div>
            </div>
          ))}
        </div>

        <div
          style={{
            background: "var(--surface)",
            borderRadius: 10,
            padding: "14px 16px",
            border: "1px solid var(--border)",
            marginBottom: 16,
          }}
        >
          <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 8 }}>
            Transaction amounts (live)
          </div>
          <SpendingChart transactions={transactions} />
        </div>

        <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          {(["feed", "chat"] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: "6px 16px",
                borderRadius: 8,
                cursor: "pointer",
                fontSize: 13,
                fontWeight: 500,
                border: "1px solid var(--border)",
                background: activeTab === tab ? "#7F77DD" : "var(--surface)",
                color: activeTab === tab ? "#fff" : "inherit",
              }}
            >
              {tab === "feed" ? "Transaction feed" : "Ask AI"}
            </button>
          ))}
        </div>

        <div
          style={{
            background: "var(--surface)",
            borderRadius: 10,
            border: "1px solid var(--border)",
            padding: 16,
            ...(activeTab === "chat"
              ? { height: 480, display: "flex", flexDirection: "column" as const }
              : { minHeight: 400 }),
          }}
        >
          {activeTab === "feed" ? (
            <TransactionFeed transactions={transactions} insights={insights} />
          ) : (
            <ChatPanel messages={messages} isTyping={isTyping} onSend={sendMessage} />
          )}
        </div>
      </div>
    </>
  )
}