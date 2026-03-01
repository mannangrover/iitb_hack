"use client"

import { useState } from "react"
import { Settings, Moon, Sun, Server, Save, RotateCcw } from "lucide-react"
import { cn } from "@/lib/utils"

interface SettingsPanelProps {
  apiUrl: string
  onApiUrlChange: (url: string) => void
  theme: "light" | "dark"
  onThemeChange: (theme: "light" | "dark") => void
}

export function SettingsPanel({
  apiUrl,
  onApiUrlChange,
  theme,
  onThemeChange,
}: SettingsPanelProps) {
  const [localApiUrl, setLocalApiUrl] = useState(apiUrl)
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    onApiUrlChange(localApiUrl)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleReset = () => {
    const defaultUrl = "https://iitbhack-insightx.streamlit.app"
    setLocalApiUrl(defaultUrl)
    onApiUrlChange(defaultUrl)
  }

  return (
    <div className="h-full flex flex-col bg-card">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-border">
        <Settings className="w-5 h-5 text-muted-foreground" />
        <h2 className="font-semibold text-foreground">Settings</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Theme Toggle */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Theme</label>
          <div className="flex gap-2">
            <button
              onClick={() => onThemeChange("light")}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg border text-sm transition-colors",
                theme === "light"
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-background border-border text-muted-foreground hover:text-foreground"
              )}
            >
              <Sun className="w-4 h-4" />
              Light
            </button>
            <button
              onClick={() => onThemeChange("dark")}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg border text-sm transition-colors",
                theme === "dark"
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-background border-border text-muted-foreground hover:text-foreground"
              )}
            >
              <Moon className="w-4 h-4" />
              Dark
            </button>
          </div>
        </div>

        {/* API Configuration */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">API Endpoint</label>
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-muted-foreground" />
            <input
              type="url"
              value={localApiUrl}
              onChange={(e) => setLocalApiUrl(e.target.value)}
              placeholder="https://api.example.com"
              className="flex-1 px-3 py-2 rounded-lg bg-background border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
          <p className="text-xs text-muted-foreground">
            The FastAPI backend URL for InsightX queries
          </p>

          <div className="flex gap-2 mt-3">
            <button
              onClick={handleSave}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                saved
                  ? "bg-accent text-accent-foreground"
                  : "bg-primary text-primary-foreground hover:bg-primary/90"
              )}
            >
              <Save className="w-4 h-4" />
              {saved ? "Saved!" : "Save"}
            </button>
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border text-sm text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
          </div>
        </div>

        {/* About */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">About InsightX</label>
          <div className="p-4 rounded-lg bg-secondary/50 border border-border">
            <p className="text-sm text-muted-foreground leading-relaxed">
              InsightX is a conversational AI for digital payment analytics. 
              Ask questions in natural language to analyze 250K+ transactions 
              and get actionable insights.
            </p>
            <div className="mt-3 pt-3 border-t border-border">
              <p className="text-xs text-muted-foreground">Version 1.0.0</p>
              <p className="text-xs text-muted-foreground">Built for TechFest IIT Bombay</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
