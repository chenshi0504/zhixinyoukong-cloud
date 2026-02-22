<template>
  <div>
    <h3 style="margin-bottom:20px">概览</h3>
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/client'

const cards = ref([
  { label: '总机构数', value: '-' },
  { label: '总 License 数', value: '-' },
  { label: '活跃 License', value: '-' },
  { label: '待批阅报告', value: '-' },
])

onMounted(async () => {
  try {
    const { data } = await api.get('/api/cloud/admin/dashboard')
    cards.value = [
      { label: '总机构数', value: data.total_organizations },
      { label: '总 License 数', value: data.total_licenses },
      { label: '活跃 License', value: data.active_licenses },
      { label: '待批阅报告', value: data.pending_reports },
    ]
  } catch { /* ignore */ }
})
</script>

<style scoped>
.stat-card { text-align: center; padding: 10px 0; }
.stat-value { font-size: 32px; font-weight: 700; color: #409eff; }
.stat-label { font-size: 14px; color: #909399; margin-top: 8px; }
</style>
