// API configuration and types

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://iitbhack-insightx.streamlit.app"

// For demo/fallback when API is not available
export const DEMO_MODE = true

export interface QueryRequest {
  query: string
  context?: {
    session_id?: string
  }
}

export interface QueryResponse {
  query: string
  intent: string
  explanation: string
  insights: string[]
  confidence_score: number
  raw_data: Record<string, unknown>
  session_id?: string
}

export interface HealthResponse {
  status: string
  service: string
  version: string
}

export interface ConversationStartResponse {
  session_id: string
  message: string
}

// Demo responses for when API is not available
const demoResponses: Record<string, QueryResponse> = {
  default: {
    query: "",
    intent: "descriptive",
    explanation: "Based on the transaction data analysis, I found interesting patterns in your data. The analysis shows significant variation across different segments with clear trends emerging from the dataset.",
    insights: [
      "Total transactions: 250,000+",
      "Average amount: Rs.1,250",
      "Peak hours: 10 AM - 2 PM"
    ],
    confidence_score: 0.92,
    raw_data: {
      data: [
        { category: "Food", total_amount: 45000000, transaction_count: 52000, average_amount: 865 },
        { category: "Shopping", total_amount: 38000000, transaction_count: 41000, average_amount: 927 },
        { category: "Entertainment", total_amount: 28000000, transaction_count: 35000, average_amount: 800 },
        { category: "Travel", total_amount: 32000000, transaction_count: 28000, average_amount: 1143 },
        { category: "Bills", total_amount: 52000000, transaction_count: 48000, average_amount: 1083 },
        { category: "Others", total_amount: 25000000, transaction_count: 46000, average_amount: 543 },
      ],
      metric: "total_amount"
    }
  },
  bank: {
    query: "",
    intent: "comparative",
    explanation: "Analyzing transaction volumes by bank reveals significant differences in market share and transaction values. The top banks dominate the transaction ecosystem with clear leaders emerging.",
    insights: [
      "Top bank: HDFC (23% share)",
      "Fastest growing: ICICI Bank",
      "Average transaction: Rs.1,450"
    ],
    confidence_score: 0.89,
    raw_data: {
      data: [
        { category: "HDFC", total_amount: 58000000, transaction_count: 40000, average_amount: 1450 },
        { category: "SBI", total_amount: 52000000, transaction_count: 45000, average_amount: 1156 },
        { category: "ICICI", total_amount: 48000000, transaction_count: 38000, average_amount: 1263 },
        { category: "Axis", total_amount: 35000000, transaction_count: 32000, average_amount: 1094 },
        { category: "Kotak", total_amount: 28000000, transaction_count: 25000, average_amount: 1120 },
      ],
      metric: "total_amount"
    }
  },
  state: {
    query: "",
    intent: "user_segmentation",
    explanation: "Geographic analysis shows strong regional variations in transaction patterns. Maharashtra leads in transaction volume, followed by Karnataka and Delhi.",
    insights: [
      "Top state: Maharashtra",
      "Highest avg: Delhi (Rs.1,650)",
      "Fastest growth: Karnataka"
    ],
    confidence_score: 0.91,
    raw_data: {
      data: [
        { category: "Maharashtra", total_amount: 42000000, transaction_count: 35000, average_amount: 1200 },
        { category: "Karnataka", total_amount: 38000000, transaction_count: 32000, average_amount: 1188 },
        { category: "Delhi", total_amount: 35000000, transaction_count: 21000, average_amount: 1667 },
        { category: "Tamil Nadu", total_amount: 28000000, transaction_count: 26000, average_amount: 1077 },
        { category: "Gujarat", total_amount: 25000000, transaction_count: 24000, average_amount: 1042 },
      ],
      metric: "total_amount"
    }
  },
  fraud: {
    query: "",
    intent: "risk_analysis",
    explanation: "Risk analysis indicates varying fraud rates across transaction categories. Shopping shows the highest fraud rate at 0.65%, requiring enhanced monitoring. Overall fraud rate remains low at 0.42%.",
    insights: [
      "Overall fraud rate: 0.42%",
      "High risk: Shopping (0.65%)",
      "Lowest risk: Bills (0.18%)"
    ],
    confidence_score: 0.95,
    raw_data: {
      groups: [
        { group: "Shopping", fraud_rate: 0.65, total: 267 },
        { group: "Entertainment", fraud_rate: 0.52, total: 182 },
        { group: "Travel", fraud_rate: 0.48, total: 134 },
        { group: "Food", fraud_rate: 0.35, total: 182 },
        { group: "Bills", fraud_rate: 0.18, total: 86 },
      ]
    }
  },
  device: {
    query: "",
    intent: "comparative",
    explanation: "Device type analysis shows iOS users have higher average transaction amounts, while Android dominates in transaction volume. Web transactions show consistent patterns.",
    insights: [
      "iOS: Higher avg amount",
      "Android: Most transactions",
      "Web: Growing steadily"
    ],
    confidence_score: 0.88,
    raw_data: {
      data: [
        { category: "Android", total_amount: 85000000, transaction_count: 125000, average_amount: 680 },
        { category: "iOS", total_amount: 72000000, transaction_count: 85000, average_amount: 847 },
        { category: "Web", total_amount: 35000000, transaction_count: 40000, average_amount: 875 },
      ],
      metric: "total_amount"
    }
  },
  hourly: {
    query: "",
    intent: "descriptive",
    explanation: "Temporal analysis reveals peak transaction hours between 10 AM and 2 PM, with a secondary peak during evening hours. Late night shows minimal activity.",
    insights: [
      "Peak: 10 AM - 2 PM",
      "Secondary peak: 6-8 PM",
      "Lowest: 2-5 AM"
    ],
    confidence_score: 0.94,
    raw_data: {
      temporal: {
        hourly: [
          { hour: 6, transaction_count: 3500 },
          { hour: 7, transaction_count: 5200 },
          { hour: 8, transaction_count: 8900 },
          { hour: 9, transaction_count: 12500 },
          { hour: 10, transaction_count: 18200 },
          { hour: 11, transaction_count: 21500 },
          { hour: 12, transaction_count: 19800 },
          { hour: 13, transaction_count: 17200 },
          { hour: 14, transaction_count: 15400 },
          { hour: 15, transaction_count: 13200 },
          { hour: 16, transaction_count: 12800 },
          { hour: 17, transaction_count: 14500 },
          { hour: 18, transaction_count: 16200 },
          { hour: 19, transaction_count: 14800 },
          { hour: 20, transaction_count: 11200 },
          { hour: 21, transaction_count: 8500 },
          { hour: 22, transaction_count: 5200 },
          { hour: 23, transaction_count: 2800 },
        ]
      }
    }
  }
}

function getDemoResponse(query: string): QueryResponse {
  const q = query.toLowerCase()
  
  if (q.includes("bank")) return { ...demoResponses.bank, query }
  if (q.includes("state")) return { ...demoResponses.state, query }
  if (q.includes("fraud") || q.includes("risk")) return { ...demoResponses.fraud, query }
  if (q.includes("device") || q.includes("ios") || q.includes("android")) return { ...demoResponses.device, query }
  if (q.includes("hour") || q.includes("peak") || q.includes("time")) return { ...demoResponses.hourly, query }
  
  return { ...demoResponses.default, query }
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(3000),
    })
    return response.ok
  } catch {
    return false
  }
}

export async function startConversation(): Promise<ConversationStartResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/conversation/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
    if (response.ok) {
      return response.json()
    }
    return null
  } catch {
    // Return mock session for demo
    return {
      session_id: `demo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      message: "Demo session started"
    }
  }
}

export async function sendQuery(request: QueryRequest): Promise<QueryResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal: AbortSignal.timeout(30000),
    })
    
    if (response.ok) {
      return response.json()
    }
    
    // Fallback to demo response
    return getDemoResponse(request.query)
  } catch {
    // Return demo response when API is unavailable
    await new Promise(resolve => setTimeout(resolve, 800)) // Simulate network delay
    return getDemoResponse(request.query)
  }
}
