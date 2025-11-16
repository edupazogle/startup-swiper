import { StartupChat } from './StartupChat'

export function AIAssistantView() {
  return (
    <div className="h-full w-full flex items-stretch justify-center">
      <div className="w-full max-w-5xl h-full flex">
        <StartupChat />
      </div>
    </div>
  )
}
