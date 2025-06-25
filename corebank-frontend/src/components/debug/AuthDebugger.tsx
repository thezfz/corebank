import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

interface AuthDebuggerProps {
  enabled?: boolean
}

export default function AuthDebugger({ enabled = false }: AuthDebuggerProps) {
  const { user, isLoading } = useAuth()
  const location = useLocation()
  const [logs, setLogs] = useState<string[]>([])

  useEffect(() => {
    if (!enabled) return

    const timestamp = new Date().toLocaleTimeString()
    const logEntry = `[${timestamp}] User: ${user ? user.username : 'null'}, Loading: ${isLoading}, Path: ${location.pathname}`
    
    setLogs(prev => [...prev.slice(-9), logEntry]) // Keep last 10 logs
    console.log('AuthDebugger:', logEntry)
  }, [user, isLoading, location.pathname, enabled])

  if (!enabled) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      width: '400px',
      maxHeight: '300px',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      color: 'white',
      padding: '10px',
      fontSize: '12px',
      fontFamily: 'monospace',
      zIndex: 9999,
      overflow: 'auto'
    }}>
      <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>🔍 Auth Debugger</div>
      <div>User: {user ? `${user.username} (${user.id})` : 'null'}</div>
      <div>Loading: {isLoading ? 'true' : 'false'}</div>
      <div>Path: {location.pathname}</div>
      <div style={{ marginTop: '10px', fontSize: '10px' }}>
        <div style={{ fontWeight: 'bold' }}>Recent logs:</div>
        {logs.map((log, index) => (
          <div key={index} style={{ opacity: 0.7 }}>{log}</div>
        ))}
      </div>
    </div>
  )
}
