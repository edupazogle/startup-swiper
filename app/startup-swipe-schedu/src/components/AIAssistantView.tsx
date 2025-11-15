import { StartupChat } from './StartupChat'

export function AIAssistantView() {
  return (
    <div className="h-full flex items-center justify-center p-4">
      <div className="w-full max-w-4xl h-[calc(100vh-12rem)] bg-white/5 backdrop-blur-sm rounded-md border border-white/10 overflow-hidden">
        <StartupChat />
      </div>
    </div>
  )
}
