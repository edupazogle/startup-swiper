/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_ENV: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// GitHub Spark API types
interface SparkUser {
  id: string | number
  login?: string
  name?: string
}

interface SparkAPI {
  user: () => Promise<SparkUser>
  [key: string]: any
}

declare global {
  interface Window {
    spark?: SparkAPI
  }
}

export {}
