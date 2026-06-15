import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import type { Language } from 'element-plus/es/locale'
import en from 'element-plus/es/locale/lang/en'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './styles/global.scss'

const locale: Language = {
  ...en,
  el: {
    ...en.el,
    pagination: {
      ...en.el.pagination,
      pagesize: '',       // "10/page" → "10"
      goto: '跳转至',    // "Go to"  → "跳转至"
      pageClassifier: '', // 去掉输入框后的 "page"
    },
  },
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale })

app.mount('#app')
