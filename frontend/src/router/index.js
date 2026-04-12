import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true },
  },
  // 管理员模块
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
      { path: 'analytics', name: 'Analytics', component: () => import('@/views/Analytics/AnalyticsView.vue') },
      { path: 'updates', name: 'Updates', component: () => import('@/views/Updates/UpdateList.vue') },
    ],
  },
  // 教师模块
  {
    path: '/teacher',
    component: () => import('@/layouts/TeacherLayout.vue'),
    children: [
      { path: '', redirect: '/teacher/classes' },
      { path: 'classes', name: 'TeacherClasses', component: () => import('@/views/Teacher/TeacherClasses.vue') },
      { path: 'students', name: 'TeacherStudents', component: () => import('@/views/Teacher/TeacherStudents.vue') },
      { path: 'tasks', name: 'TeacherTasks', component: () => import('@/views/Teacher/TeacherTasks.vue') },
      { path: 'reports', name: 'TeacherReports', component: () => import('@/views/Teacher/TeacherReports.vue') },
      { path: 'analytics', name: 'TeacherAnalytics', component: () => import('@/views/Teacher/TeacherAnalytics.vue') },
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
