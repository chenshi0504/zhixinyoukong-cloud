<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h3 style="margin:0">教学任务管理</h3>
      <div style="display:flex;gap:12px;align-items:center">
        <el-button circle plain :loading="refreshing" title="刷新最新任务数据" @click="refreshTaskData">
          <el-icon><Refresh /></el-icon>
        </el-button>
        <el-button type="primary" @click="openCreate">发布任务</el-button>
      </div>
    </div>

    <el-table :data="tasks" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="任务标题" />
      <el-table-column label="分发班级" width="140">
        <template #default="{ row }">{{ classMap[row.class_id] || row.class_name || '未指定' }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'published' ? 'success' : 'info'" size="small">
            {{ row.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="deadline" label="截止时间" width="180">
        <template #default="{ row }">{{ row.deadline ? new Date(row.deadline).toLocaleString('zh-CN') : '-' }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleString('zh-CN') }}</template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button v-if="row.status==='draft'" size="small" type="success" @click="publishTask(row)">发布</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建任务对话框 -->
    <el-dialog v-model="showCreate" title="发布新任务" width="520px">
      <el-form :model="newTask" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="newTask.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="分发班级">
          <el-select v-model="newTask.class_id" placeholder="选择班级" style="width:100%">
            <el-option v-for="c in classList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newTask.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="满分">
          <el-input-number v-model="newTask.max_score" :min="1" :max="200" />
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker v-model="newTask.deadline" type="datetime" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="createTask" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/api/client'
import { ElMessage } from 'element-plus'

const tasks = ref([])
const loading = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const refreshing = ref(false)
const classList = ref([])
const newTask = reactive({ title: '', description: '', class_id: null, max_score: 100, deadline: null })

const classMap = computed(() => {
  const m = {}
  classList.value.forEach(c => { m[c.id] = c.name })
  return m
})

async function fetchTasks() {
  loading.value = true
  try {
    const { data } = await api.get('/api/cloud/tasks', { params: { page_size: 50 } })
    tasks.value = data.items || data
    return true
  } catch {
    return false
  } finally { loading.value = false }
}

async function fetchClasses() {
  try {
    const { data } = await api.get('/api/cloud/classes', { params: { page_size: 50 } })
    classList.value = data.items || data
    return true
  } catch {
    return false
  }
}

async function refreshTaskData() {
  refreshing.value = true
  try {
    const results = await Promise.all([fetchTasks(), fetchClasses()])
    if (results.every(Boolean)) ElMessage.success('已刷新最新任务数据')
    else ElMessage.warning('任务列表已刷新，部分数据获取失败')
  } finally { refreshing.value = false }
}

function openCreate() {
  Object.assign(newTask, { title: '', description: '', class_id: null, max_score: 100, deadline: null })
  showCreate.value = true
}

async function createTask() {
  if (!newTask.title.trim()) { ElMessage.warning('请输入任务标题'); return }
  if (!newTask.class_id) { ElMessage.warning('请选择分发班级'); return }
  creating.value = true
  try {
    await api.post('/api/cloud/tasks', newTask)
    ElMessage.success('任务创建成功')
    showCreate.value = false
    fetchTasks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  } finally { creating.value = false }
}

async function publishTask(row) {
  try {
    await api.post(`/api/cloud/tasks/${row.id}/publish`)
    ElMessage.success('任务已发布')
    fetchTasks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '发布失败')
  }
}

onMounted(() => { fetchTasks(); fetchClasses() })
</script>
