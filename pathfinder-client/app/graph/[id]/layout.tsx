"use client"

import { GraphProvider } from '@/contexts/GraphContext'
import { ReactNode, useEffect, useState } from 'react'
import { useGraph } from '@/contexts/GraphContext'

// Wrapper component to provide the GraphContext
function GraphLayoutWrapper({ children }: { children: ReactNode }) {
  return (
    <GraphProvider>
      <GraphLayoutContent>{children}</GraphLayoutContent>
    </GraphProvider>
  )
}

// Main content component that uses the GraphContext
function GraphLayoutContent({ children }: { children: ReactNode }) {
  const { setNodes, setEdges } = useGraph()
  
  // Initialize the graph data
  useEffect(() => {
    // This is sample data - in a real app, you'd fetch this from your backend
    const initialNodes = [
      { id: 1, label: "Transmission Line Theory", title: "node 1 tooltip text" },
      { id: 2, label: "Node 2", title: "node 2 tooltip text" },
      { id: 3, label: "Node 3", title: "node 3 tooltip text" },
      { id: 4, label: "Node 4", title: "node 4 tooltip text" },
      { id: 5, label: "Node 5", title: "node 5 tooltip text" }
    ]
    
    const initialEdges = [
      { from: 1, to: 2 },
      { from: 1, to: 3 },
      { from: 2, to: 4 },
      { from: 2, to: 5 }
    ]
    
    setNodes(initialNodes)
    setEdges(initialEdges)
  }, [setNodes, setEdges])
  
  return <>{children}</>
}

export default GraphLayoutWrapper 