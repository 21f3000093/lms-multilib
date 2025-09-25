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

  // ✅ Full PWA configuration
  pwa: {
    // high-level settings
    name: 'Smart Library App',
    themeColor: '#3f51b5',
    msTileColor: '#ffffff',

    // optional: if you want the manifest to be /manifest.json instead of /manifest.webmanifest
    manifestPath: 'manifest.json',

    // 👇 all the fields from your manifest.json go here
    manifestOptions: {
      name: 'Smart Library App',
      short_name: 'Smart Library',
      theme_color: '#3f51b5',
      background_color: '#ffffff',
      display: 'standalone',
      scope: './',
      start_url: './',
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
          purpose: 'maskable',
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
          purpose: 'maskable',
          sizes: '512x512',
          src: 'img/icons/maskable_icon_x512.png',
          type: 'image/png'
        }
      ]
    },

    workboxPluginMode: 'GenerateSW',
    workboxOptions: {
      skipWaiting: true,
      clientsClaim: true
    }
  }
})
