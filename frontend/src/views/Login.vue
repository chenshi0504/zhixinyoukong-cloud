<template>
  <div class="login-page">
    <div class="login-container">
      <h1 class="main-title">智信优控 · 云端管理平台</h1>
      <p class="sub-title">智能交通 · 云端协同 · 高效管理</p>

      <!-- 步骤1：选择角色 -->
      <div v-if="mode === 'select'" class="login-card role-card-wrap">
        <div class="card-header"><h2>选择登录身份</h2></div>
        <div class="role-cards">
          <div class="role-card" @click="mode = 'login'; selectedRole = 'admin'">
            <div class="role-icon">🛡️</div>
            <h3 class="role-label">管理员</h3>
            <p class="role-desc">平台管理与运维</p>
          </div>
          <div class="role-card" @click="enterTeacherLogin">
            <div class="role-icon">🎓</div>
            <h3 class="role-label">教师</h3>
            <p class="role-desc">教学任务与报告</p>
          </div>
        </div>
      </div>

      <!-- 步骤2：登录表单 -->
      <div v-else-if="mode === 'login'" class="login-card">
        <div class="card-header">
          <h2>{{ selectedRole === 'admin' ? '管理员登录' : '教师登录（按机构）' }}</h2>
        </div>
        <form @submit.prevent="handleLogin">
          <div v-if="selectedRole === 'teacher'" class="form-group">
            <div class="input-container" :class="{ error: shakeInputs && !teacherOrgId }">
              <span class="input-icon">🏫</span>
              <select v-model="teacherOrgId">
                <option value="">请选择所属学校/机构</option>
                <option v-for="org in orgList" :key="org.id" :value="String(org.id)">{{ org.name }}</option>
              </select>
            </div>
            <div class="field-note">请选择教师所属学校/机构后再登录</div>
          </div>
          <div class="form-group">
            <div class="input-container" :class="{ error: shakeInputs }">
              <span class="input-icon">👤</span>
              <input v-model="form.username" type="text" placeholder="请输入用户名" required />
            </div>
          </div>
          <div class="form-group">
            <div class="input-container" :class="{ error: shakeInputs }">
              <span class="input-icon">🔒</span>
              <input v-model="form.password" type="password" placeholder="请输入密码" required
                @keyup.enter="handleLogin" />
            </div>
          </div>
          <button type="submit" class="login-button" :disabled="loading">
            {{ loading ? '登录中...' : '登录系统' }}
          </button>
        </form>
        <div class="link-row">
          <span class="back-link" @click="backToRoleSelect">← 重新选择</span>
          <span v-if="selectedRole === 'teacher'" class="register-link" @click="openTeacherRegister">教师注册 →</span>
        </div>
        <div class="status-bar">
          <span class="status-dot" :class="statusType"></span>
          <span class="status-text" :class="statusType">{{ statusMsg }}</span>
        </div>
      </div>

      <!-- 教师注册表单 -->
      <div v-else-if="mode === 'register'" class="login-card">
        <div class="card-header"><h2>教师注册（所属机构）</h2></div>
        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <div class="input-container">
              <span class="input-icon">👤</span>
              <input v-model="regForm.real_name" type="text" placeholder="请输入姓名" required />
            </div>
          </div>
          <div class="form-group">
            <div v-if="!teacherNewOrgMode" class="input-container">
              <span class="input-icon">🏢</span>
              <select v-model="teacherOrgId">
                <option value="">请选择所属学校/机构</option>
                <option v-for="org in orgList" :key="org.id" :value="String(org.id)">{{ org.name }}</option>
              </select>
            </div>
            <div v-else class="input-container">
              <span class="input-icon">🏢</span>
              <input v-model="regForm.org_name" type="text" placeholder="请输入学校/机构名称" required />
            </div>
            <div class="field-note">
              <span class="back-link" @click="teacherNewOrgMode = !teacherNewOrgMode">
                {{ teacherNewOrgMode ? '← 选择已有机构' : '没有我的机构？手动填写' }}
              </span>
            </div>
          </div>
          <div class="form-group">
            <div class="input-container">
              <span class="input-icon">🔒</span>
              <input v-model="regForm.password" type="password" placeholder="设置密码（至少6位）" required />
            </div>
          </div>
          <div class="form-group">
            <div class="input-container">
              <span class="input-icon">🔒</span>
              <input v-model="regForm.confirmPassword" type="password" placeholder="确认密码" required />
            </div>
          </div>
          <button type="submit" class="login-button" :disabled="regLoading">
            {{ regLoading ? '注册中...' : '提交注册' }}
          </button>
        </form>
        <div class="link-row">
          <span class="back-link" @click="mode = 'login'; selectedRole = 'teacher'; teacherNewOrgMode = false">← 返回登录</span>
        </div>
        <div class="status-bar">
          <span class="status-dot" :class="statusType"></span>
          <span class="status-text" :class="statusType">{{ statusMsg }}</span>
        </div>
      </div>

      <!-- 注册成功 -->
      <div v-else-if="mode === 'register-success'" class="login-card">
        <div class="card-header"><h2>注册成功 🎉</h2></div>
        <div class="success-info">
          <p>您的账号已创建，请牢记以下信息：</p>
          <div class="info-box">
            <div class="info-row"><span class="info-label">账号：</span><span class="info-value">{{ regResult.username }}</span></div>
            <div class="info-row"><span class="info-label">姓名：</span><span class="info-value">{{ regResult.real_name }}</span></div>
            <div class="info-row"><span class="info-label">机构：</span><span class="info-value">{{ regResult.org_name }}</span></div>
          </div>
        </div>
        <button class="login-button" @click="useRegisteredAccount">
          前往登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const regLoading = ref(false)
const mode = ref('select') // select | login | register | register-success
const selectedRole = ref('')
const shakeInputs = ref(false)
const statusMsg = ref('')
const statusType = ref('')
const regResult = ref({})
const orgList = ref([])
const teacherOrgId = ref('')
const teacherNewOrgMode = ref(false)

const form = reactive({ username: '', password: '' })
const regForm = reactive({ real_name: '', org_name: '', password: '', confirmPassword: '' })

onMounted(async () => {
  try {
    const { data } = await api.get('/api/cloud/public/orgs')
    orgList.value = data || []
  } catch {
    orgList.value = []
  }
  try {
    await api.get('/api/cloud/health')
    statusMsg.value = '后端服务已连接'
    statusType.value = 'ok'
  } catch {
    statusMsg.value = '后端服务未连接'
    statusType.value = 'err'
  }
})

function enterTeacherLogin() {
  selectedRole.value = 'teacher'
  mode.value = 'login'
  teacherNewOrgMode.value = false
}

function backToRoleSelect() {
  mode.value = 'select'
  selectedRole.value = ''
  teacherNewOrgMode.value = false
}

function openTeacherRegister() {
  mode.value = 'register'
  teacherNewOrgMode.value = false
}

async function handleLogin() {
  if (!form.username || !form.password) {
    triggerShake(); statusMsg.value = '请输入用户名和密码'; statusType.value = 'err'; return
  }
  if (selectedRole.value === 'teacher' && !teacherOrgId.value) {
    triggerShake(); statusMsg.value = '请先选择所属学校/机构'; statusType.value = 'err'; return
  }
  loading.value = true; statusMsg.value = '登录中...'; statusType.value = ''
  try {
    const data = await auth.login(
      form.username,
      form.password,
      selectedRole.value === 'teacher' ? Number(teacherOrgId.value) : null,
    )
    const role = data.user.role
    if (selectedRole.value === 'teacher' && role !== 'teacher') {
      statusMsg.value = '该账号不是教师角色'; statusType.value = 'err'; auth.clearAuth(); loading.value = false; return
    }
    if (selectedRole.value === 'admin' && role === 'teacher') {
      statusMsg.value = '该账号是教师角色，请选择教师身份登录'; statusType.value = 'err'; auth.clearAuth(); loading.value = false; return
    }
    localStorage.setItem('login_mode', selectedRole.value)
    statusMsg.value = '登录成功！正在跳转...'; statusType.value = 'ok'
    setTimeout(() => {
      router.push(selectedRole.value === 'teacher' ? '/teacher/classes' : '/dashboard')
    }, 500)
  } catch (e) {
    statusMsg.value = e.response?.data?.detail || '用户名或密码错误'; statusType.value = 'err'; triggerShake()
  } finally { loading.value = false }
}

async function handleRegister() {
  if (!regForm.real_name || !regForm.password) {
    statusMsg.value = '请填写所有字段'; statusType.value = 'err'; return
  }
  if (!teacherNewOrgMode.value && !teacherOrgId.value) {
    statusMsg.value = '请选择所属学校/机构'; statusType.value = 'err'; return
  }
  if (teacherNewOrgMode.value && !regForm.org_name.trim()) {
    statusMsg.value = '请输入学校/机构名称'; statusType.value = 'err'; return
  }
  if (regForm.password.length < 6) {
    statusMsg.value = '密码长度不能少于6位'; statusType.value = 'err'; return
  }
  if (regForm.password !== regForm.confirmPassword) {
    statusMsg.value = '两次密码输入不一致'; statusType.value = 'err'; return
  }
  regLoading.value = true; statusMsg.value = '注册中...'; statusType.value = ''
  try {
    const { data } = await api.post('/api/cloud/auth/register', {
      real_name: regForm.real_name,
      org_id: teacherNewOrgMode.value ? null : Number(teacherOrgId.value),
      org_name: teacherNewOrgMode.value ? regForm.org_name.trim() : null,
      password: regForm.password,
    })
    regResult.value = data
    teacherOrgId.value = data.org_id ? String(data.org_id) : teacherOrgId.value
    teacherNewOrgMode.value = false
    mode.value = 'register-success'
    statusMsg.value = ''; statusType.value = ''
  } catch (e) {
    statusMsg.value = e.response?.data?.detail || '注册失败'; statusType.value = 'err'
  } finally { regLoading.value = false }
}

function useRegisteredAccount() {
  mode.value = 'login'
  selectedRole.value = 'teacher'
  form.username = regResult.value.username || form.username
  form.password = ''
  if (regResult.value.org_id) {
    teacherOrgId.value = String(regResult.value.org_id)
  }
}

function triggerShake() {
  shakeInputs.value = true; setTimeout(() => { shakeInputs.value = false }, 500)
}
</script>

<style scoped>
.login-page {
  width: 100vw; height: 100vh;
  background-image: url('/bg.jpg');
  background-size: cover; background-position: center;
  position: relative;
  font-family: 'Microsoft YaHei', 'Source Han Sans CN', sans-serif;
}
.login-page::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(135deg, rgba(44,90,160,0.8), rgba(0,0,0,0.6));
  z-index: 1;
}
.login-container {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  text-align: center; padding: 20px;
}
.main-title {
  font-size: 36px; font-weight: 700; color: #fff;
  text-shadow: 0 0 20px rgba(255,255,255,0.5), 0 4px 8px rgba(0,0,0,0.3);
  margin-bottom: 15px; animation: slideDown 0.8s ease-out;
}
.sub-title {
  font-size: 16px; color: rgba(255,255,255,0.9); margin-bottom: 50px;
  animation: slideDown 0.8s ease-out 0.2s both;
}
.login-card {
  background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); border-radius: 16px;
  padding: 50px; width: 100%; max-width: 480px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1); animation: slideUp 0.8s ease-out 0.4s both;
}
.role-card-wrap { max-width: 560px; }
.card-header h2 { font-size: 24px; color: #2C5AA0; text-align: center; margin-bottom: 30px; }
.role-cards { display: flex; gap: 24px; justify-content: center; }
.role-card {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  padding: 32px 20px; background: #f8f9fa; border: 2px solid transparent;
  border-radius: 12px; cursor: pointer; transition: all 0.3s ease;
}
.role-card:hover {
  border-color: #2C5AA0; transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(44,90,160,0.15);
}
.role-icon { font-size: 48px; margin-bottom: 12px; }
.role-label { font-size: 18px; font-weight: 600; color: #2C5AA0; margin-bottom: 8px; }
.role-desc { font-size: 13px; color: #666; }
.form-group { margin-bottom: 20px; }
.input-container {
  display: flex; align-items: center; background: #f8f9fa;
  border: 2px solid transparent; border-radius: 12px; height: 50px;
  transition: all 0.3s ease;
}
.input-container:focus-within { border-color: #2C5AA0; box-shadow: 0 0 0 3px rgba(44,90,160,0.1); }
.input-icon { padding: 0 15px; font-size: 20px; color: #666; }
.input-container:focus-within .input-icon { color: #2C5AA0; }
.input-container input {
  flex: 1; height: 100%; padding: 0 15px; border: none; background: transparent;
  font-size: 14px; outline: none; font-family: inherit;
}
.input-container select {
  flex: 1; height: 100%; padding: 0 15px; border: none; background: transparent;
  font-size: 14px; outline: none; font-family: inherit; color: #333; appearance: none;
}
.input-container input::placeholder { color: #999; }
.input-container.error { border-color: #dc3545; animation: shake 0.5s ease-in-out; }
.field-note { margin-top: 8px; font-size: 12px; color: #666; text-align: left; }
.login-button {
  width: 100%; height: 50px;
  background: linear-gradient(135deg, #2C5AA0, #4A90E2);
  color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 600;
  cursor: pointer; margin-top: 10px; transition: all 0.3s ease;
}
.login-button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(44,90,160,0.4); }
.login-button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
.link-row {
  display: flex; justify-content: space-between; margin-top: 20px;
}
.back-link, .register-link {
  color: #2C5AA0; cursor: pointer; font-size: 14px; transition: opacity 0.3s;
}
.back-link:hover, .register-link:hover { opacity: 0.7; }
.status-bar { margin-top: 16px; text-align: center; font-size: 13px; }
.status-dot {
  display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  background: #ccc; margin-right: 6px; vertical-align: middle;
}
.status-dot.ok { background: #28a745; }
.status-dot.err { background: #dc3545; }
.status-text { color: #999; }
.status-text.ok { color: #28a745; }
.status-text.err { color: #dc3545; }
.success-info { text-align: left; margin-bottom: 24px; }
.success-info p { color: #666; margin-bottom: 16px; text-align: center; }
.info-box {
  background: #f0f5ff; border: 1px solid #d0e0ff; border-radius: 8px; padding: 16px;
}
.info-row { display: flex; padding: 8px 0; border-bottom: 1px solid #e8eef5; }
.info-row:last-child { border-bottom: none; }
.info-label { color: #666; width: 60px; flex-shrink: 0; }
.info-value { color: #2C5AA0; font-weight: 600; }
@keyframes slideDown { from { opacity:0; transform:translateY(-50px); } to { opacity:1; transform:translateY(0); } }
@keyframes slideUp { from { opacity:0; transform:translateY(50px); } to { opacity:1; transform:translateY(0); } }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }
@media (max-width:768px) { .main-title{font-size:28px} .login-card{padding:40px 30px;margin:0 15px} }
</style>
