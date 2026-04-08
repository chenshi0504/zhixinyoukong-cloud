<template>
  <div>
    <div style="margin-bottom:16px">
      <h3 style="margin:0">学生管理</h3>
      <div style="margin-top:6px;color:#666;font-size:13px">仅显示当前教师所管理班级内的学生</div>
    </div>
    <el-table :data="students" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="real_name" label="姓名" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="180">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleString('zh-CN') }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/client'

const students = ref([])
const loading = ref(false)

async function fetchStudents() {
  loading.value = true
  try {
    let all = [], page = 1
    while (true) {
      const { data } = await api.get('/api/cloud/users', { params: { role: 'student', page, page_size: 50 } })
      const items = data.items || data
      all = all.concat(items)
      if (!data.pages || page >= data.pages) break
      page++
    }
    students.value = all
  } catch { /* ignore */ } finally { loading.value = false }
}

onMounted(fetchStudents)
</script>
