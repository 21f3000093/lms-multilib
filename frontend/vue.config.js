const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,

  // ✅ Add this block for PWA
  pwa: {
    name: 'SmartLibrary',
    themeColor: '#3f51b5',
    msTileColor: '#ffffff',
    manifestPath: 'manifest.json',
    manifestOptions: {
      background_color: '#ffffff'
    },
    workboxPluginMode: 'GenerateSW',
    workboxOptions: {
      skipWaiting: true,
      clientsClaim: true
    }
  }
})
