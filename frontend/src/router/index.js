import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/AdminLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'orgs', name: 'Orgs', component: () => import('@/views/Orgs/OrgList.vue') },
      { path: 'orgs/:id', name: 'OrgDetail', component: () => import('@/views/Orgs/OrgDetail.vue') },
      { path: 'licenses', name: 'Licenses', component: () => import('@/views/Licenses/LicenseList.vue') },
      { path: 'users', name: 'Users', component: () => import('@/views/Users/UserList.vue') },
      { path: 'tasks', name: 'Tasks', component: () => import('@/views/Tasks/TaskList.vue') },
      { path: 'reports', name: 'Reports', component: () => import('@/views/Reports/ReportList.vue') },
      { path: 'analytics', name: 'Analytics', component: () => import('@/views/Analytics/AnalyticsView.vue') },
      { path: 'updates', name: 'Updates', component: () => import('@/views/Updates/UpdateList.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')
  if (!to.meta.public && !token) {
    return { name: 'Login' }
  }
})

export default router
