<template>
  <div class="no-show-list table-page">
    <!-- 提示栏 -->
    <div class="alert-bar glass-card">
      <el-icon class="alert-icon"><WarningFilled /></el-icon>
      <div>
        <h3>爽约记录</h3>
        <span>已通过审批但未在规定时间内签到的预约，系统自动标记为爽约。</span>
      </div>
    </div>

    <!-- 表格卡片 -->
    <div class="table-card glass-card">
      <div class="table-header">
        <h3>爽约列表</h3>
        <span class="table-count">共 {{ noShows.length }} 条记录</span>
      </div>
      <el-table :data="noShows" stripe v-if="noShows.length" :row-class-name="rowClass">
        <el-table-column prop="title" label="预约主题" min-width="160">
          <template #default="{ row }">
            <div class="title-cell">
              <span class="title-dot noshow"></span>
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
        <el-table-column label="预约时间" width="320">
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
          <template #default>
            <span class="status-tag noshow">
              <span class="status-light"></span>
              爽约
            </span>
          </template>
        </el-table-column>
      </el-table>
      <div v-else class="empty-block">
        <el-icon><CircleCheck /></el-icon>
        <p>暂无爽约记录</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Clock, WarningFilled, CircleCheck } from '@element-plus/icons-vue'
import { reservationApi } from '@/api'

const noShows = ref([])
const rowClass = ({ rowIndex }) => `row-${rowIndex}`

const loadData = async () => {
  try {
    const res = await reservationApi.getNoShows()
    noShows.value = res.data || []
  } catch (e) {
    noShows.value = []
  }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.no-show-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.alert-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  animation: fadeIn 0.4s ease;

  .alert-icon {
    font-size: 28px;
    color: #f59e0b;
    flex-shrink: 0;
  }
  h3 { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 2px; }
  span { font-size: 13px; color: var(--text-secondary); }
}

.table-card {
  animation: cardIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  h3 { font-size: 16px; font-weight: 700; color: var(--text-primary); }
  .table-count { font-size: 13px; color: var(--text-tertiary); }
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;

  .title-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    &.noshow { background: #ef4444; }
  }
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;

  .user-avatar {
    width: 24px; height: 24px;
    border-radius: 50%;
    background: var(--role-color);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
  }
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-secondary);
  .el-icon { font-size: 14px; color: var(--text-tertiary); }
  .time-sep { color: var(--text-tertiary); margin: 0 2px; }
}

.num-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(var(--role-color-rgb), 0.1);
  color: var(--role-color);
}

.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;

  &.noshow {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    .status-light { background: #ef4444; }
  }
  .status-light {
    width: 6px; height: 6px;
    border-radius: 50%;
  }
}

.empty-block {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);

  .el-icon { font-size: 40px; display: block; margin: 0 auto 8px; color: var(--text-quaternary); }
  p { font-size: 13px; }
}

:deep(.el-table__row) {
  animation: rowIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}
@keyframes rowIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes cardIn { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
</style>
