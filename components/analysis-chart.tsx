"use client"

import { useMemo } from "react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  CartesianGrid,
} from "recharts"
import { formatNumber, formatCurrency } from "@/lib/utils"

interface AnalysisChartProps {
  data: Record<string, unknown>
}

const CHART_COLORS = [
  "hsl(221, 83%, 53%)", // primary blue
  "hsl(158, 64%, 52%)", // accent green
  "hsl(262, 83%, 58%)", // purple
  "hsl(24, 94%, 50%)",  // orange
  "hsl(340, 82%, 52%)", // pink
  "hsl(190, 90%, 50%)", // cyan
  "hsl(45, 93%, 47%)",  // yellow
]

export function AnalysisChart({ data }: AnalysisChartProps) {
  const chartData = useMemo(() => {
    // Handle different data structures from the API

    // 1. Direct data array with categories
    if (data?.data && Array.isArray(data.data)) {
      return {
        type: "bar",
        data: data.data.slice(0, 10).map((item: Record<string, unknown>) => ({
          name: item.category || item.segment || item.group || "Unknown",
          value: item.total_amount || item.average_amount || item.transaction_count || 0,
          count: item.transaction_count,
          average: item.average_amount,
          total: item.total_amount,
        })),
        metric: data.metric as string || "total_amount",
      }
    }

    // 2. Segments array
    if (data?.segments && Array.isArray(data.segments)) {
      return {
        type: "bar",
        data: data.segments.slice(0, 10).map((item: Record<string, unknown>) => ({
          name: item.segment || "Unknown",
          value: item.transaction_count || item.average_transaction_value || 0,
          count: item.transaction_count,
          average: item.average_transaction_value,
        })),
        metric: "transaction_count",
      }
    }

    // 3. Groups array
    if (data?.groups && Array.isArray(data.groups)) {
      return {
        type: "bar",
        data: data.groups.slice(0, 10).map((item: Record<string, unknown>) => ({
          name: item.group || "Unknown",
          value: item.fraud_rate || item.total || item.count || 0,
          fraudRate: item.fraud_rate,
          total: item.total,
        })),
        metric: data.groups[0]?.fraud_rate !== undefined ? "fraud_rate" : "total",
      }
    }

    // 4. Temporal data (hourly/daily)
    if (data?.temporal) {
      const temporal = data.temporal as Record<string, unknown[]>
      
      if (temporal.hourly && Array.isArray(temporal.hourly)) {
        return {
          type: "line",
          data: temporal.hourly.map((item: Record<string, unknown>) => ({
            name: `${item.hour}:00`,
            value: item.transaction_count || 0,
          })),
          metric: "hourly",
        }
      }

      if (temporal.day_of_week && Array.isArray(temporal.day_of_week)) {
        const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return {
          type: "bar",
          data: temporal.day_of_week.map((item: Record<string, unknown>) => ({
            name: days[item.day_of_week as number] || `Day ${item.day_of_week}`,
            value: item.transaction_count || 0,
          })),
          metric: "day_of_week",
        }
      }
    }

    // 5. Comparison data
    if (data?.comparison && Array.isArray(data.comparison)) {
      return {
        type: "pie",
        data: data.comparison.slice(0, 6).map((item: Record<string, unknown>) => ({
          name: item.category || item.group || "Unknown",
          value: item.total_amount || item.transaction_count || 0,
        })),
        metric: "comparison",
      }
    }

    return null
  }, [data])

  if (!chartData || chartData.data.length === 0) {
    return null
  }

  const formatValue = (value: number) => {
    if (chartData.metric === "fraud_rate") {
      return `${value.toFixed(2)}%`
    }
    if (chartData.metric.includes("amount") || chartData.metric === "total_amount") {
      return formatCurrency(value)
    }
    return formatNumber(value)
  }

  const CustomTooltip = ({ active, payload, label }: {
    active?: boolean
    payload?: Array<{ value: number; payload: Record<string, unknown> }>
    label?: string
  }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload
      return (
        <div className="bg-popover border border-border rounded-lg shadow-lg p-3 text-sm">
          <p className="font-medium text-foreground mb-1">{label}</p>
          <div className="space-y-1 text-muted-foreground">
            {item.total !== undefined && (
              <p>Total: {formatCurrency(item.total as number)}</p>
            )}
            {item.average !== undefined && (
              <p>Average: {formatCurrency(item.average as number)}</p>
            )}
            {item.count !== undefined && (
              <p>Transactions: {formatNumber(item.count as number)}</p>
            )}
            {item.fraudRate !== undefined && (
              <p>Fraud Rate: {(item.fraudRate as number).toFixed(2)}%</p>
            )}
            {item.value !== undefined && !item.total && !item.average && !item.count && !item.fraudRate && (
              <p>Value: {formatValue(item.value as number)}</p>
            )}
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="mt-3 p-4 bg-background rounded-xl border border-border">
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          {chartData.type === "line" ? (
            <LineChart data={chartData.data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis 
                dataKey="name" 
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                axisLine={{ stroke: "hsl(var(--border))" }}
              />
              <YAxis 
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                axisLine={{ stroke: "hsl(var(--border))" }}
                tickFormatter={formatNumber}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="value"
                stroke={CHART_COLORS[0]}
                strokeWidth={2}
                dot={{ fill: CHART_COLORS[0], strokeWidth: 0, r: 3 }}
                activeDot={{ r: 5, stroke: CHART_COLORS[0], strokeWidth: 2, fill: "hsl(var(--background))" }}
              />
            </LineChart>
          ) : chartData.type === "pie" ? (
            <PieChart>
              <Pie
                data={chartData.data}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {chartData.data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          ) : (
            <BarChart data={chartData.data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis 
                dataKey="name" 
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                axisLine={{ stroke: "hsl(var(--border))" }}
                tickLine={false}
              />
              <YAxis 
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={formatNumber}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: "hsl(var(--muted) / 0.3)" }} />
              <Bar
                dataKey="value"
                radius={[4, 4, 0, 0]}
                fill={CHART_COLORS[0]}
              />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  )
}
