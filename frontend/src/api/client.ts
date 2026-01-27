import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const apiKey = import.meta.env.VITE_API_KEY || 'dev-interview-key'

const apiClient = axios.create({
  baseURL,
  headers: {
    'X-API-Key': apiKey,
    'Content-Type': 'application/json',
  },
})

export interface QueryRequest {
  user_id: string
  conversation_id?: string
  query: string
}

export interface TraceEvent {
  step: string
  status: string
  timestamp: string
  duration_ms: number
  message: string
}

export interface ConversationTurn {
  role: string
  content: string
  intent?: string
  timestamp: string
}

export interface QueryResponse {
  conversation_id: string
  answer: string
  agent_trace: string[]
  retrieved_context: string[]
  recent_turns: ConversationTurn[]
  trace_events: TraceEvent[]
  intent: string
  confidence: number
  needs_escalation: boolean
  escalation_reason?: string
  policy_violations: string[]
}

export interface DocumentIngestResponse {
  added_count: number
  total_documents: number
}

export interface RetrieverStats {
  index_size: number
  metadata_count: number
}

// Query API
export const queryAPI = {
  processQuery: async (payload: QueryRequest): Promise<QueryResponse> => {
    const response = await apiClient.post<QueryResponse>('/query', payload)
    return response.data
  },
}

// Documents API
export const documentsAPI = {
  ingest: async (docs: string[]): Promise<DocumentIngestResponse> => {
    const response = await apiClient.post<DocumentIngestResponse>('/documents', {
      documents: docs,
    })
    return response.data
  },
  stats: async (): Promise<RetrieverStats> => {
    const response = await apiClient.get<RetrieverStats>('/documents/stats')
    return response.data
  },
}

// Observability API
export const observabilityAPI = {
  getMemory: async (conversationId: string): Promise<ConversationTurn[]> => {
    const response = await apiClient.get<ConversationTurn[]>(
      `/observability/conversations/${conversationId}/memory`
    )
    return response.data
  },
  getTraces: async (conversationId: string): Promise<TraceEvent[]> => {
    const response = await apiClient.get<TraceEvent[]>(
      `/observability/conversations/${conversationId}/traces`
    )
    return response.data
  },
}

export default apiClient
