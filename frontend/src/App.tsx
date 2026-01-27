import { useState, useRef } from 'react'
import { QueryForm } from './components/QueryForm'
import { ResponseDisplay } from './components/ResponseDisplay'
import { DocumentManager } from './components/DocumentManager'
import { Stats } from './components/Stats'
import { QueryResponse } from './api/client'
import styles from './App.module.css'

function App() {
  const [response, setResponse] = useState<QueryResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [userId] = useState('demo-user')
  const [conversationId] = useState('demo-conversation')
  const [showDocs, setShowDocs] = useState(true)
  const [statsKey, setStatsKey] = useState(0)
  const responseRef = useRef<HTMLDivElement>(null)

  const handleQuerySubmit = (result: QueryResponse) => {
    setResponse(result)
    // Scroll to response
    setTimeout(() => {
      responseRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  }

  const handleDocsSuccess = () => {
    setStatsKey((k) => k + 1)
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div>
            <h1>🤖 MAS - Multi-Agent Support System</h1>
            <p>Intelligent customer query processing with LangGraph, FAISS, and Ollama</p>
          </div>
          <button
            className={styles.toggleBtn}
            onClick={() => setShowDocs(!showDocs)}
          >
            {showDocs ? '✕ Hide Setup' : '✓ Show Setup'}
          </button>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.layout}>
          {/* Sidebar */}
          <aside className={styles.sidebar}>
            {showDocs && (
              <>
                <DocumentManager onSuccess={handleDocsSuccess} />
                <Stats key={statsKey} />
                
                <div className={styles.infoCard}>
                  <h3>💡 Quick Start</h3>
                  <ol className={styles.steps}>
                    <li>Upload support documents above</li>
                    <li>Ask a customer question</li>
                    <li>See multi-agent response</li>
                    <li>Inspect traces & memory</li>
                  </ol>
                </div>

                <div className={styles.infoCard}>
                  <h3>📋 Session Info</h3>
                  <p className={styles.info}>User: <code>{userId}</code></p>
                  <p className={styles.info}>Conv: <code>{conversationId}</code></p>
                </div>
              </>
            )}
          </aside>

          {/* Main Content */}
          <section className={styles.content}>
            <div className={styles.card}>
              <h2>Ask a Question</h2>
              <QueryForm
                onSubmit={handleQuerySubmit}
                onLoading={setLoading}
                conversationId={conversationId}
                userId={userId}
              />
              {loading && <p className={styles.loading}>Processing query...</p>}
            </div>

            {response && (
              <div ref={responseRef} className={styles.card}>
                <ResponseDisplay response={response} />
              </div>
            )}
          </section>
        </div>
      </main>

      <footer className={styles.footer}>
        <p>Built with FastAPI • LangGraph • FAISS • Ollama</p>
        <p>
          API: <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
            http://localhost:8000/docs
          </a>
        </p>
      </footer>
    </div>
  )
}

export default App
