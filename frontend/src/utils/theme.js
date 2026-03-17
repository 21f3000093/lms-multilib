import { computed, reactive, readonly } from 'vue'

export const THEME_STORAGE_KEY = 'smart-library-theme'
const DEFAULT_THEME = 'dark'

const state = reactive({
  current: DEFAULT_THEME,
  initialized: false,
})

let storageListenerAttached = false

function normalizeTheme(value) {
  return value === 'light' ? 'light' : DEFAULT_THEME
}

function applyTheme(theme, { persist = true } = {}) {
  const nextTheme = normalizeTheme(theme)
  state.current = nextTheme

  if (typeof document !== 'undefined') {
    const root = document.documentElement
    root.setAttribute('data-theme', nextTheme)
    root.style.colorScheme = nextTheme
  }

  if (persist && typeof window !== 'undefined') {
    window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme)
  }

  return nextTheme
}

export function initTheme() {
  if (typeof window === 'undefined') {
    state.initialized = true
    return state.current
  }

  if (!storageListenerAttached) {
    window.addEventListener('storage', (event) => {
      if (event.key !== THEME_STORAGE_KEY) {
        return
      }
      applyTheme(event.newValue, { persist: false })
    })
    storageListenerAttached = true
  }

  const savedTheme = normalizeTheme(window.localStorage.getItem(THEME_STORAGE_KEY))
  state.initialized = true
  return applyTheme(savedTheme, { persist: false })
}

export function setTheme(theme) {
  return applyTheme(theme)
}

export function toggleTheme() {
  return applyTheme(state.current === 'dark' ? 'light' : 'dark')
}

export const themeState = readonly(state)

export function useTheme() {
  if (!state.initialized) {
    initTheme()
  }

  const currentTheme = computed(() => state.current)
  const isDarkTheme = computed(() => state.current === 'dark')
  const nextTheme = computed(() => (state.current === 'dark' ? 'light' : 'dark'))
  const nextThemeLabel = computed(() => (state.current === 'dark' ? 'Light theme' : 'Dark theme'))

  return {
    themeState,
    currentTheme,
    isDarkTheme,
    nextTheme,
    nextThemeLabel,
    setTheme,
    toggleTheme,
  }
}
