import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { toast } from 'sonner'
import { authService } from '@/lib/authService'
import { AuroralBackground } from '@/components/AuroralBackground'
import { Eye, EyeSlash } from '@phosphor-icons/react'
import logoVC from '@/assets/images/logo_vc.png'
import logoMain from '@/assets/images/f8cba53d-0d66-4aab-b97c-8fa66871fa8b.png'

interface LoginViewProps {
  onLogin: (email: string, name: string) => void
}

export function LoginView({ onLogin }: LoginViewProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      const user = await authService.login(email, password)
      
      // Extract name from user data or email
      const name = user.full_name || email.split('@')[0].split('.').map(part => 
        part.charAt(0).toUpperCase() + part.slice(1)
      ).join(' ')

      toast.success(`Welcome back, ${name}!`)
      onLogin(email, name)
    } catch (error: any) {
      console.error('Login error:', error)
      
      // User-friendly error messages
      if (error.message?.includes('credentials')) {
        setError('Invalid email or password. Please try again.')
      } else if (error.message?.includes('network') || error.message?.includes('fetch')) {
        setError('Unable to connect to server. Please check your connection.')
      } else {
        setError('Login failed. Please try again or contact support.')
      }
      
      toast.error('Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGuestMode = () => {
    // Guest mode with limited functionality
    const guestEmail = `guest_${Date.now()}@slush.local`
    const guestName = 'Guest User'
    
    toast.info('Logged in as guest. Some features may be limited.')
    onLogin(guestEmail, guestName)
  }

  return (
    <>
      <AuroralBackground />
      <div className="min-h-screen flex items-center justify-center p-4">
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
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-white mb-2">
                Email
              </label>
              <Input
                type="email"
                placeholder="your.email@company.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  setError(null)
                }}
                className="bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-white/40 focus:ring-1 focus:ring-white/20"
                required
                disabled={isLoading}
                autoComplete="email"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-white mb-2">
                Password
              </label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    setError(null)
                  }}
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/40 focus:border-white/40 focus:ring-1 focus:ring-white/20 pr-10"
                  required
                  disabled={isLoading}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/60 hover:text-white"
                  disabled={isLoading}
                >
                  {showPassword ? <EyeSlash size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold py-3 touch-manipulation disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isLoading}
              style={{ WebkitTapHighlightColor: 'transparent' }}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Logging in...
                </span>
              ) : (
                'Sign In'
              )}
            </Button>

            {/* Guest Mode */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10"></div>
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-black/50 px-2 text-white/40">Or</span>
              </div>
            </div>

            <Button
              type="button"
              onClick={handleGuestMode}
              variant="outline"
              className="w-full border-white/20 bg-white/5 hover:bg-white/10 text-white font-medium py-3"
              disabled={isLoading}
            >
              Continue as Guest
            </Button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center space-y-2">
            <p className="text-white/60 text-xs">
              Need an account? Contact your administrator
            </p>
            <p className="text-white/40 text-xs">
              AXA Venture Clienting © 2025
            </p>
          </div>
        </div>
      </Card>
      </div>
    </>
  )
}
