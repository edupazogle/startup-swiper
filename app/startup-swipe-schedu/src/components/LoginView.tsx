import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { toast } from 'sonner'
import { authService } from '@/lib/authService'
import logoVC from '@/assets/images/logo_vc.png'
import logoMain from '@/assets/images/f8cba53d-0d66-4aab-b97c-8fa66871fa8b.png'

interface LoginViewProps {
  onLogin: (email: string, name: string) => void
}

export function LoginView({ onLogin }: LoginViewProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const user = await authService.login(email, password)
      
      // Extract name from user data or email
      const name = user.full_name || email.split('@')[0].split('.').map(part => 
        part.charAt(0).toUpperCase() + part.slice(1)
      ).join(' ')

      toast.success(`Welcome, ${name}!`)
      onLogin(email, name)
    } catch (error) {
      toast.error('Login failed. Please check your credentials.')
      console.error('Login error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      </div>

      <Card className="w-full max-w-md z-10 bg-black/50 border-white/10 backdrop-blur-sm">
        <div className="p-8">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <img src={logoVC} alt="AXA Venture Clienting" className="h-8 opacity-90" />
          </div>

          {/* Title */}
          <h1 className="text-2xl font-bold text-white text-center mb-2">
            Startup Rise
          </h1>
          <p className="text-white/60 text-center mb-8">
            Discover and connect with innovative startups
          </p>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-white mb-2">
                Email
              </label>
              <Input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-white/10 border-white/20 text-white placeholder:text-white/40"
                required
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-white mb-2">
                Password
              </label>
              <Input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-white/10 border-white/20 text-white placeholder:text-white/40"
                required
                disabled={isLoading}
              />
            </div>

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold py-3 touch-manipulation"
              disabled={isLoading}
              style={{ WebkitTapHighlightColor: 'transparent' }}
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </Button>
          </form>

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-white/40 text-xs">
              AXA Venture Clienting © 2025
            </p>
          </div>
        </div>
      </Card>

      <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
      `}</style>
    </div>
  )
}
