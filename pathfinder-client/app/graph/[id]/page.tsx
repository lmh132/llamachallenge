"use client"

import { Network } from 'vis-network';
import dynamic from 'next/dynamic'
import 'vis-network/styles/vis-network.css';
import { useRouter, useParams } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { useGraph } from '@/contexts/GraphContext';

// need to import the vis network css in order to show tooltip

const Graph = dynamic(() => import("react-graph-vis"), {
  ssr: false,
});

export default function GraphPage() {
  const router = useRouter();
  const params = useParams();
  const graphId = params.id as string;
  const { nodes, edges } = useGraph();

  const handleSelect = (event: { nodes: number[]; edges: number[] }) => {
    // Your select handler code
  };

  const handleDoubleClick = (event: { nodes: number[] }) => {
    if (event.nodes.length > 0) {
      const nodeId = event.nodes[0];
      router.push(`/graph/${graphId}/node/${nodeId}`);
    }
  };

  const handleGetNetwork = (network: Network) => {
    // Your network handler code
  };

  return (
    <div className="fixed inset-0 bg-black">
      <Button
        onClick={() => router.push('/home')}
        className="absolute top-4 left-4 z-10 bg-zinc-800/50 hover:bg-zinc-700/50 text-white border border-zinc-700/50 shadow-lg backdrop-blur-sm"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Dashboard
      </Button>
      
      <Graph
        graph={{
          nodes: nodes,
          edges: edges
        }}
        options={{
          layout: {
            hierarchical: false
          },
          nodes: {
            color: {
              background: '#1e293b',
              border: '#475569',
              highlight: {
                background: '#2563eb',
                border: '#60a5fa'
              }
            },
            font: {
              color: '#e2e8f0',
              size: 16
            },
            borderWidth: 2,
            shadow: true
          },
          edges: {
            color: {
              color: '#475569',
              highlight: '#60a5fa'
            },
            width: 2,
            smooth: {
              enabled: true,
              type: 'continuous',
              roundness: 0.5
            }
          },
          height: '100%',
          width: '100%',
          interaction: {
            hover: true,
            navigationButtons: true
          },
          physics: {
            stabilization: {
              iterations: 200
            },
            barnesHut: {
              gravitationalConstant: -80000,
              springConstant: 0.001,
              springLength: 200
            }
          }
        }}
        events={{
          select: handleSelect,
          doubleClick: handleDoubleClick
        }}
        getNetwork={handleGetNetwork}
      />
    </div>
  );
}
