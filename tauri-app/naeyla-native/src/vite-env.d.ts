/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_NAEYLA_TOKEN: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

