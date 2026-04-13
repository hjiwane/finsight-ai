import { useEffect, useRef, useState } from "react"
import type { ChatMessage, WsMessage } from "../types/index"

interface UseChatSocketReturn {
  messages: ChatMessage[]
  isTyping: boolean
  sendMessage: (text: string) => void
}

export function useChatSocket(): UseChatSocketReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/chat")
    wsRef.current = ws

    ws.onmessage = (e) => {
      const msg: WsMessage = JSON.parse(e.data)

      if (msg.type === "chat_response") {
        setMessages(prev => [...prev, { role: "assistant", content: msg.message }])
      }
      if (msg.type === "typing") {
        setIsTyping(msg.value)
      }
    }

    return () => ws.close()
  }, [])

  const sendMessage = (text: string) => {
    // add user message to UI immediately
    setMessages(prev => [...prev, { role: "user", content: text }])
    // send to backend
    wsRef.current?.send(JSON.stringify({ message: text }))
  }

  return { messages, isTyping, sendMessage }
}