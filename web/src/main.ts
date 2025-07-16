import naive from 'naive-ui'
import { createApp } from 'vue'
import App from './App.vue'

let app = createApp(App);
app.use(naive)
app.mount('#app')
