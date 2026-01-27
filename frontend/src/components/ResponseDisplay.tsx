import { QueryResponse } from '../api/client'
import styles from './ResponseDisplay.module.css'

interface ResponseDisplayProps {
  response: QueryResponse | null
}

export const ResponseDisplay: React.FC<ResponseDisplayProps> = ({ response }) => {
  if (!response) {
    return (
      <div className={styles.placeholder}>
        Submit a query to see the multi-agent response and trace information.
      </div>
    )
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#10b981'
    if (confidence >= 0.6) return '#f59e0b'
    return '#ef4444'
  }

  const getIntentBadgeColor = (intent: string) => {
    const colors: Record<string, string> = {
      billing: '#8b5cf6',
      shipping: '#06b6d4',
      account: '#ec4899',
      complaint: '#f97316',
      general: '#6366f1',
    }
    return colors[intent] || '#6b7280'
  }

  return (
    <div className={styles.container}>
      <div className={styles.section}>
        <h3>Agent Response</h3>
        <p className={styles.answer}>{response.answer}</p>
      </div>

      <div className={styles.grid}>
        <div className={styles.card}>
          <h4>Intent Classification</h4>
          <div className={styles.badge} style={{ background: getIntentBadgeColor(response.intent) }}>
            {response.intent}
          </div>
          <div className={styles.confidence}>
            Confidence: <strong style={{ color: getConfidenceColor(response.confidence) }}>
              {(response.confidence * 100).toFixed(1)}%
            </strong>
          </div>
        </div>

        {response.needs_escalation && (
          <div className={`${styles.card} ${styles.escalated}`}>
            <h4>⚠️ Escalation</h4>
            <p>{response.escalation_reason}</p>
          </div>
        )}

        {response.policy_violations.length > 0 && (
          <div className={styles.card}>
            <h4>Policy Checks</h4>
            <ul className={styles.list}>
              {response.policy_violations.map((violation, i) => (
                <li key={i}>{violation}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {response.retrieved_context.length > 0 && (
        <div className={styles.section}>
          <h4>Retrieved Context ({response.retrieved_context.length})</h4>
          <div className={styles.context}>
            {response.retrieved_context.map((ctx, i) => (
              <div key={i} className={styles.contextItem}>
                {ctx}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className={styles.section}>
        <h4>Agent Trace</h4>
        <div className={styles.trace}>
          {response.agent_trace.map((step, i) => (
            <div key={i} className={styles.traceStep}>
              <span className={styles.stepNumber}>{i + 1}</span>
              <span>{step}</span>
              {i < response.agent_trace.length - 1 && <span className={styles.arrow}>→</span>}
            </div>
          ))}
        </div>
      </div>

      {response.trace_events.length > 0 && (
        <div className={styles.section}>
          <h4>Execution Timeline</h4>
          <div className={styles.timeline}>
            {response.trace_events.map((event, i) => (
              <div key={i} className={styles.timelineItem}>
                <div className={styles.timelineHeader}>
                  <strong>{event.step}</strong>
                  <span className={styles.duration}>{event.duration_ms.toFixed(1)}ms</span>
                </div>
                <p className={styles.timelineMessage}>{event.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {response.recent_turns.length > 0 && (
        <div className={styles.section}>
          <h4>Conversation Memory ({response.recent_turns.length})</h4>
          <div className={styles.memory}>
            {response.recent_turns.map((turn, i) => (
              <div key={i} className={`${styles.turn} ${styles[turn.role]}`}>
                <div className={styles.role}>{turn.role.toUpperCase()}</div>
                <p>{turn.content}</p>
                {turn.intent && <span className={styles.turnIntent}>{turn.intent}</span>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
