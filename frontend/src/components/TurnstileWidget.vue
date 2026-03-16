<template>
  <div v-if="siteKey" class="turnstile-shell">
    <div ref="widgetRef" class="turnstile-host"></div>
    <p v-if="hint" class="turnstile-hint">{{ hint }}</p>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'

const props = defineProps({
  siteKey: {
    type: String,
    default: '',
  },
  hint: {
    type: String,
    default: 'Complete the verification challenge to continue.',
  },
  resetKey: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['verified', 'expired'])
const widgetRef = ref(null)
let widgetId = null
let scriptPromise = null

const loadScript = () => {
  if (window.turnstile) {
    return Promise.resolve(window.turnstile)
  }
  if (scriptPromise) {
    return scriptPromise
  }

  scriptPromise = new Promise((resolve, reject) => {
    const existing = document.querySelector('script[data-turnstile-script="true"]')
    if (existing) {
      existing.addEventListener('load', () => resolve(window.turnstile))
      existing.addEventListener('error', reject)
      return
    }

    const script = document.createElement('script')
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'
    script.async = true
    script.defer = true
    script.dataset.turnstileScript = 'true'
    script.onload = () => resolve(window.turnstile)
    script.onerror = reject
    document.head.appendChild(script)
  })

  return scriptPromise
}

const renderWidget = async () => {
  if (!props.siteKey || !widgetRef.value) {
    return
  }

  const turnstile = await loadScript()
  await nextTick()

  if (widgetId !== null && turnstile?.remove) {
    turnstile.remove(widgetId)
    widgetId = null
  }
  widgetRef.value.innerHTML = ''

  widgetId = turnstile.render(widgetRef.value, {
    sitekey: props.siteKey,
    theme: 'dark',
    callback: (token) => emit('verified', token),
    'expired-callback': () => emit('expired'),
    'error-callback': () => emit('expired'),
  })
}

onMounted(() => {
  renderWidget()
})

watch(() => props.siteKey, () => {
  renderWidget()
})

watch(() => props.resetKey, () => {
  emit('expired')
  renderWidget()
})
</script>

<style scoped>
.turnstile-shell {
  display: grid;
  gap: 0.5rem;
  justify-items: center;
}

.turnstile-hint {
  margin: 0;
  font-size: 0.82rem;
  color: #94a3b8;
  text-align: center;
}
</style>
