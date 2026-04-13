import { useEffect, useRef, useState } from "react"
import type { Transaction, WsMessage } from "../types/index"

interface UseFeedSocketReturn {
  transactions: Transaction[]
  insights: Record<string, string>
  connected: boolean
}

export function useFeedSocket(): UseFeedSocketReturn {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [insights, setInsights] = useState<Record<string, string>>({})
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/feed")
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)

    ws.onmessage = (e) => {
      const msg: WsMessage = JSON.parse(e.data)

      if (msg.type === "transaction") {
        setTransactions(prev => {
          const existingIndex = prev.findIndex(t => t.id === msg.data.id)

          if (existingIndex !== -1) {
            const updated = [...prev]
            updated[existingIndex] = msg.data
            return updated
          }

          return [msg.data, ...prev].slice(0, 50)
        })
      }

      if (msg.type === "agent_insight") {
        setInsights(prev => ({ ...prev, [msg.transaction_id]: msg.message }))
      }
    }

    const ping = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping")
    }, 25000)

    return () => {
      clearInterval(ping)
      ws.close()
    }
  }, [])

  return { transactions, insights, connected }
}