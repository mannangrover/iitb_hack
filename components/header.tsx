"use client"

import { cn } from "@/lib/utils"
import { Circle, Menu, RefreshCw } from "lucide-react"

interface HeaderProps {
  apiStatus: "connected" | "disconnected" | "loading"
  sessionId: string | null
  onMenuToggle: () => void
  onRefresh: () => void
}

export function Header({ apiStatus, sessionId, onMenuToggle, onRefresh }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-4 py-3 bg-card border-b border-border">
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuToggle}
          className="lg:hidden p-2 rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-lg font-semibold text-foreground">Analytics Dashboard</h1>
          <p className="text-xs text-muted-foreground">
            Natural language queries for transaction insights
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Session Badge */}
        {sessionId && (
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary text-xs text-muted-foreground">
            <span>Session:</span>
            <code className="font-mono text-foreground">{sessionId.slice(0, 8)}...</code>
          </div>
        )}

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          className="p-2 rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
          title="Refresh connection"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        {/* API Status */}
        <div
          className={cn(
            "flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium",
            apiStatus === "connected"
              ? "bg-accent/10 text-accent"
              : apiStatus === "loading"
              ? "bg-primary/10 text-primary"
              : "bg-destructive/10 text-destructive"
          )}
        >
          <Circle
            className={cn(
              "w-2 h-2 fill-current",
              apiStatus === "loading" && "animate-pulse"
            )}
          />
          <span className="hidden sm:inline">
            {apiStatus === "connected"
              ? "API Connected"
              : apiStatus === "loading"
              ? "Connecting..."
              : "Disconnected"}
          </span>
        </div>
      </div>
    </header>
  )
}
