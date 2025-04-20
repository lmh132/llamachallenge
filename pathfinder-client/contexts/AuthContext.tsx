'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { 
  User,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup
} from 'firebase/auth';
import { auth } from '../firebase/firebaseconfig.js';
import { useRouter } from 'next/navigation';

interface Graph {
  id: number;
  title: string;
  image: string;
  tags: string[];
  date: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  graphs: Graph[];
  addGraph: (graph: Omit<Graph, "id" | "date">) => void;
  updateGraph: (id: number, graph: Partial<Graph>) => void;
  deleteGraph: (id: number) => void;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, education: string) => Promise<void>;
  logout: () => Promise<void>;
}

// Initial graphs data
const initialGraphs = [
  {
    id: 1,
    title: "Monthly Revenue Analysis",
    image: "/placeholder.svg?height=200&width=300",
    tags: ["Finance", "Revenue", "Monthly"],
    date: "2024-04-15",
  },
  {
    id: 2,
    title: "User Engagement Metrics",
    image: "/placeholder.svg?height=200&width=300",
    tags: ["Users", "Engagement", "Analytics"],
    date: "2024-04-10",
  },
  {
    id: 3,
    title: "Product Performance Comparison",
    image: "/placeholder.svg?height=200&width=300",
    tags: ["Product", "Performance", "Comparison"],
    date: "2024-04-05",
  },
  {
    id: 4,
    title: "Regional Sales Distribution",
    image: "/placeholder.svg?height=200&width=300",
    tags: ["Sales", "Regional", "Distribution"],
    date: "2024-04-01",
  },
  {
    id: 5,
    title: "Customer Satisfaction Trends",
    image: "/placeholder.svg?height=200&width=300",
    tags: ["Customer", "Satisfaction", "Trends"],
    date: "2024-03-28",
  },
  {
    id: 6,
    title: "Marketing Campaign Results",
    image: "/placeholder.svg?height=200&width=300",
    tags: ["Marketing", "Campaign", "Results"],
    date: "2024-03-25",
  },
];

export const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  graphs: [],
  addGraph: () => {},
  updateGraph: () => {},
  deleteGraph: () => {},
  signIn: async () => {},
  signUp: async () => {},
  logout: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [graphs, setGraphs] = useState<Graph[]>(initialGraphs);
  const router = useRouter();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const addGraph = (newGraph: Omit<Graph, "id" | "date">) => {
    setGraphs(currentGraphs => {
      const nextId = Math.max(...currentGraphs.map(g => g.id), 0) + 1;
      return [{
        ...newGraph,
        id: nextId,
        date: new Date().toISOString().split('T')[0]
      }, ...currentGraphs];
    });
  };

  const updateGraph = (id: number, updates: Partial<Graph>) => {
    setGraphs(currentGraphs =>
      currentGraphs.map(graph =>
        graph.id === id ? { ...graph, ...updates } : graph
      )
    );
  };

  const deleteGraph = (id: number) => {
    setGraphs(currentGraphs => currentGraphs.filter(graph => graph.id !== id));
  };

  const signIn = async (email: string, password: string) => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
      router.push('/home');
    } catch (error) {
      throw error;
    }
  };

  const signUp = async (email: string, password: string, education: string) => {
    try {
      await createUserWithEmailAndPassword(auth, email, password);
      router.push('/home');
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      throw error;
    }
  };

  const signInWithGoogle = async () => {
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
    } catch (error) {
      throw error;
    }
  };

  const value = {
    user,
    loading,
    graphs,
    addGraph,
    updateGraph,
    deleteGraph,
    signIn,
    signUp,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 