"use client"

import { cn, formatNumber, formatCurrency } from "@/lib/utils"
import { TrendingUp, TrendingDown, Activity, DollarSign, Users, AlertTriangle } from "lucide-react"

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon: React.ReactNode
  color: "primary" | "accent" | "chart-3" | "chart-5"
}

const colorVariants = {
  primary: "bg-primary/10 text-primary",
  accent: "bg-accent/10 text-accent",
  "chart-3": "bg-chart-3/10 text-chart-3",
  "chart-5": "bg-chart-5/10 text-chart-5",
}

function StatCard({ title, value, change, icon, color }: StatCardProps) {
  return (
    <div className="bg-card rounded-xl border border-border p-4 transition-all hover:shadow-lg hover:border-primary/30">
      <div className="flex items-start justify-between">
        <div className={cn("p-2 rounded-lg", colorVariants[color])}>
          {icon}
        </div>
        {change !== undefined && (
          <div className={cn(
            "flex items-center gap-1 text-xs font-medium",
            change >= 0 ? "text-accent" : "text-destructive"
          )}>
            {change >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {Math.abs(change)}%
          </div>
        )}
      </div>
      <div className="mt-3">
        <p className="text-xs text-muted-foreground">{title}</p>
        <p className="text-2xl font-semibold text-foreground mt-1">
          {typeof value === "number" ? formatNumber(value) : value}
        </p>
      </div>
    </div>
  )
}

interface StatsCardsProps {
  stats?: {
    totalTransactions?: number
    totalVolume?: number
    activeUsers?: number
    fraudRate?: number
  }
}

export function StatsCards({ stats }: StatsCardsProps) {
  const defaultStats = {
    totalTransactions: stats?.totalTransactions || 250000,
    totalVolume: stats?.totalVolume || 156800000,
    activeUsers: stats?.activeUsers || 45200,
    fraudRate: stats?.fraudRate || 0.42,
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total Transactions"
        value={defaultStats.totalTransactions}
        icon={<Activity className="w-5 h-5" />}
        color="primary"
        change={12}
      />
      <StatCard
        title="Total Volume"
        value={formatCurrency(defaultStats.totalVolume)}
        icon={<DollarSign className="w-5 h-5" />}
        color="accent"
        change={8}
      />
      <StatCard
        title="Active Users"
        value={defaultStats.activeUsers}
        icon={<Users className="w-5 h-5" />}
        color="chart-3"
        change={5}
      />
      <StatCard
        title="Fraud Rate"
        value={`${defaultStats.fraudRate}%`}
        icon={<AlertTriangle className="w-5 h-5" />}
        color="chart-5"
        change={-2}
      />
    </div>
  )
}
