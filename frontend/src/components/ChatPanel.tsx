import { useEffect, useRef, useState } from "react"
import type { ChatMessage } from "../types/index"

interface Props {
  messages: ChatMessage[]
  isTyping: boolean
  onSend: (msg: string) => void
}

export function ChatPanel({ messages, isTyping, onSend }: Props) {
  const [input, setInput] = useState("")
  const [isFocused, setIsFocused] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isTyping])

  const send = () => {
    const msg = input.trim()
    if (!msg) return
    onSend(msg)
    setInput("")
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ flex: 1, overflowY: "auto", padding: "12px 0" }}>
        {messages.length === 0 && (
          <div style={{ color: "var(--muted)", fontSize: 13, textAlign: "center", marginTop: 24 }}>
            Ask me anything about your spending.
            <div style={{ fontSize: 11, marginTop: 6 }}>
              "How much did I spend on food?" · "Set a ₹3000 food budget"
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              justifyContent: m.role === "user" ? "flex-end" : "flex-start",
              marginBottom: 10,
            }}
          >
            <div
              style={{
                maxWidth: "80%",
                background: m.role === "user" ? "#7F77DD" : "var(--surface)",
                color: m.role === "user" ? "#fff" : "inherit",
                borderRadius: m.role === "user"
                  ? "12px 12px 2px 12px"
                  : "12px 12px 12px 2px",
                padding: "8px 12px",
                fontSize: 13,
                lineHeight: 1.5,
                whiteSpace: "pre-wrap",
              }}
            >
              {m.content}
            </div>
          </div>
        ))}

        {isTyping && (
          <div style={{ display: "flex", gap: 4, padding: "4px 8px" }}>
            {[0, 1, 2].map(i => (
              <div
                key={i}
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  background: "#7F77DD",
                  opacity: 0.6,
                  animation: `bounce 1s ${i * 0.2}s infinite`,
                }}
              />
            ))}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div
        style={{
          display: "flex",
          gap: 8,
          paddingTop: 8,
          borderTop: "1px solid var(--border)",
        }}
      >
        <input
          value={input}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && send()}
          placeholder={isFocused ? "" : "Ask about your spending..."}
          style={{
            flex: 1,
            borderRadius: 8,
            border: "1px solid var(--border)",
            padding: "8px 12px",
            fontSize: 13,
            background: "var(--bg)",
            color: "#7F77DD",
            outline: "none",
          }}
        />
        <button
          onClick={send}
          style={{
            background: "#7F77DD",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            padding: "8px 16px",
            cursor: "pointer",
            fontSize: 13,
            fontWeight: 500,
          }}
        >
          Send
        </button>
      </div>
    </div>
  )
}