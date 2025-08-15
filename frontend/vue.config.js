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

    // 🔑 WebSocket settings for VS Code tunnel
  // devServer: {
  //   port: 8080,
  //   host: '0.0.0.0',        // allow external access
  //   allowedHosts: 'all',    // accept tunnel hostnames
  //   // https: true,            // serve the app over HTTPS
  //   client: {
  //     webSocketURL: {
  //       protocol: 'wss',          // secure WebSocket
  //       hostname: process.env.WDS_SOCKET_HOST || '0.0.0.0',
  //       port: process.env.WDS_SOCKET_PORT || 0,
  //       pathname: '/ws'
  //     }
  //   }
  // },

  // ✅ Add this block for PWA
  pwa: {
    name: 'Smart Library App',
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
