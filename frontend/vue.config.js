const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,

  chainWebpack: (config) => {
    config.plugin('define').tap((definitions) => {
      Object.assign(definitions[0], {
        __VUE_OPTIONS_API__: 'true',
        __VUE_PROD_DEVTOOLS__: 'false',
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
      })
      return definitions
    })
  },

  // PWA configuration
  pwa: {
    name: 'Smart Library App',
    // Align browser/PWA chrome with the dark enterprise app theme.
    themeColor: '#ffffff',
    msTileColor: '#ffffff',

    // optional: manifest path
    manifestPath: 'manifest.json',

    // manifest.json fields
    manifestOptions: {
      id: '/',

      name: 'Smart Library App',
      
      short_name: 'Smart Library',

      description: 'Smart Library is a multi-library management platform for seat management, fee tracking, reminders, attendance, and analytics.',
      
      theme_color: '#ffffff',

      background_color: '#ffffff',

      display: 'standalone',

      orientation: 'portrait',
      
      scope: '/',
      
      start_url: '/',

      categories: ['business', 'productivity', 'education'],

      lang: 'en',

      dir: 'ltr',

      screenshots: [
        {
          src: '/img/screenshots/dashboard.png',
          sizes: '1080x1920',
          type: 'image/png',
          form_factor: 'narrow'
        },
        {
          src: '/img/screenshots/students.png',
          sizes: '1080x1920',
          type: 'image/png',
          form_factor: 'narrow'
        },
        {
          src: '/img/screenshots/seats.png',
          sizes: '1080x1920',
          type: 'image/png',
          form_factor: 'narrow'
        },
        {
          src: '/img/screenshots/payments.png',
          sizes: '1080x1920',
          type: 'image/png',
          form_factor: 'narrow'
        },
        {
          src: '/img/screenshots/reminders.png',
          sizes: '1080x1920',
          type: 'image/png',
          form_factor: 'narrow'
        }
      ],
      
      icons: [
        {
          purpose: 'maskable',
          sizes: '1024x1024',
          src: 'img/icons/maskable_icon.png',
          type: 'image/png'
        },
        {
          purpose: 'maskable',
          sizes: '48x48',
          src: 'img/icons/maskable_icon_x48.png',
          type: 'image/png'
        },
        {
          purpose: 'maskable',
          sizes: '72x72',
          src: 'img/icons/maskable_icon_x72.png',
          type: 'image/png'
        },
        {
          purpose: 'maskable',
          sizes: '96x96',
          src: 'img/icons/maskable_icon_x96.png',
          type: 'image/png'
        },
        {
          purpose: 'maskable',
          sizes: '128x128',
          src: 'img/icons/maskable_icon_x128.png',
          type: 'image/png'
        },
        {
          purpose: 'any',
          sizes: '192x192',
          src: 'img/icons/maskable_icon_x192.png',
          type: 'image/png'
        },
        {
          purpose: 'maskable',
          sizes: '384x384',
          src: 'img/icons/maskable_icon_x384.png',
          type: 'image/png'
        },
        {
          purpose: 'any',
          sizes: '512x512',
          src: 'img/icons/maskable_icon_x512.png',
          type: 'image/png'
        }
      ]
    },

    workboxPluginMode: 'GenerateSW',
    workboxOptions: {
      skipWaiting: true,
      clientsClaim: true,
      importScripts: ['sw-push.js'],

      // change this version string on important deployments
      cacheId: 'smart-library-v4',

      runtimeCaching: [
        {
          // 🚫 Never cache API calls to Railway backend
          urlPattern: /^https:\/\/api\.smartlibraryapp\.in\/.*/,
          handler: 'NetworkOnly'
        },
        {
          // Cache images for offline use
          urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp|ico)$/,
          handler: 'CacheFirst',
          options: {
            cacheName: 'image-cache-v2',
            expiration: {
              maxEntries: 50,
              maxAgeSeconds: 30 * 24 * 60 * 60 // 30 days
            }
          }
        },
        {
          // Cache JS and CSS with stale‑while‑revalidate
          urlPattern: /\.(?:js|css)$/,
          handler: 'StaleWhileRevalidate',
          options: {
            cacheName: 'static-resources-v2'
          }
        }
      ]
    }
  }
})
