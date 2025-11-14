import { Elm } from './Main.elm'

const app = Elm.Main.init({
  node: document.getElementById('app'),
  flags: {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  }
})
