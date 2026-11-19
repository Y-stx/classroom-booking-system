<template>
  <div class="approval-center">
    <!-- 统计概览 -->
    <div class="stats-row">
      <div class="mini-stat glass-card">
        <div class="ms-icon pending-bg">
          <el-icon><Clock /></el-icon>
        </div>
        <div>
          <span class="ms-value">{{ stats.pending }}</span>
          <span class="ms-label">待审批</span>
        </div>
      </div>
      <div class="mini-stat glass-card">
        <div class="ms-icon approved-bg">
          <el-icon><Check /></el-icon>
        </div>
        <div>
          <span class="ms-value">{{ stats.today }}</span>
          <span class="ms-label">今日处理</span>
        </div>
      </div>
      <div class="mini-stat glass-card">
        <div class="ms-icon total-bg">
          <el-icon><Document /></el-icon>
        </div>
        <div>
          <span class="ms-value">{{ stats.total }}</span>
          <span class="ms-label">总记录</span>
        </div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar glass-card">
      <el-input v-model="query.keyword" placeholder="搜索预约主题" clearable style="width: 240px" @keyup.enter="loadData">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <button class="btn-gradient" @click="loadData">
        <el-icon><Search /></el-icon>
        <span>查询</span>
      </button>
      <span class="filter-tip">共 {{ total }} 条待审批记录</span>
    </div>

    <!-- 表格 -->
    <div class="table-card glass-card">
      <div class="table-header">
        <div>
          <h3>审批队列</h3>
          <span class="table-sub">点击通过或驳回处理预约</span>
        </div>
        <div class="table-dot"></div>
      </div>
      <el-table :data="reservations" stripe :row-class-name="rowClass">
        <el-table-column prop="title" label="预约主题" min-width="160">
          <template #default="{ row }">
            <div class="title-cell">
              <span class="title-dot" :class="row.status?.toLowerCase()"></span>
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="classroomName" label="教室" width="120" />
        <el-table-column prop="building" label="楼栋" width="120" />
        <el-table-column prop="userName" label="预约人" width="110">
          <template #default="{ row }">
            <div class="user-cell">
              <span class="user-avatar">{{ row.userName?.charAt(0) }}</span>
              <span>{{ row.userName }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="320">
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon><Clock /></el-icon>
              <span>{{ row.startTime }}</span>
              <span class="time-sep">→</span>
              <span>{{ row.endTime }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="attendees" label="人数" width="80" align="center">
          <template #default="{ row }">
            <span class="num-badge">{{ row.attendees }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <span class="status-tag" :class="row.status?.toLowerCase()">
              <span class="status-light"></span>
              {{ statusText(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-row" v-if="row.status === 'PENDING'">
              <button class="action-btn approve" @click="handleApprove(row)">
                <el-icon><Select /></el-icon>
                <span>通过</span>
              </button>
              <button class="action-btn reject" @click="handleReject(row)">
                <el-icon><CloseBold /></el-icon>
                <span>驳回</span>
              </button>
            </div>
            <span v-else class="no-action">已处理</span>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" layout="prev, pager, next" @current-change="loadData" />
      </div>
    </div>

    <!-- 驳回弹窗 -->
    <el-dialog v-model="rejectVisible" width="440px" class="custom-dialog">
      <template #header>
        <div class="dialog-header danger">
          <el-icon class="dialog-icon"><CircleCloseFilled /></el-icon>
          <div>
            <h3>驳回预约</h3>
            <span>{{ currentRow?.title }}</span>
          </div>
        </div>
      </template>
      <el-form>
        <el-form-item label="驳回原因">
          <el-input v-model="rejectReason" type="textarea" :rows="3" placeholder="请输入驳回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <button class="btn-gradient danger-btn" @click="confirmReject">确认驳回</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Clock, Check, Document, Select, CloseBold,
  CircleCloseFilled
} from '@element-plus/icons-vue'
import { approvalApi } from '@/api'

const reservations = ref([])
const total = ref(0)
const query = reactive({ keyword: '', page: 1, pageSize: 10 })

const stats = reactive({ pending: 0, today: 0, total: 0 })

const rejectVisible = ref(false)
const rejectReason = ref('')
const currentRow = ref(null)

const statusText = (s) => ({ PENDING: '待审批', APPROVED: '已通过', REJECTED: '已驳回', COMPLETED: '已完成', CANCELLED: '已取消' }[s] || s)
const rowClass = ({ rowIndex }) => `row-${rowIndex}`

const loadData = async () => {
  try {
    const res = await approvalApi.getPending(query)
    reservations.value = res.data.list || []
    total.value = res.data.total || 0
    stats.pending = res.data.total || 0
    stats.total = res.data.total || 0
  } catch (e) {
    reservations.value = []
    total.value = 0
  }
}

const handleApprove = async (row) => {
  try {
    await ElMessageBox.confirm(`确认通过预约"${row.title}"？`, '审批确认', { type: 'success' })
    await approvalApi.approve(row.id)
    ElMessage.success('已通过审批')
    loadData()
  } catch (e) { /* 取消 */ }
}

const handleReject = (row) => {
  currentRow.value = row
  rejectReason.value = ''
  rejectVisible.value = true
}

const confirmReject = async () => {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请输入驳回原因')
    return
  }
  try {
    await approvalApi.reject(currentRow.value.id, rejectReason.value)
    ElMessage.success('已驳回')
    rejectVisible.value = false
    loadData()
  } catch (e) { /* handled */ }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.approval-center {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

// 统计概览
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.mini-stat {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  animation: cardIn 0.4s ease;

  .ms-icon {
    width: 48px; height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;

    &.pending-bg { background: rgba(245, 158, 11, 0.12); color: #d97706; }
    &.approved-bg { background: rgba(16, 185, 129, 0.12); color: #059669; }
    &.total-bg { background: var(--primary-50); color: var(--primary); }
  }

  div {
    display: flex;
    flex-direction: column;
    .ms-value {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-primary);
      font-variant-numeric: tabular-nums;
    }
    .ms-label {
      font-size: 12px;
      color: var(--text-tertiary);
    }
  }
}

.table-card {
  padding: 20px 24px;
  animation: cardIn 0.5s ease;

  // 装饰性圆点（.table-header / h3 / .table-sub 由全局提供）
  .table-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #f59e0b;
  }
}

.no-action {
  font-size: 12px;
  color: var(--text-muted);
  padding: 6px 12px;
}

.danger-btn {
  background: #ef4444 !important;
  &:hover { filter: brightness(0.94); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

:deep(.el-table__row) {
  animation: rowIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}
@keyframes rowIn {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

@media (max-width: 768px) {
  .stats-row { grid-template-columns: 1fr; }
}
</style>
