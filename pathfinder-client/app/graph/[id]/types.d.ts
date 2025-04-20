declare module 'react-graph-vis' {
  import { Network, Options, Node, Edge } from 'vis-network';
  
  interface GraphEvents {
    select?: (params: { nodes: number[]; edges: number[] }) => void;
    [key: string]: ((params: any) => void) | undefined;
  }

  interface GraphProps {
    graph: {
      nodes: Node[];
      edges: Edge[];
    };
    options?: Options;
    events?: GraphEvents;
    getNetwork?: (network: Network) => void;
  }

  const Graph: React.ComponentType<GraphProps>;
  export default Graph;
} 