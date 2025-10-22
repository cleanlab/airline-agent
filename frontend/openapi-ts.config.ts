import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
  client: '@hey-api/client-axios',
  input: 'http://localhost:8000/api/openapi.json',
  output: {
    format: 'prettier',
    lint: 'eslint',
    path: 'client'
  },
  services: {
    filter: '^(?!\\w+ /api/health)'
  },
  plugins: ['@tanstack/react-query']
})
