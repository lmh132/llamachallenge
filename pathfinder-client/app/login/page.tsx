"use client"

import type React from "react"

import { useContext, useState } from "react"
import { Button } from "../../components/ui/button"
import { Input } from "../../components/ui/input"
import { Label } from "../../components/ui/label"
import { cn } from "../../lib/utils"
import { School, BookOpen, GraduationCap, Briefcase } from "lucide-react"
import { AuthContext } from "@/contexts/AuthContext"
type EducationLevel = "elementary" | "highschool" | "undergrad" | "graduate"

interface EducationOption {
  value: EducationLevel
  label: string
  icon: React.ReactNode
}

export default function AuthScreen() {
  // Form state

  const { signIn, signUp } = useContext(AuthContext);
  
  const [isLogin, setIsLogin] = useState(false)
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [selectedEducation, setSelectedEducation] = useState<EducationLevel | null>(null)

  const educationOptions: EducationOption[] = [
    {
      value: "elementary",
      label: "Elementary",
      icon: <School className="h-6 w-6" />,
    },
    {
      value: "highschool",
      label: "High School",
      icon: <BookOpen className="h-6 w-6" />,
    },
    {
      value: "undergrad",
      label: "Undergrad",
      icon: <GraduationCap className="h-6 w-6" />,
    },
    {
      value: "graduate",
      label: "Graduate",
      icon: <Briefcase className="h-6 w-6" />,
    },
  ]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (isLogin) {
      signIn(email, password)
    } else {
      signUp(email, password, selectedEducation!)
    }
  }

  const resetForm = () => {
    setName("")
    setEmail("")
    setPassword("")
    setSelectedEducation(null)
  }

  const toggleMode = () => {
    setIsLogin(!isLogin)
    resetForm()
  }

  return (
    <main className="min-h-screen w-full flex items-center justify-center bg-black">
      <div className="w-full min-h-screen md:min-h-0 md:max-w-md p-8 bg-zinc-900 md:rounded-xl md:shadow-lg md:border border-zinc-800">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white">{isLogin ? "Welcome Back" : "Create Account"}</h1>
          <p className="text-zinc-400 mt-2">{isLogin ? "Sign in to access your account" : "Sign up to get started"}</p>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {!isLogin && (
            <div className="space-y-2">
              <Label htmlFor="name" className="text-zinc-300">Full Name</Label>
              <Input 
                id="name" 
                placeholder="John Doe" 
                required 
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500 focus:border-white focus:ring-white"
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="email" className="text-zinc-300">Email</Label>
            <Input 
              id="email" 
              type="email" 
              placeholder="you@example.com" 
              required 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500 focus:border-white focus:ring-white"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-zinc-300">Password</Label>
            <Input 
              id="password" 
              type="password" 
              required 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-zinc-800 border-zinc-700 text-white focus:border-white focus:ring-white"
            />
          </div>

          {!isLogin && (
            <div className="space-y-3">
              <Label className="text-zinc-300">Education Level</Label>
              <div className="grid grid-cols-2 gap-4">
                {educationOptions.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setSelectedEducation(option.value)}
                    className={cn(
                      "flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all duration-200 hover:bg-zinc-800",
                      selectedEducation === option.value 
                        ? "border-white bg-zinc-800" 
                        : "border-zinc-700 bg-zinc-900"
                    )}
                  >
                    <div className="w-12 h-12 rounded-full bg-zinc-800 flex items-center justify-center mb-2 text-white">
                      {option.icon}
                    </div>
                    <span className="text-sm font-medium text-zinc-300">{option.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <Button type="submit" className="w-full bg-white hover:bg-zinc-200 text-black">
            {isLogin ? "Sign In" : "Create Account"}
          </Button>
        </form>

        <div className="text-center mt-6">
          <button 
            type="button" 
            onClick={toggleMode} 
            className="text-zinc-400 hover:text-white text-sm hover:underline"
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
          </button>
        </div>
      </div>
    </main>
  )
}
