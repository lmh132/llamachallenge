"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"

interface Message {
  text: string
  type: "ai" | "rating" | "input"
  complete: boolean
}

interface ConversationStep {
  message: string
  type: "intro" | "rating" | "final"
  topic?: string
  labels?: {
    start: string
    end: string
  }
}

export default function CreatePage() {
  const router = useRouter()
  const { id } = useParams()
  const [currentStep, setCurrentStep] = useState(0)
  const [ratings, setRatings] = useState<Record<string, number>>({})
  const [isTyping, setIsTyping] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [hasInitialized, setHasInitialized] = useState(false)
  const [typedMessages, setTypedMessages] = useState<number[]>([])
  const conversationSteps: ConversationStep[] = [
    {
      message: "Hi! I'm here to help you create a new graph. I'll ask you a few questions to understand your needs better.",
      type: "intro"
    },
    {
      message: "How familiar are you with data visualization?",
      type: "rating",
      topic: "visualization_familiarity",
      labels: {
        start: "Not familiar",
        end: "Very familiar"
      }
    },
    {
      message: "How complex is the data you're working with?",
      type: "rating",
      topic: "data_complexity",
      labels: {
        start: "Very simple",
        end: "Very complex"
      }
    },
    {
      message: "How technical is your target audience?",
      type: "rating",
      topic: "audience_expertise",
      labels: {
        start: "Non-technical",
        end: "Highly technical"
      }
    },
    {
      message: "How interactive would you like the visualization to be?",
      type: "rating",
      topic: "interactivity_level",
      labels: {
        start: "Static",
        end: "Highly interactive"
      }
    },
    {
      message: "Perfect! Based on your responses, I can help create a visualization that matches your needs. Let me analyze your preferences and suggest the best options.",
      type: "final"
    }
  ]

  useEffect(() => {
    if (!hasInitialized) {
      setHasInitialized(true)
      typeMessage(0)
    }
  }, [hasInitialized])

  const typeMessage = async (stepIndex: number) => {
    console.log("stepIndex", stepIndex)
    if (typedMessages.includes(stepIndex)) return;
    typedMessages.push(stepIndex);
    if (stepIndex >= conversationSteps.length) return;

    setIsTyping(true)
    const message = conversationSteps[stepIndex].message
    
    // Add initial empty message
    setMessages(prev => [...prev, { text: "", type: "ai", complete: false }])
    
    // Type out the message
    for (let i = 0; i < message.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 30))
      setMessages(prev => {
        const newMessages = [...prev]
        newMessages[newMessages.length - 1] = {
          text: message.slice(0, i + 1),
          type: "ai",
          complete: false
        }
        return newMessages
      })
    }

    // Mark as complete
    setMessages(prev => {
      const newMessages = [...prev]
      newMessages[newMessages.length - 1] = {
        text: message,
        type: "ai",
        complete: true
      }
      return newMessages
    })
    setIsTyping(false)

    if (stepIndex === 0) {
      setTimeout(() => {
        setCurrentStep(1)
        typeMessage(1)
      }, 500)
    }
    if (stepIndex === conversationSteps.length - 1) {
      setTimeout(() => {
        router.push(`/graph/${id}`)
      }, 500)
    }
  }

  const handleRating = (rating: number) => {
    const currentTopic = conversationSteps[currentStep].topic
    if (!currentTopic) return

    setRatings(prev => ({ ...prev, [currentTopic]: rating }))
    
    const labels = conversationSteps[currentStep].labels
    const ratingText = labels 
      ? `Selected ${rating}/10 (${rating <= 3 ? labels.start : rating >= 8 ? labels.end : 'Moderate'})`
      : `Selected ${rating}/10`
    
    setMessages(prev => [...prev, {
      text: ratingText,
      type: "rating",
      complete: true
    }])

    const nextStep = currentStep + 1
    setTimeout(() => {
      setCurrentStep(nextStep)
      typeMessage(nextStep)
    }, 500)
  }

  const shouldShowRating = () => {
    return !isTyping && currentStep < conversationSteps.length && conversationSteps[currentStep].type === "rating"
  }

  const getCurrentLabels = () => {
    if (shouldShowRating()) {
      return conversationSteps[currentStep].labels ?? { start: "", end: "" }
    }
    return { start: "", end: "" }
  }

  const getCurrentRating = () => {
    const currentTopic = conversationSteps[currentStep].topic
    return currentTopic ? ratings[currentTopic] : undefined
  }

  return (
    <div className="min-h-screen bg-black">
      <div className="container max-w-2xl mx-auto py-8">
        <Card className="p-6 bg-zinc-900/70 border border-zinc-700/50 shadow-lg backdrop-blur-sm">
          <div className="flex flex-col">
            <div className="space-y-6">
              {messages.map((message, index) => (
                <div key={index} className="flex items-start gap-4">
                  {message.type === "ai" && (
                    <>
                      <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center shadow-md flex-shrink-0">
                        <span className="text-sm font-medium text-black">AI</span>
                      </div>
                      <div className="flex-1 bg-zinc-800/50 p-4 rounded-2xl rounded-tl-none border border-zinc-700/50">
                        <p className="text-lg text-white">
                          {message.text}
                          {!message.complete && <span className="animate-pulse text-white">▋</span>}
                        </p>
                      </div>
                    </>
                  )}
                  {message.type === "rating" && (
                    <div className="flex-1 ml-14">
                      <p className="text-zinc-400 italic">{message.text}</p>
                    </div>
                  )}
                </div>
              ))}

              {shouldShowRating() && (
                <div className="space-y-6 mt-8 ml-14">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center gap-2">
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((rating) => (
                        <Button
                          key={rating}
                          variant={getCurrentRating() === rating ? "default" : "outline"}
                          size="sm"
                          className={`w-10 h-10 p-0 ${
                            getCurrentRating() === rating 
                              ? "bg-white text-black border-white" 
                              : "border-zinc-500 text-white hover:bg-zinc-800 hover:border-white"
                          }`}
                          onClick={() => handleRating(rating)}
                        >
                          {rating}
                        </Button>
                      ))}
                    </div>
                    <div className="flex justify-between text-sm text-zinc-300">
                      <span>{getCurrentLabels().start}</span>
                      <span>{getCurrentLabels().end}</span>
                    </div>
                  </div>
                </div>
              )}

              {currentStep >= conversationSteps.length && (
                <div className="text-center py-8">
                  <p className="text-lg mb-4 text-white">Thank you for providing that information!</p>
                  <p className="text-zinc-300 mb-6">
                    I'll use this to help create the perfect graph for you.
                  </p>
                  <Button 
                    onClick={() => router.push('/home')}
                    className="bg-white text-black hover:bg-zinc-200"
                  >
                    Return to Dashboard
                  </Button>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
} 