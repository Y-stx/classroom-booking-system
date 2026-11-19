<template>
  <div class="reservation-list table-page">
    <!-- 筛选栏 -->
    <div class="filter-bar glass-card">
      <el-input v-model="query.keyword" placeholder="搜索预约主题" clearable style="width: 240px" @keyup.enter="loadData">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px" @change="loadData">
        <el-option label="待审批" value="PENDING" />
        <el-option label="已通过" value="APPROVED" />
        <el-option label="已驳回" value="REJECTED" />
        <el-option label="已完成" value="COMPLETED" />
        <el-option label="已取消" value="CANCELLED" />
      </el-select>
      <button class="btn-gradient" @click="loadData">
        <el-icon><Search /></el-icon>
        <span>查询</span>
      </button>

      <button class="btn-gradient" @click="batchVisible = true">
        <el-icon><Calendar /></el-icon>
        <span>批量预约</span>
      </button>

      <div class="filter-right">
        <button class="quick-chip" :class="{ active: !query.status }" @click="query.status = ''; loadData()">全部</button>
        <button class="quick-chip" :class="{ active: query.status === 'PENDING' }" @click="query.status = 'PENDING'; loadData()">
          <span class="chip-dot amber"></span>待审批
        </button>
        <button class="quick-chip" :class="{ active: query.status === 'APPROVED' }" @click="query.status = 'APPROVED'; loadData()">
          <span class="chip-dot green"></span>已通过
        </button>
        <button class="quick-chip" :class="{ active: query.status === 'COMPLETED' }" @click="query.status = 'COMPLETED'; loadData()">
          <span class="chip-dot blue"></span>已完成
        </button>
      </div>
    </div>

    <!-- 表格卡片 -->
    <div class="table-card glass-card">
      <div class="table-header">
        <h3>我的预约</h3>
        <span class="table-count">共 {{ total }} 条记录</span>
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
        <el-table-column prop="attendees" label="人数" width="70" align="center">
          <template #default="{ row }">
            <span class="num-badge">{{ row.attendees }}</span>
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
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <div class="action-row">
              <button v-if="canCancel(row.status)" class="action-btn danger" @click="handleCancel(row)">
                <el-icon><Close /></el-icon>
                <span>取消</span>
              </button>
              <button v-if="row.status === 'APPROVED'" class="action-btn success" @click="goCheckIn(row)">
                <el-icon><Check /></el-icon>
                <span>签到</span>
              </button>
              <span v-if="!canCancel(row.status) && row.status !== 'APPROVED'" class="no-action">—</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" layout="prev, pager, next" @current-change="loadData" />
      </div>
    </div>

    <!-- 取消弹窗 -->
    <el-dialog v-model="cancelVisible" width="440px" class="custom-dialog">
      <template #header>
        <div class="dialog-header danger">
          <el-icon class="dialog-icon"><CircleCloseFilled /></el-icon>
          <div>
            <h3>取消预约</h3>
            <span>{{ currentRow?.title }}</span>
          </div>
        </div>
      </template>
      <el-form>
        <el-form-item label="取消原因" required>
          <el-input v-model="cancelReason" type="textarea" :rows="3" placeholder="请输入取消原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelVisible = false">关闭</el-button>
        <button class="btn-gradient danger-btn" @click="confirmCancel">确认取消</button>
      </template>
    </el-dialog>

    <!-- 签到/签退弹窗 -->
    <el-dialog v-model="checkVisible" width="500px" class="custom-dialog">
      <template #header>
        <div class="dialog-header" :class="checkMode === 'in' ? 'success' : 'primary'">
          <el-icon class="dialog-icon">
            <CircleCheckFilled v-if="checkMode === 'in'" />
            <EditPen v-else />
          </el-icon>
          <div>
            <h3>{{ checkMode === 'in' ? '签到登记' : '签退登记' }}</h3>
            <span>{{ currentRow?.title }}</span>
          </div>
        </div>
      </template>
      <div class="check-info" v-if="currentRow">
        <div class="info-block">
          <el-icon><School /></el-icon>
          <span>{{ currentRow.classroomName }}</span>
        </div>
        <div class="info-block">
          <el-icon><User /></el-icon>
          <span>{{ currentRow.attendees }} 人</span>
        </div>
        <div class="info-block">
          <el-icon><Clock /></el-icon>
          <span>{{ currentRow.startTime }}</span>
        </div>
      </div>
      <el-form label-width="100px" v-if="checkMode === 'out'">
        <el-form-item label="实际人数">
          <el-input-number v-model="checkForm.actualAttendees" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="设备状况">
          <el-input v-model="checkForm.equipmentStatus" placeholder="如：设备完好、投影仪故障等" />
        </el-form-item>
        <el-form-item label="卫生评分">
          <el-rate v-model="checkForm.cleanliness" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="checkForm.notes" type="textarea" :rows="2" placeholder="其他需要登记的内容" />
        </el-form-item>
      </el-form>
      <div class="check-tip" v-if="checkMode === 'in'">
        <el-icon><InfoFilled /></el-icon>
        <p>签到后将进入使用中状态，结束使用时请记得签退登记。</p>
      </div>
      <template #footer>
        <el-button @click="checkVisible = false">取消</el-button>
        <button class="btn-gradient" @click="submitCheck">
          <span>确认{{ checkMode === 'in' ? '签到' : '签退' }}</span>
          <el-icon><ArrowRight /></el-icon>
        </button>
      </template>
    </el-dialog>

    <!-- 批量预约弹窗 -->
    <el-dialog v-model="batchVisible" width="520px" class="custom-dialog">
      <template #header>
        <div class="dialog-header primary">
          <el-icon class="dialog-icon"><Calendar /></el-icon>
          <div>
            <h3>批量预约</h3>
            <span>按周次自动生成重复预约</span>
          </div>
        </div>
      </template>
      <el-form label-width="100px">
        <el-form-item label="教室" required>
          <el-select v-model="batchForm.classroomId" placeholder="选择教室" filterable style="width: 100%">
            <el-option v-for="c in classroomOptions" :key="c.id" :label="`${c.name}（${c.building}）`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="预约主题" required>
          <el-input v-model="batchForm.title" placeholder="如：每周社团例会" />
        </el-form-item>
        <el-form-item label="预约目的">
          <el-input v-model="batchForm.purpose" placeholder="选填" />
        </el-form-item>
        <el-form-item label="开始时间" required>
          <el-date-picker v-model="batchForm.startTime" type="datetime" placeholder="选择开始时间" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" required>
          <el-date-picker v-model="batchForm.endTime" type="datetime" placeholder="选择结束时间" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="预计人数">
          <el-input-number v-model="batchForm.attendees" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="重复周数">
          <el-input-number v-model="batchForm.weekCount" :min="1" :max="16" style="width: 100%" />
        </el-form-item>
      </el-form>
      <div class="check-tip">
        <el-icon><InfoFilled /></el-icon>
        <p>系统将按周次自动生成 {{ batchForm.weekCount }} 条预约，冲突时段将自动跳过。</p>
      </div>
      <template #footer>
        <el-button @click="batchVisible = false">取消</el-button>
        <button class="btn-gradient" @click="submitBatch">
          <span>确认批量预约</span>
          <el-icon><ArrowRight /></el-icon>
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Clock, Close, Check, CircleCloseFilled,
  CircleCheckFilled, EditPen, School, User, ArrowRight, InfoFilled, Calendar
} from '@element-plus/icons-vue'
import { reservationApi, usageApi, classroomApi } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const reservations = ref([])
const total = ref(0)
const query = reactive({ keyword: '', status: '', page: 1, pageSize: 10 })

const cancelVisible = ref(false)
const cancelReason = ref('')
const currentRow = ref(null)

const checkVisible = ref(false)
const checkMode = ref('in')
const checkForm = reactive({ actualAttendees: 1, equipmentStatus: '', cleanliness: 5, notes: '' })

const batchVisible = ref(false)
const classroomOptions = ref([])
const batchForm = reactive({ classroomId: null, title: '', purpose: '', startTime: '', endTime: '', attendees: 10, weekCount: 4 })

const statusText = (s) => ({ PENDING: '待审批', APPROVED: '已通过', REJECTED: '已驳回', COMPLETED: '已完成', CANCELLED: '已取消' }[s] || s)
const canCancel = (s) => ['PENDING', 'APPROVED'].includes(s)
const rowClass = ({ rowIndex }) => `row-${rowIndex}`

const loadData = async () => {
  try {
    const res = await reservationApi.getMyList(query)
    reservations.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (e) {
    reservations.value = []
    total.value = 0
  }
}

const handleCancel = (row) => {
  currentRow.value = row
  cancelReason.value = ''
  cancelVisible.value = true
}

const confirmCancel = async () => {
  if (!cancelReason.value.trim()) {
    ElMessage.warning('请填写取消原因')
    return
  }
  try {
    await reservationApi.cancel(currentRow.value.id, cancelReason.value)
    ElMessage.success('已取消预约')
    cancelVisible.value = false
    loadData()
  } catch (e) { /* handled */ }
}

const goCheckIn = (row) => {
  currentRow.value = row
  checkMode.value = 'in'
  Object.assign(checkForm, { actualAttendees: 1, equipmentStatus: '', cleanliness: 5, notes: '' })
  checkVisible.value = true
}

const submitCheck = async () => {
  try {
    if (checkMode.value === 'in') {
      await usageApi.checkIn(currentRow.value.id)
      ElMessage.success('签到成功')
      checkMode.value = 'out'
      ElMessageBox.alert('签到成功！使用结束后请记得签退登记。', '提示', { type: 'success' })
    } else {
      await usageApi.checkOut({ reservationId: currentRow.value.id, ...checkForm })
      ElMessage.success('签退成功')
      checkVisible.value = false
      loadData()
    }
  } catch (e) { /* handled */ }
}

const loadClassrooms = async () => {
  try {
    const res = await classroomApi.getList({ page: 1, pageSize: 100 })
    classroomOptions.value = res.data.list || []
  } catch (e) { /* 忽略 */ }
}

const submitBatch = async () => {
  if (!batchForm.classroomId) { ElMessage.warning('请选择教室'); return }
  if (!batchForm.title.trim()) { ElMessage.warning('请填写预约主题'); return }
  if (!batchForm.startTime || !batchForm.endTime) { ElMessage.warning('请选择起止时间'); return }
  try {
    const res = await reservationApi.batchCreate(batchForm)
    ElMessage.success(res.message || '批量预约完成')
    batchVisible.value = false
    loadData()
  } catch (e) { /* handled */ }
}

onMounted(() => {
  loadData()
  loadClassrooms()
})
</script>

<style lang="scss" scoped>
.reservation-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-bar {
  animation: fadeIn 0.4s ease;
}

.table-card {
  animation: cardIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.no-action { color: var(--text-muted); font-size: 14px; }

.danger-btn {
  background: #ef4444 !important;
  &:hover { filter: brightness(.96); }
}

// 动画
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
  .filter-bar { flex-direction: column; align-items: stretch; }
  .filter-right { margin-left: 0; flex-wrap: wrap; }
}
</style>
