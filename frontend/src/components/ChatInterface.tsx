'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Bot, User, Loader2, Paperclip, ArrowUp } from 'lucide-react'

const suggestedQuestions = [
  "什麼是 DysonV2 的主要特色？",
  "DysonV2 的 Premium 計算公式是什麼？", 
  "如何使用 DysonV2 進行雙幣理財？",
  "DysonV2 的風險管理機制有哪些？"
]

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  timestamp: Date
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageText,
          conversation_history: messages.map(msg => ({
            role: msg.role,
            content: msg.content
          }))
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        sources: data.sources,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '抱歉，發生了錯誤。請稍後再試。',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      sendMessage(input)
    }
  }

  const handleSuggestedQuestion = (question: string) => {
    sendMessage(question)
  }

  return (
    <div className="flex flex-col h-screen bg-black text-white">
      {/* Header - only show when there are no messages */}
      {messages.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center px-4">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-3">Hello there!</h1>
            <p className="text-gray-400 text-lg">您好！我是 DysonV2 專屬的 AI 助手</p>
          </div>

          {/* Suggested Questions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full mb-8">
            {suggestedQuestions.map((question, index) => (
              <Card 
                key={index}
                className="bg-zinc-900 border-zinc-800 hover:bg-zinc-800 transition-colors cursor-pointer rounded-2xl"
                onClick={() => handleSuggestedQuestion(question)}
              >
                <CardContent className="p-4">
                  <p className="text-sm text-gray-300">{question}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Messages - only show when there are messages */}
      {messages.length > 0 && (
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full px-4 py-6 bg-black">
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`flex max-w-[80%] space-x-3 ${
                      message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                    }`}
                  >
                    <Avatar className="w-8 h-8 flex-shrink-0">
                      <AvatarFallback className={`${
                        message.role === 'user' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-white text-black'
                      }`}>
                        {message.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                      </AvatarFallback>
                    </Avatar>
                    
                    <div className="space-y-2">
                      <Card className="bg-zinc-900 border-zinc-800 text-white rounded-2xl">
                        <CardContent className="p-4">
                          {message.role === 'user' ? (
                            <p className="text-sm">{message.content}</p>
                          ) : (
                            <div className="prose prose-sm max-w-none prose-invert">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm, remarkMath]}
                                rehypePlugins={[rehypeKatex]}
                                components={{
                                  h1: ({ children }) => <h1 className="text-lg font-bold mb-2 text-white">{children}</h1>,
                                  h2: ({ children }) => <h2 className="text-md font-bold mb-2 text-white">{children}</h2>,
                                  h3: ({ children }) => <h3 className="text-sm font-bold mb-1 text-white">{children}</h3>,
                                  p: ({ children }) => <p className="mb-2 text-sm leading-relaxed text-gray-200">{children}</p>,
                                  ul: ({ children }) => <ul className="mb-2 ml-4 list-disc text-sm text-gray-200">{children}</ul>,
                                  ol: ({ children }) => <ol className="mb-2 ml-4 list-decimal text-sm text-gray-200">{children}</ol>,
                                  li: ({ children }) => <li className="mb-1 text-gray-200">{children}</li>,
                                  code: ({ children, className }) => {
                                    const isInline = !className
                                    return isInline ? (
                                      <code className="bg-zinc-800 text-yellow-400 px-1 py-0.5 rounded text-xs font-mono">
                                        {children}
                                      </code>
                                    ) : (
                                      <pre className="bg-zinc-800 p-3 rounded-lg text-xs font-mono overflow-x-auto">
                                        <code className="text-gray-200">{children}</code>
                                      </pre>
                                    )
                                  },
                                  strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
                                  em: ({ children }) => <em className="italic text-gray-300">{children}</em>,
                                }}
                              >
                                {message.content}
                              </ReactMarkdown>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                      
                      {/* Sources */}
                      {message.sources && message.sources.length > 0 && (
                        <div className="text-xs text-gray-500">
                          <div className="bg-zinc-800 rounded-lg p-2">
                            <p className="font-medium mb-1">參考來源:</p>
                            <ul className="list-disc list-inside space-y-1">
                              {message.sources.map((source, index) => (
                                <li key={index}>{source}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex space-x-3">
                    <Avatar className="w-8 h-8">
                      <AvatarFallback className="bg-white text-black">
                        <Bot size={16} />
                      </AvatarFallback>
                    </Avatar>
                    <Card className="bg-zinc-900 border-zinc-800 rounded-2xl">
                      <CardContent className="p-4">
                        <div className="flex items-center space-x-2 text-sm text-gray-400">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>正在思考中...</span>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
      )}

      {/* Input Area - Fixed at bottom */}
      <div className="shrink-0 p-4 bg-black border-t border-zinc-800">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSubmit} className="relative">
            <div className="relative flex items-center">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute left-3 z-10 text-gray-400 hover:text-white rounded-full p-2"
              >
                <Paperclip size={16} />
              </Button>
              
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Send a message..."
                disabled={isLoading}
                className="bg-zinc-900 border-zinc-800 text-white placeholder-gray-500 pl-12 pr-12 py-6 rounded-full focus:ring-1 focus:ring-gray-600 focus:border-gray-600"
              />
              
              <Button 
                type="submit" 
                disabled={!input.trim() || isLoading}
                size="sm"
                className="absolute right-3 bg-white text-black hover:bg-gray-200 rounded-full p-2 disabled:opacity-50"
              >
                <ArrowUp size={16} />
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}