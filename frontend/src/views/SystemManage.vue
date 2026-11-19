<template>
  <div class="system-manage">
    <el-tabs v-model="activeTab" class="glass-card tabs-card">
      <el-tab-pane name="classroom">
        <template #label>
          <span class="tab-label">
            <el-icon><School /></el-icon>
            <span>教室管理</span>
          </span>
        </template>
        <div class="tab-toolbar">
          <el-input v-model="cQuery.keyword" placeholder="搜索教室" clearable style="width: 220px" @keyup.enter="loadClassrooms">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <button class="btn-gradient" @click="loadClassrooms">
            <el-icon><Search /></el-icon>
            <span>查询</span>
          </button>
          <button class="btn-gradient btn-add" @click="openClassroomDialog()">
            <el-icon><Plus /></el-icon>
            <span>新增教室</span>
          </button>
        </div>
        <el-table :data="classrooms" stripe :row-class-name="rowClass">
          <el-table-column prop="name" label="名称" width="120">
            <template #default="{ row }">
              <span class="name-cell">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="building" label="楼栋" width="120" />
          <el-table-column prop="floor" label="楼层" width="70" align="center">
            <template #default="{ row }">
              <span class="num-badge">{{ row.floor }}F</span>
            </template>
          </el-table-column>
          <el-table-column prop="capacity" label="容量" width="80" align="center">
            <template #default="{ row }">
              <span class="num-badge">{{ row.capacity }}</span>
            </template>
          </el-table-column>
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <span class="type-tag" :class="row.type?.toLowerCase()">{{ typeText(row.type) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <span class="status-tag" :class="row.status?.toLowerCase()">
                <span class="status-light"></span>
                {{ statusText(row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="equipment" label="设备" min-width="150" />
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <div class="action-row">
                <button class="action-btn edit" @click="openClassroomDialog(row)">
                  <el-icon><Edit /></el-icon>
                  <span>编辑</span>
                </button>
                <button class="action-btn danger" @click="deleteClassroom(row)">
                  <el-icon><Delete /></el-icon>
                  <span>删除</span>
                </button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination">
          <el-pagination v-model:current-page="cQuery.page" v-model:page-size="cQuery.pageSize" :total="cTotal" layout="prev, pager, next" @current-change="loadClassrooms" />
        </div>
      </el-tab-pane>

      <el-tab-pane name="user">
        <template #label>
          <span class="tab-label">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </span>
        </template>
        <div class="tab-toolbar">
          <el-input v-model="uQuery.keyword" placeholder="搜索用户" clearable style="width: 220px" @keyup.enter="loadUsers">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <button class="btn-gradient" @click="loadUsers">
            <el-icon><Search /></el-icon>
            <span>查询</span>
          </button>
          <button class="btn-gradient btn-add" @click="openUserDialog()">
            <el-icon><Plus /></el-icon>
            <span>新增用户</span>
          </button>
        </div>
        <el-table :data="users" stripe :row-class-name="rowClass">
          <el-table-column prop="username" label="用户名" width="120">
            <template #default="{ row }">
              <div class="user-cell">
                <span class="user-avatar" :class="row.role?.toLowerCase()">{{ row.name?.charAt(0) }}</span>
                <span>{{ row.username }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column label="角色" width="100">
            <template #default="{ row }">
              <span class="role-tag" :class="row.role?.toLowerCase()">{{ roleText(row.role) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="department" label="院系" width="120" />
          <el-table-column prop="phone" label="手机" width="130" />
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <span class="status-pill" :class="row.status === 1 ? 'active' : 'inactive'">
                <span class="status-light"></span>
                {{ row.status === 1 ? '启用' : '禁用' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <div class="action-row">
                <button class="action-btn edit" @click="openUserDialog(row)">
                  <el-icon><Edit /></el-icon>
                  <span>编辑</span>
                </button>
                <button class="action-btn danger" @click="deleteUser(row)">
                  <el-icon><Delete /></el-icon>
                  <span>删除</span>
                </button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination">
          <el-pagination v-model:current-page="uQuery.page" v-model:page-size="uQuery.pageSize" :total="uTotal" layout="prev, pager, next" @current-change="loadUsers" />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 教室编辑弹窗 -->
    <el-dialog v-model="cDialog" width="500px" class="custom-dialog">
      <template #header>
        <div class="dialog-header">
          <el-icon class="dialog-icon"><School /></el-icon>
          <div>
            <h3>{{ cForm.id ? '编辑教室' : '新增教室' }}</h3>
            <span>{{ cForm.id ? '修改教室信息' : '填写新教室信息' }}</span>
          </div>
        </div>
      </template>
      <el-form :model="cForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="cForm.name" placeholder="请输入教室名称" /></el-form-item>
        <el-form-item label="楼栋"><el-input v-model="cForm.building" placeholder="请输入楼栋" /></el-form-item>
        <el-form-item label="楼层"><el-input-number v-model="cForm.floor" :min="1" :max="30" style="width: 100%" /></el-form-item>
        <el-form-item label="容量"><el-input-number v-model="cForm.capacity" :min="1" :max="500" style="width: 100%" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="cForm.type" style="width: 100%">
            <el-option label="多媒体教室" value="MULTIMEDIA" />
            <el-option label="机房" value="COMPUTER" />
            <el-option label="实验室" value="LAB" />
            <el-option label="普通教室" value="NORMAL" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="cForm.status" style="width: 100%">
            <el-option label="可用" value="AVAILABLE" />
            <el-option label="维护中" value="MAINTENANCE" />
            <el-option label="停用" value="DISABLED" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备"><el-input v-model="cForm.equipment" placeholder="如：投影仪、空调、白板" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="cForm.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cDialog = false">取消</el-button>
        <button class="btn-gradient" @click="saveClassroom">
          <span>保存</span>
          <el-icon><Check /></el-icon>
        </button>
      </template>
    </el-dialog>

    <!-- 用户编辑弹窗 -->
    <el-dialog v-model="uDialog" width="500px" class="custom-dialog">
      <template #header>
        <div class="dialog-header">
          <el-icon class="dialog-icon"><User /></el-icon>
          <div>
            <h3>{{ uForm.id ? '编辑用户' : '新增用户' }}</h3>
            <span>{{ uForm.id ? '修改用户信息' : '填写新用户信息' }}</span>
          </div>
        </div>
      </template>
      <el-form :model="uForm" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="uForm.username" :disabled="!!uForm.id" placeholder="登录用户名" /></el-form-item>
        <el-form-item v-if="!uForm.id" label="密码"><el-input v-model="uForm.password" type="password" show-password placeholder="设置登录密码" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="uForm.name" placeholder="用户姓名" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="uForm.role" style="width: 100%">
            <el-option label="管理员" value="ADMIN" />
            <el-option label="教师" value="TEACHER" />
            <el-option label="学生" value="STUDENT" />
          </el-select>
        </el-form-item>
        <el-form-item label="院系"><el-input v-model="uForm.department" placeholder="所属院系" /></el-form-item>
        <el-form-item label="手机"><el-input v-model="uForm.phone" placeholder="手机号码" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="uForm.email" placeholder="邮箱地址" /></el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="uForm.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uDialog = false">取消</el-button>
        <button class="btn-gradient" @click="saveUser">
          <span>保存</span>
          <el-icon><Check /></el-icon>
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  School, User, Search, Plus, Edit, Delete, Check
} from '@element-plus/icons-vue'
import { classroomApi, userApi } from '@/api'

const activeTab = ref('classroom')

const classrooms = ref([])
const cTotal = ref(0)
const cQuery = reactive({ keyword: '', page: 1, pageSize: 10 })
const cDialog = ref(false)
const cForm = reactive({})

const users = ref([])
const uTotal = ref(0)
const uQuery = reactive({ keyword: '', page: 1, pageSize: 10 })
const uDialog = ref(false)
const uForm = reactive({})

const statusText = (s) => ({ AVAILABLE: '可用', MAINTENANCE: '维护中', DISABLED: '停用' }[s] || s)
const typeText = (t) => ({ MULTIMEDIA: '多媒体', COMPUTER: '机房', LAB: '实验室', NORMAL: '普通' }[t] || t)
const roleText = (r) => ({ ADMIN: '管理员', TEACHER: '教师', STUDENT: '学生' }[r] || r)
const rowClass = ({ rowIndex }) => `row-${rowIndex}`

const loadClassrooms = async () => {
  try {
    const res = await classroomApi.getList(cQuery)
    classrooms.value = res.data.list || []
    cTotal.value = res.data.total || 0
  } catch (e) {
    classrooms.value = []
    cTotal.value = 0
  }
}

const loadUsers = async () => {
  try {
    const res = await userApi.getList(uQuery)
    users.value = res.data.list || []
    uTotal.value = res.data.total || 0
  } catch (e) {
    users.value = []
    uTotal.value = 0
  }
}

const openClassroomDialog = (row) => {
  Object.assign(cForm, row || { id: null, name: '', building: '', floor: 1, capacity: 40, type: 'NORMAL', status: 'AVAILABLE', equipment: '', remark: '' })
  cDialog.value = true
}

const saveClassroom = async () => {
  try {
    if (cForm.id) {
      await classroomApi.update(cForm.id, cForm)
    } else {
      await classroomApi.create(cForm)
    }
    ElMessage.success('保存成功')
    cDialog.value = false
    loadClassrooms()
  } catch (e) { /* handled */ }
}

const deleteClassroom = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除教室"${row.name}"？`, '提示', { type: 'warning' })
    await classroomApi.remove(row.id)
    ElMessage.success('删除成功')
    loadClassrooms()
  } catch (e) { /* 取消 */ }
}

const openUserDialog = (row) => {
  Object.assign(uForm, row || { id: null, username: '', password: '', name: '', role: 'STUDENT', department: '', phone: '', email: '', status: 1 })
  uDialog.value = true
}

const saveUser = async () => {
  try {
    if (uForm.id) {
      await userApi.update(uForm.id, uForm)
    } else {
      await userApi.create(uForm)
    }
    ElMessage.success('保存成功')
    uDialog.value = false
    loadUsers()
  } catch (e) { /* handled */ }
}

const deleteUser = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除用户"${row.name}"？`, '提示', { type: 'warning' })
    await userApi.remove(row.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (e) { /* 取消 */ }
}

onMounted(() => {
  loadClassrooms()
  loadUsers()
})
</script>

<style lang="scss" scoped>
.tabs-card {
  padding: 20px 24px;
  animation: fadeIn 0.4s ease;
}

:deep(.el-tabs__item) {
  height: 44px;
  font-size: 14px;
  font-weight: 500;

  &.is-active {
    color: var(--role-primary, #6366f1);
    font-weight: 600;
  }
}

:deep(.el-tabs__active-bar) {
  background: var(--role-primary, #6366f1);
  height: 3px;
  border-radius: 3px;
}

.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  .el-icon { font-size: 16px; }
}

.tab-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.btn-gradient {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: var(--role-primary, #6366f1);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover { filter: brightness(.96); }

  &.btn-add {
    background: #10b981;
  }
}

.name-cell {
  font-weight: 600;
  color: #1e293b;
}

.num-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 6px;
  background: rgba(99, 102, 241, 0.08);
  color: #6366f1;
  font-weight: 600;
  font-size: 13px;
  font-variant-numeric: tabular-nums;
}

.type-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;

  &.multimedia { background: rgba(99, 102, 241, 0.12); color: #6366f1; }
  &.computer { background: rgba(6, 182, 212, 0.12); color: #06b6d4; }
  &.lab { background: rgba(16, 185, 129, 0.12); color: #10b981; }
  &.normal { background: rgba(139, 92, 246, 0.12); color: #8b5cf6; }
}

.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;

  .status-light { width: 6px; height: 6px; border-radius: 50%; }

  &.available { background: rgba(16, 185, 129, 0.12); color: #10b981; .status-light { background: #10b981; } }
  &.maintenance { background: rgba(245, 158, 11, 0.12); color: #f59e0b; .status-light { background: #f59e0b; } }
  &.disabled { background: rgba(156, 163, 175, 0.12); color: #9ca3af; .status-light { background: #9ca3af; } }
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;

  .user-avatar {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    color: white;

    &.admin { background: #6366f1; }
    &.teacher { background: #10b981; }
    &.student { background: #f59e0b; }
  }
}

.role-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;

  &.admin { background: rgba(99, 102, 241, 0.12); color: #6366f1; }
  &.teacher { background: rgba(16, 185, 129, 0.12); color: #10b981; }
  &.student { background: rgba(245, 158, 11, 0.12); color: #f59e0b; }
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;

  .status-light { width: 6px; height: 6px; border-radius: 50%; }

  &.active {
    background: rgba(16, 185, 129, 0.12);
    color: #10b981;
    .status-light { background: #10b981; }
  }
  &.inactive {
    background: rgba(239, 68, 68, 0.12);
    color: #ef4444;
    .status-light { background: #ef4444; }
  }
}

.action-row {
  display: flex;
  gap: 8px;

  .action-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.3s;

    .el-icon { font-size: 13px; }

    &.edit {
      background: rgba(99, 102, 241, 0.1);
      color: #6366f1;
      &:hover { background: #6366f1; color: white; }
    }
    &.danger {
      background: rgba(239, 68, 68, 0.1);
      color: #ef4444;
      &:hover { background: #ef4444; color: white; }
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 12px;

  .dialog-icon {
    width: 40px; height: 40px;
    border-radius: 10px;
    background: var(--role-primary, #6366f1);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
  }
  h3 { font-size: 16px; font-weight: 700; color: #1e293b; }
  span { font-size: 12px; color: #94a3b8; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

:deep(.el-table__row) {
  animation: rowIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}
@keyframes rowIn {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
