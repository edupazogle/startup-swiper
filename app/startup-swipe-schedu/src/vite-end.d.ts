/// <reference types="vite/client" />
declare const GITHUB_RUNTIME_PERMANENT_NAME: string

// Note: BASE_KV_SERVICE_URL removed - API is used instead of KV service
// All state management uses custom useKV hook with localStorage or API calls