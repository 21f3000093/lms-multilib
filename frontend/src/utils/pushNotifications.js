import API from '../api'

const getServiceWorkerUrl = () => {
  const base = process.env.BASE_URL || '/'
  const normalizedBase = base.endsWith('/') ? base : `${base}/`
  return `${normalizedBase}service-worker.js`
}

const urlBase64ToUint8Array = (base64String) => {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; i += 1) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

const getOrRegisterServiceWorker = async () => {
  if (!('serviceWorker' in navigator)) {
    return null
  }

  try {
    const existingRegistration = await navigator.serviceWorker.getRegistration()
    if (existingRegistration) {
      return existingRegistration
    }

    const swUrl = getServiceWorkerUrl()
    const registration = await navigator.serviceWorker.register(swUrl)
    await navigator.serviceWorker.ready
    return registration
  } catch (error) {
    try {
      // Fallback for local/dev where Vue PWA service-worker.js may not be generated.
      const fallbackRegistration = await navigator.serviceWorker.register('/sw-push.js')
      await navigator.serviceWorker.ready
      return fallbackRegistration
    } catch (fallbackError) {
      return null
    }
  }
}

const getPushConfig = async () => {
  const res = await API.get('/notifications/push/config')
  return res.data
}

export const setupPushForCurrentAdmin = async () => {
  const role = localStorage.getItem('role')
  if (role !== 'admin') {
    return false
  }

  if (!('serviceWorker' in navigator) || !('PushManager' in window) || !('Notification' in window)) {
    return false
  }

  try {
    const pushConfig = await getPushConfig()
    if (!pushConfig?.enabled || !pushConfig?.vapid_public_key) {
      return false
    }

    const registration = await getOrRegisterServiceWorker()
    if (!registration || !registration.pushManager) {
      return false
    }

    let subscription = await registration.pushManager.getSubscription()
    if (!subscription) {
      const permission = Notification.permission === 'granted'
        ? 'granted'
        : await Notification.requestPermission()

      if (permission !== 'granted') {
        return false
      }

      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(pushConfig.vapid_public_key),
      })
    }

    await API.post('/notifications/push/subscriptions', subscription.toJSON())
    return true
  } catch (error) {
    return false
  }
}

export const unsubscribeCurrentBrowserPush = async () => {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    return
  }

  try {
    const registration = await navigator.serviceWorker.getRegistration()
    if (!registration || !registration.pushManager) {
      return
    }

    const subscription = await registration.pushManager.getSubscription()
    if (!subscription) {
      return
    }

    await API.post('/notifications/push/subscriptions/unsubscribe', {
      endpoint: subscription.endpoint,
    })
    await subscription.unsubscribe()
  } catch (error) {
    // best-effort cleanup only
  }
}
