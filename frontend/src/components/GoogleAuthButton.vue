<template>
  <div v-if="enabled" class="google-auth-shell">
    <div ref="buttonHost" class="google-button-host"></div>
    <p v-if="hint" class="google-hint">{{ hint }}</p>
  </div>
</template>

<script>
import API from '../api'

const GOOGLE_SCRIPT_SRC = 'https://accounts.google.com/gsi/client'

export default {
  name: 'GoogleAuthButton',
  props: {
    text: {
      type: String,
      default: 'continue_with',
    },
    width: {
      type: Number,
      default: 320,
    },
    hint: {
      type: String,
      default: '',
    },
  },
  emits: ['credential', 'error', 'ready', 'disabled'],
  data() {
    return {
      enabled: false,
      clientId: '',
    }
  },
  async mounted() {
    await this.initialize()
  },
  methods: {
    async initialize() {
      try {
        const res = await API.get('/auth/google/config')
        this.enabled = Boolean(res.data?.enabled && res.data?.client_id)
        this.clientId = res.data?.client_id || ''
        if (!this.enabled) {
          this.$emit('disabled')
          return
        }
        await this.loadScript()
        this.renderButton()
        this.$emit('ready')
      } catch (error) {
        this.enabled = false
        this.$emit('error', error)
      }
    },
    loadScript() {
      if (window.google?.accounts?.id) {
        return Promise.resolve(window.google)
      }
      if (window.__googleIdentityScriptPromise) {
        return window.__googleIdentityScriptPromise
      }

      window.__googleIdentityScriptPromise = new Promise((resolve, reject) => {
        const existing = document.querySelector('script[data-google-identity-script="true"]')
        if (existing) {
          existing.addEventListener('load', () => resolve(window.google))
          existing.addEventListener('error', reject)
          return
        }

        const script = document.createElement('script')
        script.src = GOOGLE_SCRIPT_SRC
        script.async = true
        script.defer = true
        script.dataset.googleIdentityScript = 'true'
        script.onload = () => resolve(window.google)
        script.onerror = reject
        document.head.appendChild(script)
      })

      return window.__googleIdentityScriptPromise
    },
    renderButton() {
      if (!this.enabled || !this.clientId || !this.$refs.buttonHost || !window.google?.accounts?.id) {
        return
      }

      this.$refs.buttonHost.innerHTML = ''
      window.google.accounts.id.initialize({
        client_id: this.clientId,
        callback: (response) => {
          if (response?.credential) {
            this.$emit('credential', response.credential)
            return
          }
          this.$emit('error', new Error('Google sign-in did not return a credential.'))
        },
        auto_select: false,
        cancel_on_tap_outside: false,
      })
      window.google.accounts.id.renderButton(this.$refs.buttonHost, {
        theme: 'outline',
        size: 'large',
        shape: 'pill',
        text: this.text,
        logo_alignment: 'left',
        width: this.width,
      })
    },
  },
}
</script>

<style scoped>
.google-auth-shell {
  display: grid;
  gap: 0.5rem;
  justify-items: center;
}

.google-button-host {
  width: 100%;
  display: flex;
  justify-content: center;
}

.google-hint {
  margin: 0;
  color: #94a3b8;
  font-size: 0.82rem;
  text-align: center;
}
</style>
