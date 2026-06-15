import { createRouter, createWebHistory } from 'vue-router'
import HomeMapView from '@/views/HomeMapView.vue'
import SchoolLibraryView from '@/views/SchoolLibraryView.vue'
import ScoreQueryView from '@/views/ScoreQueryView.vue'
import VolunteerView from '@/views/VolunteerView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'HomeMap',
      component: HomeMapView,
    },
    {
      path: '/schools',
      name: 'SchoolLibrary',
      component: SchoolLibraryView,
    },
    {
      path: '/scores',
      name: 'ScoreQuery',
      component: ScoreQueryView,
    },
    {
      path: '/volunteer',
      name: 'VolunteerAssistant',
      component: VolunteerView,
    },
  ],
})

export default router
