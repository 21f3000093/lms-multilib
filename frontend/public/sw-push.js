const DEFAULT_NOTIFICATION_URL = '/notifications'

self.addEventListener('push', (event) => {
  let payload = {}
  if (event.data) {
    try {
      payload = event.data.json()
    } catch (error) {
      payload = { body: event.data.text() }
    }
  }

  const title = payload.title || 'Smart Library App'
  const body = payload.body || payload.message || 'You have a new update.'
  const url = typeof payload.url === 'string' && payload.url.trim()
    ? payload.url.trim()
    : DEFAULT_NOTIFICATION_URL

  const options = {
    body,
    icon: '/img/icons/maskable_icon_x192.png',
    badge: '/img/icons/maskable_icon_x192.png',
    data: {
      url,
    },
  }

  event.waitUntil(self.registration.showNotification(title, options))
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  const targetUrl = event.notification?.data?.url || DEFAULT_NOTIFICATION_URL
  const absoluteTarget = new URL(targetUrl, self.location.origin).href

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url === absoluteTarget && 'focus' in client) {
          return client.focus()
        }
      }

      if (self.clients.openWindow) {
        return self.clients.openWindow(absoluteTarget)
      }
      return null
    })
  )
})
