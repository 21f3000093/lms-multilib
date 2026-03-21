import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './registerServiceWorker'
import './styles/theme.css'
import { initTheme } from './utils/theme'

initTheme()
createApp(App).use(router).mount('#app')
