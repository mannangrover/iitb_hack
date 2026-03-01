"use client"

import { cn } from "@/lib/utils"
import { Clock, BarChart, TrendingUp, Users, AlertTriangle, Trash2 } from "lucide-react"
import type { Message } from "./chat-interface"

interface HistoryPanelProps {
  messages: Message[]
  onClearHistory: () => void
  onSelectMessage: (index: number) => void
}

const intentIcons: Record<string, React.ReactNode> = {
  descriptive: <BarChart className="w-4 h-4" />,
  comparative: <TrendingUp className="w-4 h-4" />,
  user_segmentation: <Users className="w-4 h-4" />,
  risk_analysis: <AlertTriangle className="w-4 h-4" />,
}

const intentColors: Record<string, string> = {
  descriptive: "text-chart-1",
  comparative: "text-chart-2",
  user_segmentation: "text-chart-3",
  risk_analysis: "text-chart-5",
}

export function HistoryPanel({ messages, onClearHistory, onSelectMessage }: HistoryPanelProps) {
  const userMessages = messages.filter((m) => m.type === "user")

  return (
    <div className="h-full flex flex-col bg-card">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-muted-foreground" />
          <h2 className="font-semibold text-foreground">Query History</h2>
        </div>
        {userMessages.length > 0 && (
          <button
            onClick={onClearHistory}
            className="p-2 rounded-lg text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
            title="Clear history"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {userMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-8">
            <Clock className="w-12 h-12 text-muted-foreground/30 mb-4" />
            <p className="text-muted-foreground text-sm">No queries yet</p>
            <p className="text-muted-foreground/60 text-xs mt-1">
              Your query history will appear here
            </p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {userMessages.map((message, index) => {
              const intent = message.intent || "descriptive"
              const messageIndex = messages.findIndex((m) => m.id === message.id)
              
              return (
                <button
                  key={message.id}
                  onClick={() => onSelectMessage(messageIndex)}
                  className="w-full text-left px-4 py-3 hover:bg-secondary/50 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className={cn("mt-0.5", intentColors[intent] || "text-muted-foreground")}>
                      {intentIcons[intent] || <BarChart className="w-4 h-4" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-foreground line-clamp-2">
                        {message.content}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-muted-foreground capitalize">
                          {intent.replace("_", " ")}
                        </span>
                        <span className="text-xs text-muted-foreground/50">
                          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
