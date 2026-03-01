"use client"

import { useState, useRef, useEffect } from "react"
import { cn } from "@/lib/utils"
import { Send, Sparkles, User, Bot, TrendingUp, AlertTriangle, BarChart, Users } from "lucide-react"
import { AnalysisChart } from "./analysis-chart"

export interface Message {
  id: string
  type: "user" | "assistant"
  content: string
  intent?: string
  confidence?: number
  insights?: string[]
  rawData?: Record<string, unknown>
  timestamp: Date
}

interface ChatInterfaceProps {
  messages: Message[]
  onSendMessage: (query: string) => void
  isLoading: boolean
}

const exampleQueries = [
  "Top banks by total transaction value",
  "Average transaction amount by state",
  "Compare iOS vs Android by total amount",
  "Fraud rate by category",
  "Peak hours for Food transactions",
  "Transaction count by device type",
]

const intentIcons: Record<string, React.ReactNode> = {
  descriptive: <BarChart className="w-4 h-4" />,
  comparative: <TrendingUp className="w-4 h-4" />,
  user_segmentation: <Users className="w-4 h-4" />,
  risk_analysis: <AlertTriangle className="w-4 h-4" />,
}

const intentColors: Record<string, string> = {
  descriptive: "bg-chart-1/10 text-chart-1 border-chart-1/20",
  comparative: "bg-chart-2/10 text-chart-2 border-chart-2/20",
  user_segmentation: "bg-chart-3/10 text-chart-3 border-chart-3/20",
  risk_analysis: "bg-chart-5/10 text-chart-5 border-chart-5/20",
}

export function ChatInterface({ messages, onSendMessage, isLoading }: ChatInterfaceProps) {
  const [input, setInput] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput("")
    }
  }

  const handleExampleClick = (query: string) => {
    if (!isLoading) {
      onSendMessage(query)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
              <Sparkles className="w-8 h-8 text-primary" />
            </div>
            <h2 className="text-xl font-semibold text-foreground mb-2">
              Welcome to InsightX
            </h2>
            <p className="text-muted-foreground mb-8 max-w-md leading-relaxed">
              Ask questions about payment transactions in natural language. I can analyze 250K+ transactions and provide actionable insights.
            </p>

            {/* Example Queries */}
            <div className="w-full max-w-2xl">
              <p className="text-sm text-muted-foreground mb-3">Try asking:</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {exampleQueries.map((query, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleClick(query)}
                    className="text-left px-4 py-3 rounded-lg bg-secondary/50 hover:bg-secondary text-sm text-foreground transition-colors border border-border hover:border-primary/30"
                  >
                    {query}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3 animate-slide-up",
                  message.type === "user" ? "justify-end" : "justify-start"
                )}
              >
                {message.type === "assistant" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-primary" />
                  </div>
                )}

                <div
                  className={cn(
                    "max-w-[85%] lg:max-w-[75%]",
                    message.type === "user" ? "order-first" : ""
                  )}
                >
                  {/* Message Content */}
                  <div
                    className={cn(
                      "rounded-xl px-4 py-3",
                      message.type === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-card border border-border"
                    )}
                  >
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">
                      {message.content}
                    </p>
                  </div>

                  {/* Assistant metadata */}
                  {message.type === "assistant" && (
                    <div className="mt-2 space-y-3">
                      {/* Intent & Confidence */}
                      {message.intent && (
                        <div className="flex items-center gap-2 flex-wrap">
                          <span
                            className={cn(
                              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border",
                              intentColors[message.intent] || "bg-secondary text-foreground"
                            )}
                          >
                            {intentIcons[message.intent]}
                            {message.intent.replace("_", " ")}
                          </span>
                          {message.confidence !== undefined && (
                            <span className="text-xs text-muted-foreground">
                              {Math.round(message.confidence * 100)}% confidence
                            </span>
                          )}
                        </div>
                      )}

                      {/* Insights */}
                      {message.insights && message.insights.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {message.insights.slice(0, 3).map((insight, idx) => (
                            <span
                              key={idx}
                              className="text-xs px-2 py-1 rounded-md bg-accent/10 text-accent"
                            >
                              {insight}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Chart Visualization */}
                      {message.rawData && (
                        <AnalysisChart data={message.rawData} />
                      )}
                    </div>
                  )}

                  {/* Timestamp */}
                  <p className={cn(
                    "text-xs text-muted-foreground mt-1",
                    message.type === "user" ? "text-right" : ""
                  )}>
                    {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </p>
                </div>

                {message.type === "user" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-secondary flex items-center justify-center">
                    <User className="w-4 h-4 text-muted-foreground" />
                  </div>
                )}
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex gap-3 animate-slide-up">
                <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
                <div className="bg-card border border-border rounded-xl px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                    <span className="text-sm text-muted-foreground">Analyzing...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-border bg-card p-4">
        <form onSubmit={handleSubmit} className="flex items-center gap-3">
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about transaction data..."
              disabled={isLoading}
              className="w-full px-4 py-3 rounded-xl bg-background border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all disabled:opacity-50"
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex items-center justify-center w-12 h-12 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  )
}
