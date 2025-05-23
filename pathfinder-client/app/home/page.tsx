"use client"

import { useState, useEffect, useContext } from "react"
import Link from "next/link"
import Image from "next/image"
import { CalendarIcon, FilterIcon, LogOut, PlusCircle, Search, SortAsc, SortDesc, Tag } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"
import { AuthContext } from "@/contexts/AuthContext"
import { createGraph } from "@/utils/authAPI"
import { Graph } from "@/contexts/AuthContext"
// Sample data for graphs
/** 
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
] **/

// Get all unique tags from the graphs

export default function Home() {
  const { logout, graphs, addGraph, user } = useContext(AuthContext);
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")
  const [sortBy, setSortBy] = useState<"date" | "title">("date")
  const [newGraphTitle, setNewGraphTitle] = useState("")
  const [newGraphDescription, setNewGraphDescription] = useState("")
  const [newGraphFile, setNewGraphFile] = useState<File | null>(null)
  const [newGraphTags, setNewGraphTags] = useState<string[]>([])
  const [newTagInput, setNewTagInput] = useState("")
  const router = useRouter()
  


  const allTags = graphs ? 
  Array.from(new Set(graphs.map((graph : Graph) => graph.tags).flat() || [])) : [];

  const handleToggleTag = (tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    )
  }

  // Filter and sort graphs
  const filteredGraphs = graphs
    .filter((graph) => {
      const matchesSearch = graph.title.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesTags = selectedTags.length === 0 || selectedTags.some((tag) => graph.tags.includes(tag))
      return matchesSearch && matchesTags
    })
    .sort((a, b) => {
      if (sortBy === "date") {
        return sortOrder === "asc"
          ? new Date(a.date).getTime() - new Date(b.date).getTime()
          : new Date(b.date).getTime() - new Date(a.date).getTime()
      } else {
        return sortOrder === "asc" ? a.title.localeCompare(b.title) : b.title.localeCompare(a.title)
      }
    })

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  const handleCreateGraph = async () => {
    const ogGraph = {
      title: newGraphTitle,
      image: "/placeholder.svg?height=200&width=300",
      tags: newGraphTags,
    };
    
    const newGraph = await createGraph({
      user_id: user?.uid,
      name: newGraphTitle,
      topic: newGraphDescription,
      tags: "asdfasdf",
    }); //fix
    addGraph(ogGraph, newGraph.graph_id); //fix
    
    setNewGraphTitle("");
    setNewGraphDescription("");
    setNewGraphFile(null);
    setNewGraphTags([]);
    setNewTagInput("");
    
    //const newGraphId = Math.max(...graphs.map(g => g.id)) + 1;
    router.push(`/create/${newGraph.graph_id}`);
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur">
        <div className="w-full max-w-full flex items-center justify-between h-16 px-4">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold">Welcome Back, Evan</h1>
            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-muted-foreground hover:text-foreground">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <PlusCircle className="w-4 h-4 mr-2" />
                Create New Graph
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Create New Graph</DialogTitle>
                <DialogDescription>Create a new graph visualization for your data.</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <label htmlFor="title" className="text-sm font-medium">Title</label>
                  <Input
                    id="title"
                    value={newGraphTitle}
                    onChange={(e) => setNewGraphTitle(e.target.value)}
                    placeholder="Enter graph title"
                  />
                </div>
                <div className="grid gap-2">
                  <label htmlFor="description" className="text-sm font-medium">Description</label>
                  <Input
                    id="description"
                    value={newGraphDescription}
                    onChange={(e) => setNewGraphDescription(e.target.value)}
                    placeholder="Enter graph description"
                  />
                </div>
                <div className="grid gap-2">
                  <label htmlFor="file" className="text-sm font-medium">Upload PDF</label>
                  <Input
                    id="file"
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setNewGraphFile(e.target.files?.[0] || null)}
                  />
                </div>
                <div className="grid gap-2">
                  <label className="text-sm font-medium">Tags</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {newGraphTags.map((tag) => (
                      <Badge
                        key={tag}
                        variant="secondary"
                        className="cursor-pointer"
                        onClick={() => setNewGraphTags(newGraphTags.filter(t => t !== tag))}
                      >
                        {tag} ×
                      </Badge>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Input
                      value={newTagInput}
                      onChange={(e) => setNewTagInput(e.target.value)}
                      placeholder="Add new tag"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && newTagInput.trim()) {
                          setNewGraphTags([...newGraphTags, newTagInput.trim()]);
                          setNewTagInput('');
                        }
                      }}
                    />
                    <Button
                      variant="outline"
                      onClick={() => {
                        if (newTagInput.trim()) {
                          setNewGraphTags([...newGraphTags, newTagInput.trim()]);
                          setNewTagInput('');
                        }
                      }}
                    >
                      Add
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    <div className="text-sm text-muted-foreground mb-1 w-full">Suggested tags:</div>
                    {allTags.map((tag) => (
                      <Badge
                        key={tag}
                        variant={newGraphTags.includes(tag) ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => {
                          if (newGraphTags.includes(tag)) {
                            setNewGraphTags(newGraphTags.filter(t => t !== tag));
                          } else {
                            setNewGraphTags([...newGraphTags, tag]);
                          }
                        }}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
                <Button onClick={handleCreateGraph}>
                  Create Graph
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </header>

      <main className="w-full max-w-full px-4 py-6">
        <div className="flex flex-col gap-6">
          <div className="grid gap-4 md:grid-cols-[1fr_auto]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search graphs..."
                className="pl-9"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon">
                    <FilterIcon className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <div className="p-2">
                    <div className="font-medium mb-2">Filter by Tags</div>
                    <div className="flex flex-wrap gap-1">
                      {allTags.map((tag) => (
                        <Badge
                          key={tag}
                          variant={selectedTags.includes(tag) ? "default" : "outline"}
                          className="cursor-pointer"
                          onClick={() => handleToggleTag(tag)}
                        >
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </DropdownMenuContent>
              </DropdownMenu>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon">
                    {sortOrder === "asc" ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setSortBy("date")}>
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    <span>Sort by Date</span>
                    {sortBy === "date" && <span className="ml-auto">✓</span>}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortBy("title")}>
                    <Tag className="mr-2 h-4 w-4" />
                    <span>Sort by Title</span>
                    {sortBy === "title" && <span className="ml-auto">✓</span>}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortOrder(prev => prev === "asc" ? "desc" : "asc")}>
                    {sortOrder === "asc" ? <SortAsc className="mr-2 h-4 w-4" /> : <SortDesc className="mr-2 h-4 w-4" />}
                    <span>{sortOrder === "asc" ? "Ascending" : "Descending"}</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          {selectedTags.length > 0 && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm text-muted-foreground">Filtered by:</span>
              {selectedTags.map((tag) => (
                <Badge key={tag} variant="secondary" className="cursor-pointer" onClick={() => handleToggleTag(tag)}>
                  {tag}
                  <span className="ml-1">×</span>
                </Badge>
              ))}
              <Button variant="ghost" size="sm" onClick={() => setSelectedTags([])} className="h-7 text-xs">
                Clear all
              </Button>
            </div>
          )}

          {filteredGraphs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <p className="text-muted-foreground">No graphs found matching your criteria.</p>
              <Button
                variant="link"
                onClick={() => {
                  setSearchQuery("")
                  setSelectedTags([])
                }}
              >
                Clear filters
              </Button>
            </div>
          ) : (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {filteredGraphs.map((graph) => (
                <Link href={`/graph/${graph.id}`} key={graph.id} className="group">
                  <Card className="overflow-hidden transition-all hover:shadow-md">
                    <CardHeader className="p-0">
                      <div className="relative aspect-[3/2] w-full overflow-hidden">
                        <Image
                          src={graph.image || "/placeholder.svg"}
                          alt={graph.title}
                          fill
                          className="object-cover transition-transform group-hover:scale-105"
                        />
                      </div>
                    </CardHeader>
                    <CardContent className="p-4">
                      <h2 className="font-semibold line-clamp-1">{graph.title}</h2>
                      <p className="text-sm text-muted-foreground">{new Date(graph.date).toLocaleDateString()}</p>
                    </CardContent>
                    <CardFooter className="flex flex-wrap gap-1 p-4 pt-0">
                      {graph.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </CardFooter>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
