<template>
  <el-container class="admin-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">智信优控</div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#1d1e2c"
        text-color="#a0a4b8"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>概览</span>
        </el-menu-item>
        <el-menu-item index="/orgs" v-if="isSuperAdmin">
          <el-icon><OfficeBuilding /></el-icon>
          <span>机构管理</span>
        </el-menu-item>
        <el-menu-item index="/licenses" v-if="isSuperAdmin">
          <el-icon><Key /></el-icon>
          <span>License 管理</span>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><Document /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="/reports">
          <el-icon><Files /></el-icon>
          <span>报告管理</span>
        </el-menu-item>
        <el-menu-item index="/analytics" v-if="isSuperAdmin">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计分析</span>
        </el-menu-item>
        <el-menu-item index="/updates" v-if="isSuperAdmin">
          <el-icon><Upload /></el-icon>
          <span>版本更新</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="topbar">
        <span></span>
        <div class="user-info">
          <span>{{ auth.user?.real_name || auth.user?.username }}</span>
          <el-tag size="small" type="info" style="margin-left:8px">{{ roleLabel }}</el-tag>
          <el-button text type="danger" style="margin-left:12px" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const activeMenu = computed(() => '/' + route.path.split('/')[1])
const isSuperAdmin = computed(() => auth.userRole === 'super_admin')

const roleMap = { super_admin: '超级管理员', org_admin: '机构管理员', teacher: '教师', student: '学生' }
const roleLabel = computed(() => roleMap[auth.userRole] || auth.userRole)

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout { height: 100vh; }
.sidebar { background: #1d1e2c; overflow-y: auto; }
.logo {
  height: 60px; display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 18px; font-weight: 600; letter-spacing: 2px;
}
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #e4e7ed; background: #fff;
}
.user-info { display: flex; align-items: center; }
</style>
