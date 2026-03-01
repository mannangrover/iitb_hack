"use client"

import { useState, useEffect, useCallback } from "react"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { ChatInterface, type Message } from "@/components/chat-interface"
import { StatsCards } from "@/components/stats-cards"
import { HistoryPanel } from "@/components/history-panel"
import { SettingsPanel } from "@/components/settings-panel"
import { checkApiHealth, sendQuery, startConversation, API_BASE_URL } from "@/lib/api"
import { cn } from "@/lib/utils"

export default function Dashboard() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeTab, setActiveTab] = useState("chat")
  const [apiStatus, setApiStatus] = useState<"connected" | "disconnected" | "loading">("loading")
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [apiUrl, setApiUrl] = useState(API_BASE_URL)
  const [theme, setTheme] = useState<"light" | "dark">("dark")

  // Check API health on mount
  const checkHealth = useCallback(async () => {
    setApiStatus("loading")
    const isHealthy = await checkApiHealth()
    setApiStatus(isHealthy ? "connected" : "disconnected")
    
    // Start a session if healthy
    if (isHealthy && !sessionId) {
      const session = await startConversation()
      if (session) {
        setSessionId(session.session_id)
      }
    } else if (!sessionId) {
      // Create demo session
      const session = await startConversation()
      if (session) {
        setSessionId(session.session_id)
      }
    }
  }, [sessionId])

  useEffect(() => {
    checkHealth()
  }, [checkHealth])

  // Handle theme change
  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [theme])

  const handleSendMessage = async (query: string) => {
    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: "user",
      content: query,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await sendQuery({
        query,
        context: { session_id: sessionId || undefined },
      })

      // Update session ID if returned
      if (response.session_id) {
        setSessionId(response.session_id)
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        type: "assistant",
        content: response.explanation,
        intent: response.intent,
        confidence: response.confidence_score,
        insights: response.insights,
        rawData: response.raw_data,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: "assistant",
        content: "Sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
      console.error("Query error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearHistory = () => {
    setMessages([])
  }

  const handleSelectMessage = (index: number) => {
    // Scroll to message in chat
    setActiveTab("chat")
    // Could implement scroll-to-message logic here
  }

  const renderContent = () => {
    switch (activeTab) {
      case "analytics":
        return (
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-foreground mb-2">Overview</h2>
              <p className="text-muted-foreground text-sm mb-6">
                Key metrics from your transaction data
              </p>
              <StatsCards />
            </div>
            
            <div className="bg-card rounded-xl border border-border p-6">
              <h3 className="font-semibold text-foreground mb-4">Quick Start</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Switch to the Chat tab and ask questions like:
              </p>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                  &quot;Top banks by total transaction value&quot;
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent" />
                  &quot;Compare iOS vs Android transactions&quot;
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-chart-3" />
                  &quot;Fraud rate by category&quot;
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-chart-5" />
                  &quot;Peak transaction hours&quot;
                </li>
              </ul>
            </div>
          </div>
        )
      case "history":
        return (
          <HistoryPanel
            messages={messages}
            onClearHistory={handleClearHistory}
            onSelectMessage={handleSelectMessage}
          />
        )
      case "settings":
        return (
          <SettingsPanel
            apiUrl={apiUrl}
            onApiUrlChange={setApiUrl}
            theme={theme}
            onThemeChange={setTheme}
          />
        )
      default:
        return (
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        )
    }
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-50 lg:static lg:z-auto transition-transform duration-300",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          activeTab={activeTab}
          onTabChange={(tab) => {
            setActiveTab(tab)
            setMobileMenuOpen(false)
          }}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          apiStatus={apiStatus}
          sessionId={sessionId}
          onMenuToggle={() => setMobileMenuOpen(!mobileMenuOpen)}
          onRefresh={checkHealth}
        />
        
        <main className="flex-1 overflow-hidden">
          {renderContent()}
        </main>
      </div>
    </div>
  )
}
