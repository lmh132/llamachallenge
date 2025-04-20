"use client"

import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react'

// Define types for our graph data
export interface Node {
  id: number
  label: string
  title?: string
}

export interface Edge {
  from: number
  to: number
}

interface GraphContextType {
  nodes: Node[]
  edges: Edge[]
  setNodes: (nodes: Node[]) => void
  setEdges: (edges: Edge[]) => void
  getPrerequisites: (nodeId: number) => Edge[]
  getPostRequisites: (nodeId: number) => Edge[]
}

// Create the context with default values
export const GraphContext = createContext<GraphContextType>({
  nodes: [],
  edges: [],
  setNodes: () => {},
  setEdges: () => {},
  getPrerequisites: () => [],
  getPostRequisites: () => [],
})

// Custom hook to use the graph context
export const useGraph = () => {
  const context = useContext(GraphContext)
  if (!context) {
    throw new Error('useGraph must be used within a GraphProvider')
  }
  return context
}

interface GraphProviderProps {
  children: ReactNode
}

export const GraphProvider: React.FC<GraphProviderProps> = ({ children }) => {
  // Initialize state from localStorage if available, otherwise use empty arrays
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])

  // Load initial data
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
  }, []) // Only run once on mount

  // Helper function to get prerequisites for a node
  const getPrerequisites = (nodeId: number): Edge[] => {
    return edges.filter(edge => edge.to === nodeId)
  }

  // Helper function to get post-requisites for a node
  const getPostRequisites = (nodeId: number): Edge[] => {
    return edges.filter(edge => edge.from === nodeId)
  }

  const value = {
    nodes,
    edges,
    setNodes,
    setEdges,
    getPrerequisites,
    getPostRequisites,
  }

  return <GraphContext.Provider value={value}>{children}</GraphContext.Provider>
} 