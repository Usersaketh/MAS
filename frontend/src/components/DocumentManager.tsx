import { useState, type FormEvent } from 'react'
import { documentsAPI, DocumentIngestResponse } from '../api/client'
import styles from './DocumentManager.module.css'

interface DocumentManagerProps {
  onSuccess?: () => void
}

export const DocumentManager: React.FC<DocumentManagerProps> = ({ onSuccess }) => {
  const [docs, setDocs] = useState<string[]>([''])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DocumentIngestResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleDocChange = (index: number, value: string) => {
    const newDocs = [...docs]
    newDocs[index] = value
    setDocs(newDocs)
  }

  const addDocField = () => {
    setDocs([...docs, ''])
  }

  const removeDocField = (index: number) => {
    setDocs(docs.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const nonEmptyDocs = docs.filter((d) => d.trim())

    if (nonEmptyDocs.length === 0) {
      setError('Please enter at least one document')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const res = await documentsAPI.ingest(nonEmptyDocs)
      setResult(res)
      setDocs([''])
      onSuccess?.()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to ingest documents')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.card}>
      <h3>📚 Ingest Documents</h3>
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.docsContainer}>
          {docs.map((doc, i) => (
            <div key={i} className={styles.docField}>
              <textarea
                placeholder={`Document ${i + 1} (e.g., policy text, FAQ)`}
                value={doc}
                onChange={(e) => handleDocChange(i, e.target.value)}
                rows={3}
              />
              {docs.length > 1 && (
                <button
                  type="button"
                  className={styles.removeBtn}
                  onClick={() => removeDocField(i)}
                >
                  Remove
                </button>
              )}
            </div>
          ))}
        </div>

        <button type="button" className={styles.addBtn} onClick={addDocField}>
          + Add Another Document
        </button>

        {error && <div className={styles.error}>{error}</div>}
        {result && (
          <div className={styles.success}>
            ✓ Added {result.added_count} documents. Total in index: {result.total_documents}
          </div>
        )}

        <button type="submit" className={styles.submitBtn} disabled={loading}>
          {loading ? 'Ingesting...' : 'Ingest Documents'}
        </button>
      </form>
    </div>
  )
}
