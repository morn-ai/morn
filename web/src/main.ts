import naive from 'naive-ui'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import i18n from './i18n'

let app = createApp(App);
app.use(naive)
app.use(router)
app.use(i18n)
app.mount('#app')
