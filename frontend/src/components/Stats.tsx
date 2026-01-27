import { useEffect, useState } from 'react'
import { documentsAPI, RetrieverStats } from '../api/client'
import styles from './Stats.module.css'

export const Stats: React.FC = () => {
  const [stats, setStats] = useState<RetrieverStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await documentsAPI.stats()
      setStats(data)
    } catch (err: any) {
      setError('Failed to load stats')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.card}>
      <h3>📊 Index Status</h3>
      {loading && <p>Loading...</p>}
      {error && <p className={styles.error}>{error}</p>}
      {stats && (
        <div className={styles.stats}>
          <div className={styles.stat}>
            <div className={styles.label}>Documents Indexed</div>
            <div className={styles.value}>{stats.metadata_count}</div>
          </div>
          <div className={styles.stat}>
            <div className={styles.label}>FAISS Index Size</div>
            <div className={styles.value}>{stats.index_size}</div>
          </div>
        </div>
      )}
      <button className={styles.refreshBtn} onClick={loadStats}>
        🔄 Refresh
      </button>
    </div>
  )
}
