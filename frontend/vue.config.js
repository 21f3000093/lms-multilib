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
    themeColor: '#0f172a',
    msTileColor: '#0f172a',

    // optional: manifest path
    manifestPath: 'manifest.json',

    // manifest.json fields
    manifestOptions: {
      name: 'Smart Library App',
      short_name: 'Smart Library',
      theme_color: '#0f172a',
      background_color: '#0b1222',
      display: 'standalone',
      scope: './',
      start_url: './login',
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
          urlPattern: /^https:\/\/lms-multilib-production\.up\.railway\.app\/.*/,
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
