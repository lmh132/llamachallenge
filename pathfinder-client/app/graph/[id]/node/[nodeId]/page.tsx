"use client"

import { useParams, useRouter } from 'next/navigation'
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { useGraph } from '@/contexts/GraphContext'
import { useEffect, useState } from 'react'

export default function NodePage() {
  const router = useRouter()
  const params = useParams()
  const graphId = params.id as string
  const nodeId = parseInt(params.nodeId as string)
  const { edges, getPrerequisites, getPostRequisites } = useGraph()
  
  // State to store the prerequisites and post-requisites
  const [prereqs, setPrereqs] = useState<any[]>([])
  const [next, setNext] = useState<any[]>([])
  
  // Compute prerequisites and post-requisites when the component mounts or when edges change
  useEffect(() => {
    if (edges.length > 0) {
      setPrereqs(getPrerequisites(nodeId))
      setNext(getPostRequisites(nodeId))
    }
  }, [edges, nodeId, getPrerequisites, getPostRequisites])

  // This is a placeholder for node data - in a real app, you'd fetch this from your backend
  const nodeData = {
    id: nodeId,
    title: `Node ${nodeId}`,
    summary: "This is an AI-generated summary of the node content. It provides a concise overview of the key concepts, principles, and applications related to this topic. The summary is designed to give you a quick understanding without overwhelming you with details."
  }

  // Function to navigate to a specific node
  const navigateToNode = (targetNodeId: number) => {
    router.push(`/graph/${graphId}/node/${targetNodeId}`)
  }

  return (
    <div className="min-h-screen bg-black p-8">
      <Button
        onClick={() => router.push(`/graph/${graphId}`)}
        className="mb-6 bg-zinc-800/50 hover:bg-zinc-700/50 text-white border border-zinc-700/50 shadow-lg backdrop-blur-sm"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Graph
      </Button>

      <Card className="max-w-2xl mx-auto bg-zinc-900/70 border-zinc-700/50 text-white shadow-lg backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-2xl">{nodeData.title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* AI Summary */}
            <div className="space-y-2">
              <h3 className="text-lg font-medium text-zinc-300">AI Summary</h3>
              <p className="text-zinc-400">{nodeData.summary}</p>
            </div>
            
            {/* Prerequisites */}
            <div className="space-y-2">
              <h3 className="text-lg font-medium text-zinc-300">Prerequisites</h3>
              {prereqs.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {prereqs.map((prereq) => (
                    <Button 
                      key={prereq.from}
                      onClick={() => navigateToNode(prereq.from)}
                      className="bg-blue-600/50 hover:bg-blue-500/50 text-white border border-blue-700/50"
                    >
                      Node {prereq.from}
                    </Button>
                  ))}
                </div>
              ) : (
                <p className="text-zinc-500 italic">No prerequisites</p>
              )}
            </div>
            
            {/* Post-requisites */}
            <div className="space-y-2">
              <h3 className="text-lg font-medium text-zinc-300">Post-requisites</h3>
              {next.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {next.map((postreq) => (
                    <Button 
                      key={postreq.to}
                      onClick={() => navigateToNode(postreq.to)}
                      className="bg-green-600/50 hover:bg-green-500/50 text-white border border-green-700/50"
                    >
                      Node {postreq.to}
                    </Button>
                  ))}
                </div>
              ) : (
                <p className="text-zinc-500 italic">No post-requisites</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 