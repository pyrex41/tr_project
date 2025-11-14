import { Elm } from './Main.elm'

// Use relative URL for production (same domain as frontend), localhost for dev
const isProduction = import.meta.env.PROD
const apiBaseUrl = isProduction
  ? ''  // Empty string = relative URLs to same domain
  : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')

const app = Elm.Main.init({
  node: document.getElementById('app'),
  flags: {
    apiBaseUrl: apiBaseUrl
  }
})
