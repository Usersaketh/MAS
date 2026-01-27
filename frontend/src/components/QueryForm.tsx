import { useState, type FormEvent } from 'react'
import { queryAPI, QueryResponse } from '../api/client'
import styles from './QueryForm.module.css'

interface QueryFormProps {
  onSubmit: (result: QueryResponse) => void
  onLoading: (loading: boolean) => void
  conversationId: string
  userId: string
}

export const QueryForm: React.FC<QueryFormProps> = ({
  onSubmit,
  onLoading,
  conversationId,
  userId,
}) => {
  const [query, setQuery] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!query.trim()) {
      setError('Please enter a question')
      return
    }

    setError(null)
    onLoading(true)

    try {
      const result = await queryAPI.processQuery({
        user_id: userId,
        conversation_id: conversationId,
        query,
      })
      setQuery('')
      onSubmit(result)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process query')
    } finally {
      onLoading(false)
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.inputGroup}>
        <textarea
          className={styles.textarea}
          placeholder="Ask a question about orders, returns, shipping, billing..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={4}
        />
      </div>
      {error && <div className={styles.error}>{error}</div>}
      <button className={styles.submitBtn} type="submit">
        Send Query
      </button>
    </form>
  )
}
