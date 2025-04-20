"use client"

import React, { createContext, useContext, useState, ReactNode } from 'react'

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
const GraphContext = createContext<GraphContextType>({
  nodes: [],
  edges: [],
  setNodes: () => {},
  setEdges: () => {},
  getPrerequisites: () => [],
  getPostRequisites: () => [],
})

// Custom hook to use the graph context
export const useGraph = () => useContext(GraphContext)

interface GraphProviderProps {
  children: ReactNode
}

export const GraphProvider: React.FC<GraphProviderProps> = ({ children }) => {
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])

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