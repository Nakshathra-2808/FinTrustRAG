// App.js — Day 1 Skeleton
// This is the simplest possible version:
// One button that talks to our backend and shows the response.

import { useState } from "react";

// The URL of our FastAPI backend
const API_URL = "http://localhost:8000";

function App() {
  const [status, setStatus] = useState("Not connected yet");
  const [loading, setLoading] = useState(false);

  // Test the /health endpoint
  const testConnection = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();
      setStatus(data.status);
    } catch (error) {
      setStatus("❌ Cannot reach backend. Is it running?");
    }
    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>💹 FinTrustRAG</h1>
      <p style={styles.subtitle}>
        Financial Document QA with Hallucination Detection
      </p>

      <div style={styles.card}>
        <h2>Day 1: Connection Test</h2>
        <p>Backend status: <strong>{status}</strong></p>
        <button
          style={styles.button}
          onClick={testConnection}
          disabled={loading}
        >
          {loading ? "Connecting..." : "Test Backend Connection"}
        </button>
      </div>
    </div>
  );
}

// Inline styles (we'll move to CSS later)
const styles = {
  container: {
    maxWidth: "800px",
    margin: "0 auto",
    padding: "40px 20px",
    fontFamily: "Arial, sans-serif",
  },
  title: {
    fontSize: "2.5rem",
    color: "#1a365d",
    marginBottom: "8px",
  },
  subtitle: {
    color: "#4a5568",
    marginBottom: "32px",
  },
  card: {
    background: "#f7fafc",
    border: "1px solid #e2e8f0",
    borderRadius: "8px",
    padding: "24px",
  },
  button: {
    background: "#2b6cb0",
    color: "white",
    border: "none",
    padding: "10px 24px",
    borderRadius: "6px",
    fontSize: "1rem",
    cursor: "pointer",
    marginTop: "12px",
  },
};

export default App;
