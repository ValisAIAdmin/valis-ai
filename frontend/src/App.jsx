import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  MessageCircle, 
  Home, 
  Users, 
  Code, 
  Zap, 
  Brain, 
  Rocket,
  Monitor,
  Send,
  Sparkles,
  Globe,
  Star,
  TrendingUp
} from 'lucide-react'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState('landing')
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [currentTask, setCurrentTask] = useState(null)
  const [onlineUsers, setOnlineUsers] = useState(1456)

  // Initialize with welcome message
  useEffect(() => {
    if (currentView === 'chat' && messages.length === 0) {
      setMessages([{
        id: 1,
        type: 'ai',
        content: "Hello! I'm Valis AI. I can help you create websites, applications, presentations, and more. What would you like to build today?",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }])
    }
  }, [currentView, messages.length])

  const sendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        type: 'ai',
        content: `I'll help you with that! I've detected this as a ${detectTaskType(inputMessage)} request. Let me work on this autonomously...`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setMessages(prev => [...prev, aiResponse])
      setIsTyping(false)
      
      // Start task simulation
      startTaskExecution(inputMessage)
    }, 1500)
  }

  const detectTaskType = (input) => {
    const lower = input.toLowerCase()
    if (lower.includes('website') || lower.includes('landing')) return 'website creation'
    if (lower.includes('app') || lower.includes('application')) return 'application development'
    if (lower.includes('presentation') || lower.includes('slides')) return 'presentation creation'
    if (lower.includes('api') || lower.includes('backend')) return 'API development'
    return 'general assistance'
  }

  const startTaskExecution = (input) => {
    const task = {
      id: Date.now(),
      type: detectTaskType(input),
      description: input,
      status: 'planning',
      progress: 0,
      steps: ['Analyzing requirements', 'Generating code', 'Testing functionality', 'Deploying project'],
      currentStep: 0
    }

    setCurrentTask(task)

    // Simulate task progress
    let progress = 0
    const interval = setInterval(() => {
      progress += Math.random() * 20
      if (progress >= 100) {
        progress = 100
        clearInterval(interval)
        
        // Task completed
        setTimeout(() => {
          const completionMessage = {
            id: Date.now(),
            type: 'ai',
            content: `✅ Task completed successfully! Your ${task.type} is ready. You can view it at: https://valis-${task.id.toString().slice(-8)}.vercel.app`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
          setMessages(prev => [...prev, completionMessage])
          setCurrentTask(null)
        }, 1000)
      }

      setCurrentTask(prev => ({
        ...prev,
        progress: Math.min(progress, 100),
        status: progress < 25 ? 'planning' : progress < 50 ? 'executing' : progress < 75 ? 'testing' : progress < 100 ? 'deploying' : 'completed',
        currentStep: Math.floor(progress / 25)
      }))
    }, 800)
  }

  const LandingPage = () => (
    <div className="min-h-screen valis-gradient">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-lg flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white">Valis AI</span>
        </div>
        <div className="flex items-center space-x-4">
          <Button 
            variant="ghost" 
            className="text-white hover:bg-white/10"
            onClick={() => setCurrentView('landing')}
          >
            <Home className="w-4 h-4 mr-2" />
            Home
          </Button>
          <Button 
            variant="ghost" 
            className="text-white hover:bg-white/10"
            onClick={() => setCurrentView('chat')}
          >
            <MessageCircle className="w-4 h-4 mr-2" />
            Chat
          </Button>
          <Button 
            variant="ghost" 
            className="text-white hover:bg-white/10"
            onClick={() => setCurrentView('community')}
          >
            <Users className="w-4 h-4 mr-2" />
            Community
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-6 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-6xl font-bold mb-6">
            <span className="text-white">The Future of </span>
            <span className="valis-gradient-text">Autonomous Intelligence</span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Where every thought becomes action through autonomous AI that builds, deploys, and manages your digital projects in real-time.
          </p>
          <div className="flex justify-center space-x-4">
            <Button 
              className="valis-button-primary px-8 py-3 text-lg font-semibold"
              onClick={() => setCurrentView('chat')}
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Experience Valis
            </Button>
            <Button 
              variant="outline" 
              className="border-cyan-400 text-cyan-400 hover:bg-cyan-400/10 px-8 py-3 text-lg"
              onClick={() => setCurrentView('community')}
            >
              <Users className="w-5 h-5 mr-2" />
              Join Community
            </Button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-6 py-20">
        <div className="grid md:grid-cols-3 gap-8">
          <Card className="valis-card">
            <CardHeader>
              <CardTitle className="flex items-center text-white">
                <Brain className="w-6 h-6 mr-2 text-cyan-400" />
                Autonomous Intelligence
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300">
                AI that thinks, plans, and executes complex tasks without constant guidance. Just describe what you want, and watch it happen.
              </p>
            </CardContent>
          </Card>

          <Card className="valis-card">
            <CardHeader>
              <CardTitle className="flex items-center text-white">
                <Code className="w-6 h-6 mr-2 text-cyan-400" />
                Real-time Execution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300">
                Watch your ideas come to life in real-time. See code being written, applications being built, and projects being deployed live.
              </p>
            </CardContent>
          </Card>

          <Card className="valis-card">
            <CardHeader>
              <CardTitle className="flex items-center text-white">
                <Rocket className="w-6 h-6 mr-2 text-cyan-400" />
                Instant Deployment
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300">
                From concept to live application in minutes. Automatic deployment, testing, and optimization for production-ready results.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Stats Section */}
      <div className="container mx-auto px-6 py-20">
        <div className="grid md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold valis-gradient-text mb-2">12,847</div>
            <div className="text-gray-300">Active Users</div>
          </div>
          <div>
            <div className="text-4xl font-bold valis-gradient-text mb-2">8,934</div>
            <div className="text-gray-300">Projects Created</div>
          </div>
          <div>
            <div className="text-4xl font-bold valis-gradient-text mb-2">567</div>
            <div className="text-gray-300">Templates Shared</div>
          </div>
          <div>
            <div className="text-4xl font-bold valis-gradient-text mb-2">99.9%</div>
            <div className="text-gray-300">Uptime</div>
          </div>
        </div>
      </div>
    </div>
  )

  const ChatInterface = () => (
    <div className="min-h-screen valis-gradient">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 border-b border-white/10">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-lg flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white">Valis AI</span>
          <Badge variant="secondary" className="bg-cyan-400/20 text-cyan-400">
            Autonomous AI Assistant
          </Badge>
        </div>
        <div className="flex items-center space-x-4">
          <Button 
            variant="ghost" 
            className="text-white hover:bg-white/10"
            onClick={() => setCurrentView('landing')}
          >
            <Home className="w-4 h-4" />
          </Button>
          <Button 
            variant="ghost" 
            className="text-white hover:bg-white/10"
            onClick={() => setCurrentView('community')}
          >
            <Users className="w-4 h-4" />
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-6 h-[calc(100vh-88px)] flex flex-col">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user' 
                  ? 'valis-chat-bubble user' 
                  : 'valis-chat-bubble'
              }`}>
                <p className={message.type === 'user' ? 'text-navy-900' : 'text-white'}>
                  {message.content}
                </p>
                <p className={`text-xs mt-1 ${
                  message.type === 'user' ? 'text-navy-700' : 'text-gray-400'
                }`}>
                  {message.timestamp}
                </p>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="valis-chat-bubble px-4 py-2">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full valis-animate-pulse"></div>
                  <div className="w-2 h-2 bg-cyan-400 rounded-full valis-animate-pulse" style={{animationDelay: '0.2s'}}></div>
                  <div className="w-2 h-2 bg-cyan-400 rounded-full valis-animate-pulse" style={{animationDelay: '0.4s'}}></div>
                  <span className="text-white ml-2">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          {/* Task Progress */}
          {currentTask && (
            <div className="valis-card p-4 valis-animate-slide-up">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">
                  <Zap className="w-4 h-4 inline mr-2 text-cyan-400" />
                  {currentTask.status.charAt(0).toUpperCase() + currentTask.status.slice(1)}...
                </span>
                <span className="text-cyan-400 text-sm">{Math.round(currentTask.progress)}%</span>
              </div>
              <div className="valis-progress-bar h-2 mb-2">
                <div 
                  className="valis-progress-fill h-full"
                  style={{ width: `${currentTask.progress}%` }}
                ></div>
              </div>
              <p className="text-gray-300 text-sm">
                {currentTask.steps[Math.min(currentTask.currentStep, currentTask.steps.length - 1)]}
              </p>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="flex space-x-2">
          <Input
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Message Valis AI..."
            className="valis-input flex-1"
          />
          <Button 
            onClick={sendMessage}
            className="valis-button-primary"
            disabled={!inputMessage.trim()}
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )

  const CommunityHub = () => (
    <div className="min-h-screen valis-gradient">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 border-b border-white/10">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-lg flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white">Valis AI Community</span>
        </div>
        <div className="flex items-center space-x-4">
          <Button 
            variant="ghost" 
            className="text-white hover:bg-white/10"
            onClick={() => setCurrentView('landing')}
          >
            <Home className="w-4 h-4" />
          </Button>
          <Button 
            variant="ghost" 
            className="text-white hover:bg-white/10"
            onClick={() => setCurrentView('chat')}
          >
            <MessageCircle className="w-4 h-4" />
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-6">
        {/* Community Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card className="valis-card">
            <CardContent className="p-4 text-center">
              <Users className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{onlineUsers.toLocaleString()}</div>
              <div className="text-gray-300 text-sm">Online Now</div>
            </CardContent>
          </Card>
          
          <Card className="valis-card">
            <CardContent className="p-4 text-center">
              <Code className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">567</div>
              <div className="text-gray-300 text-sm">Templates Shared</div>
            </CardContent>
          </Card>
          
          <Card className="valis-card">
            <CardContent className="p-4 text-center">
              <Rocket className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">8,934</div>
              <div className="text-gray-300 text-sm">Projects Created</div>
            </CardContent>
          </Card>
          
          <Card className="valis-card">
            <CardContent className="p-4 text-center">
              <TrendingUp className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">1,890</div>
              <div className="text-gray-300 text-sm">This Week</div>
            </CardContent>
          </Card>
        </div>

        {/* Featured Projects */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Featured Projects</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                name: "AI Chat Bot",
                author: "Emma_Student",
                category: "AI/ML",
                views: 1250,
                likes: 89
              },
              {
                name: "Task Management App",
                author: "Alex_Dev", 
                category: "Productivity",
                views: 980,
                likes: 67
              },
              {
                name: "Weather Dashboard",
                author: "Sarah_Designer",
                category: "Data Visualization", 
                views: 756,
                likes: 45
              }
            ].map((project, index) => (
              <Card key={index} className="valis-card hover:valis-glow transition-all cursor-pointer">
                <CardHeader>
                  <CardTitle className="text-white text-lg">{project.name}</CardTitle>
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary" className="bg-cyan-400/20 text-cyan-400">
                      {project.category}
                    </Badge>
                    <span className="text-gray-400 text-sm">by {project.author}</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between text-sm text-gray-300">
                    <div className="flex items-center">
                      <Monitor className="w-4 h-4 mr-1" />
                      {project.views} views
                    </div>
                    <div className="flex items-center">
                      <Star className="w-4 h-4 mr-1" />
                      {project.likes} likes
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Community Chat Preview */}
        <Card className="valis-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <MessageCircle className="w-5 h-5 mr-2 text-cyan-400" />
              Community Chat
              <Badge variant="secondary" className="ml-2 bg-cyan-400/20 text-cyan-400">
                {onlineUsers.toLocaleString()} online
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 mb-4">
              {[
                { user: "Alex_Dev", message: "Just deployed my new SaaS landing page! 🚀", time: "2m ago" },
                { user: "Sarah_Designer", message: "The new Valis AI features are incredible!", time: "5m ago" },
                { user: "Mike_Founder", message: "Anyone want to collaborate on an e-commerce project?", time: "8m ago" }
              ].map((chat, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    {chat.user[0]}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-white font-medium text-sm">{chat.user}</span>
                      <span className="text-gray-400 text-xs">{chat.time}</span>
                    </div>
                    <p className="text-gray-300 text-sm">{chat.message}</p>
                  </div>
                </div>
              ))}
            </div>
            <Button 
              className="w-full valis-button-primary"
              onClick={() => setCurrentView('chat')}
            >
              Join the Conversation
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  return (
    <div className="App">
      {currentView === 'landing' && <LandingPage />}
      {currentView === 'chat' && <ChatInterface />}
      {currentView === 'community' && <CommunityHub />}
    </div>
  )
}

export default App

