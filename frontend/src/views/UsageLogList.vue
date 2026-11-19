<template>
  <div class="usage-list">
    <!-- 筛选栏 -->
    <div class="filter-bar glass-card">
      <el-input v-model="keyword" placeholder="搜索预约主题" clearable style="width: 240px" @keyup.enter="loadData">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <button class="btn-gradient" @click="loadData">
        <el-icon><Search /></el-icon>
        <span>查询</span>
      </button>
      <span class="filter-tip">共 {{ total }} 条使用记录</span>
    </div>

    <!-- 表格 -->
    <div class="table-card glass-card">
      <div class="table-header">
        <div>
          <h3>使用登记记录</h3>
          <span class="table-sub">签到签退与设备登记</span>
        </div>
        <div class="table-dot"></div>
      </div>
      <el-table :data="logs" stripe :row-class-name="rowClass">
        <el-table-column prop="title" label="预约主题" min-width="160">
          <template #default="{ row }">
            <div class="title-cell">
              <el-icon><Document /></el-icon>
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="classroomName" label="教室" width="120" />
        <el-table-column prop="userName" label="登记人" width="110">
          <template #default="{ row }">
            <div class="user-cell">
              <span class="user-avatar">{{ row.userName?.charAt(0) }}</span>
              <span>{{ row.userName }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="checkInTime" label="签到时间" width="180">
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon class="in"><CircleCheckFilled /></el-icon>
              <span>{{ row.checkInTime }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="checkOutTime" label="签退时间" width="180">
          <template #default="{ row }">
            <div class="time-cell" v-if="row.checkOutTime">
              <el-icon class="out"><EditPen /></el-icon>
              <span>{{ row.checkOutTime }}</span>
            </div>
            <span v-else class="no-data">未签退</span>
          </template>
        </el-table-column>
        <el-table-column prop="actualAttendees" label="实际人数" width="100" align="center">
          <template #default="{ row }">
            <span class="num-badge">{{ row.actualAttendees }}</span>
          </template>
        </el-table-column>
        <el-table-column label="卫生评分" width="140">
          <template #default="{ row }">
            <div class="rate-cell">
              <el-rate v-model="row.cleanliness" disabled size="small" />
              <span class="rate-text">{{ row.cleanliness }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="equipmentStatus" label="设备状况" min-width="160">
          <template #default="{ row }">
            <el-popover
              v-if="row.notes"
              placement="top"
              :width="280"
              trigger="click"
              :show-arrow="true"
            >
              <template #reference>
                <span class="equip-tag clickable" :class="equipClass(row.equipmentStatus)">
                  {{ row.equipmentStatus || '—' }}
                  <el-icon class="hint-icon"><View /></el-icon>
                </span>
              </template>
              <div class="notes-popover">
                <div class="notes-title">
                  <el-icon><ChatDotRound /></el-icon>
                  <span>签退备注</span>
                </div>
                <div class="notes-content">{{ row.notes }}</div>
              </div>
            </el-popover>
            <span v-else class="equip-tag" :class="equipClass(row.equipmentStatus)">
              {{ row.equipmentStatus || '—' }}
            </span>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" layout="prev, pager, next" @current-change="loadData" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  Search, Document, CircleCheckFilled, EditPen, View, ChatDotRound
} from '@element-plus/icons-vue'
import { usageApi } from '@/api'

const logs = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')

const rowClass = ({ rowIndex }) => `row-${rowIndex}`

const equipClass = (s) => {
  if (!s) return ''
  if (/好|完好|正常|良好/.test(s)) return 'good'
  if (/故障|损坏|问题|异常/.test(s)) return 'bad'
  return 'normal'
}

const loadData = async () => {
  try {
    const res = await usageApi.getList({ keyword: keyword.value, page: page.value, pageSize: pageSize.value })
    logs.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (e) {
    logs.value = []
    total.value = 0
  }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.usage-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  padding: 16px;
  align-items: center;
  animation: fadeIn 0.4s ease;

  .filter-tip {
    font-size: 13px;
    color: #94a3b8;
    margin-left: auto;
  }
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
}

.table-card {
  padding: 20px 24px;
  animation: cardIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);

  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;

    h3 { font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 2px; }
    .table-sub { font-size: 11px; color: #94a3b8; }
    .table-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: #06b6d4;
    }
  }
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  .el-icon { color: #94a3b8; font-size: 16px; }
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;

  .user-avatar {
    width: 24px; height: 24px;
    border-radius: 50%;
    background: var(--role-primary, #6366f1);
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
  gap: 6px;
  font-size: 13px;
  color: #64748b;

  .el-icon {
    font-size: 14px;
    &.in { color: #10b981; }
    &.out { color: #6366f1; }
  }
}

.no-data {
  font-size: 12px;
  color: #cbd5e1;
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

.rate-cell {
  display: flex;
  align-items: center;
  gap: 6px;

  .rate-text {
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
  }
}

.equip-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;

  &.good { background: rgba(16, 185, 129, 0.12); color: #10b981; }
  &.bad { background: rgba(239, 68, 68, 0.12); color: #ef4444; }
  &.normal { background: rgba(148, 163, 184, 0.12); color: #64748b; }

  &.clickable {
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 4px;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .hint-icon {
      font-size: 12px;
      opacity: 0.5;
      transition: opacity 0.2s;
    }

    &:hover .hint-icon {
      opacity: 1;
    }
  }
}

.notes-popover {
  .notes-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid #f1f5f9;

    .el-icon {
      color: var(--role-primary, #6366f1);
      font-size: 15px;
    }
  }

  .notes-content {
    font-size: 13px;
    color: #475569;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-all;
  }
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
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
</style>
