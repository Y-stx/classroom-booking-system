<template>
  <div class="admin-home">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner glass-card admin-theme">
      <div class="banner-content">
        <div class="banner-text">
          <span class="role-badge">管理员</span>
          <h2>{{ greeting }}，{{ userStore.displayName }}</h2>
          <p>{{ dateStr }} · {{ weekStr }}</p>
        </div>
        <div class="banner-stats" v-if="stats.totalClassrooms !== undefined">
          <div class="quick-stat">
            <span class="qs-value">{{ stats.pendingApprovals || 0 }}</span>
            <span class="qs-label">待审批</span>
          </div>
          <div class="divider"></div>
          <div class="quick-stat">
            <span class="qs-value warn">{{ stats.todayReservations || 0 }}</span>
            <span class="qs-label">今日预约</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <StatCard v-for="(card, i) in statCards" :key="card.label" v-bind="card" :style="{ '--i': i }" />
    </div>

    <!-- 图表区 -->
    <div class="charts-grid">
      <div class="chart-card glass-card">
        <div class="chart-header">
          <div>
            <h3>预约状态分布</h3>
            <span class="chart-sub">实时统计</span>
          </div>
          <div class="chart-dot"></div>
        </div>
        <v-chart class="chart" :option="pieOption" autoresize />
      </div>
      <div class="chart-card glass-card">
        <div class="chart-header">
          <div>
            <h3>教室状态分布</h3>
            <span class="chart-sub">实时统计</span>
          </div>
          <div class="chart-dot dot-cool"></div>
        </div>
        <v-chart class="chart" :option="barOption" autoresize />
      </div>
    </div>

    <!-- 使用率统计图表 -->
    <div class="charts-grid">
      <div class="chart-card glass-card">
        <div class="chart-header">
          <div>
            <h3>教室使用率排行</h3>
            <span class="chart-sub">按预约次数统计</span>
          </div>
          <div class="chart-dot dot-usage"></div>
        </div>
        <v-chart class="chart" :option="usageBarOption" autoresize />
      </div>
      <div class="chart-card glass-card">
        <div class="chart-header">
          <div>
            <h3>周预约趋势</h3>
            <span class="chart-sub">近8周预约数</span>
          </div>
          <div class="chart-dot dot-trend"></div>
        </div>
        <v-chart class="chart" :option="weeklyLineOption" autoresize />
      </div>
    </div>

    <!-- 待审批列表 -->
    <div class="block-card glass-card">
      <div class="block-header">
        <div>
          <h3>待审批列表</h3>
          <span class="block-sub">点击通过或驳回处理</span>
        </div>
        <el-button text type="primary" @click="$router.push('/admin/approvals')">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <el-table :data="pendingList" stripe v-if="pendingList.length">
        <el-table-column prop="title" label="预约主题" min-width="160">
          <template #default="{ row }">
            <div class="title-cell">
              <span class="title-dot pending"></span>
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="classroomName" label="教室" width="120" />
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
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-row">
              <button class="action-btn approve" @click="handleApprove(row)">
                <el-icon><Select /></el-icon>
                <span>通过</span>
              </button>
              <button class="action-btn reject" @click="goApproval">
                <el-icon><ArrowRight /></el-icon>
                <span>详情</span>
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div v-else class="empty-block">
        <el-icon><CircleCheck /></el-icon>
        <p>暂无待审批预约</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import StatCard from '@/components/StatCard.vue'
import {
  ArrowRight, Clock, Select, CircleCheck
} from '@element-plus/icons-vue'
import { dashboardApi, approvalApi } from '@/api'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

use([CanvasRenderer, PieChart, BarChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const router = useRouter()
const userStore = useUserStore()
const stats = reactive({})
const pendingList = ref([])
const classroomUsage = ref([])
const weeklyUsage = ref([])

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const dateStr = computed(() => {
  const d = new Date()
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}/${pad(d.getMonth()+1)}/${pad(d.getDate())}`
})

const weekStr = computed(() => ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'][new Date().getDay()])

const statCards = computed(() => [
  { label: '教室总数', value: stats.totalClassrooms || 0, icon: 'School', color: '#6366f1' },
  { label: '可用教室', value: stats.availableClassrooms || 0, icon: 'CircleCheck', color: '#10b981' },
  { label: '待审批', value: stats.pendingApprovals || 0, icon: 'Clock', color: '#f59e0b' },
  { label: '今日预约', value: stats.todayReservations || 0, icon: 'Calendar', color: '#8b5cf6' },
  { label: '总预约数', value: stats.totalReservations || 0, icon: 'Document', color: '#3b82f6' },
  { label: '已完成', value: stats.completedReservations || 0, icon: 'CircleCheckFilled', color: '#06b6d4' },
  { label: '总用户数', value: stats.totalUsers || 0, icon: 'User', color: '#ec4899' },
  { label: '维护中', value: stats.maintenanceClassrooms || 0, icon: 'Warning', color: '#ef4444' }
])

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', backgroundColor: 'rgba(255,255,255,0.95)', borderColor: '#eef2ff', borderWidth: 1, textStyle: { color: '#1e293b' } },
  legend: { bottom: 0, icon: 'circle', itemWidth: 8, itemHeight: 8, textStyle: { color: '#64748b', fontSize: 12 } },
  series: [{
    type: 'pie',
    radius: ['45%', '72%'],
    center: ['50%', '45%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
    label: { show: false },
    emphasis: {
      scale: true,
      scaleSize: 8,
      label: { show: true, fontSize: 14, fontWeight: 'bold', formatter: '{b}\n{c}' }
    },
    animationType: 'scale',
    animationEasing: 'elasticOut',
    animationDuration: 1000,
    data: [
      { value: stats.pendingApprovals || 0, name: '待审批', itemStyle: { color: '#f59e0b' } },
      { value: stats.approvedReservations || 0, name: '已通过', itemStyle: { color: '#10b981' } },
      { value: stats.completedReservations || 0, name: '已完成', itemStyle: { color: '#3b82f6' } },
      { value: stats.rejectedReservations || 0, name: '已驳回', itemStyle: { color: '#ef4444' } },
      { value: stats.cancelledReservations || 0, name: '已取消', itemStyle: { color: '#9ca3af' } }
    ]
  }]
}))

const barOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(255,255,255,0.95)', borderColor: '#eef2ff', borderWidth: 1, textStyle: { color: '#1e293b' } },
  xAxis: {
    type: 'category',
    data: ['可用', '维护中', '停用'],
    axisLine: { lineStyle: { color: '#e2e8f0' } },
    axisLabel: { color: '#64748b' },
    axisTick: { show: false }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } },
    axisLabel: { color: '#64748b' }
  },
  series: [{
    type: 'bar',
    barWidth: '45%',
    itemStyle: { borderRadius: [8, 8, 0, 0] },
    animationDuration: 1200,
    animationEasing: 'cubicOut',
    data: [
      { value: stats.availableClassrooms || 0, itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#34d399' }, { offset: 1, color: '#10b981' }] } } },
      { value: stats.maintenanceClassrooms || 0, itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#fbbf24' }, { offset: 1, color: '#f59e0b' }] } } },
      { value: (stats.totalClassrooms || 0) - (stats.availableClassrooms || 0) - (stats.maintenanceClassrooms || 0), itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#cbd5e1' }, { offset: 1, color: '#94a3b8' }] } } }
    ]
  }]
}))

const usageBarOption = computed(() => {
  const sorted = [...classroomUsage.value].sort((a, b) => (b.reservationCount || 0) - (a.reservationCount || 0)).slice(0, 8)
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(255,255,255,0.95)', borderColor: '#eef2ff', borderWidth: 1, textStyle: { color: '#1e293b' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } },
      axisLabel: { color: '#64748b' }
    },
    yAxis: {
      type: 'category',
      data: sorted.map(i => i.classroomName || ''),
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#64748b', fontSize: 11 },
      axisTick: { show: false }
    },
    series: [{
      type: 'bar',
      barWidth: '55%',
      itemStyle: { borderRadius: [0, 8, 8, 0] },
      animationDuration: 1200,
      animationEasing: 'cubicOut',
      data: sorted.map(i => ({
        value: i.reservationCount || 0,
        itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#a78bfa' }, { offset: 1, color: '#8b5cf6' }] } }
      }))
    }]
  }
})

const weeklyLineOption = computed(() => {
  const data = weeklyUsage.value
  return {
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.95)', borderColor: '#eef2ff', borderWidth: 1, textStyle: { color: '#1e293b' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map(i => i.weekLabel || ''),
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#64748b', fontSize: 11 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } },
      axisLabel: { color: '#64748b' }
    },
    series: [{
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { width: 3, color: '#06b6d4' },
      itemStyle: { color: '#06b6d4', borderColor: '#fff', borderWidth: 2 },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(6,182,212,0.25)' }, { offset: 1, color: 'rgba(6,182,212,0.02)' }] } },
      animationDuration: 1500,
      animationEasing: 'cubicOut',
      data: data.map(i => i.reservationCount || 0)
    }]
  }
})

const handleApprove = async (row) => {
  try {
    await ElMessageBox.confirm(`确认通过预约"${row.title}"？`, '审批确认', { type: 'success' })
    await approvalApi.approve(row.id)
    ElMessage.success('已通过审批')
    loadData()
  } catch (e) { /* 取消 */ }
}

const goApproval = () => router.push('/admin/approvals')

const loadData = async () => {
  try {
    const [res1, res2, res3, res4] = await Promise.all([
      dashboardApi.getStats(),
      approvalApi.getPending({ page: 1, pageSize: 5 }),
      dashboardApi.getClassroomUsage(),
      dashboardApi.getWeeklyUsage(8)
    ])
    Object.assign(stats, res1.data)
    pendingList.value = res2.data.list || []
    classroomUsage.value = res3.data || []
    weeklyUsage.value = res4.data || []
  } catch (e) {
    // 忽略
  }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.admin-home {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.admin-theme {
  --role-color: #8b5cf6;
  --role-color-rgb: 139, 92, 246;
  --role-soft: rgba(var(--role-color-rgb), 0.12);
}

.welcome-banner {
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(var(--role-color-rgb), 0.07), transparent 60%);
  animation: bannerIn 0.5s ease;

  .banner-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .role-badge {
    display: inline-block;
    padding: 2px 10px;
    background: var(--role-color);
    color: white;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  .banner-text {
    h2 {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 4px;
      letter-spacing: -0.01em;
    }
    p { font-size: 14px; color: var(--text-secondary); }
  }

  .banner-stats {
    display: flex;
    align-items: center;
    gap: 24px;

    .quick-stat {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;

      .qs-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--role-color);
        font-variant-numeric: tabular-nums;
        &.warn { color: #f59e0b; }
      }
      .qs-label { font-size: 12px; color: var(--text-tertiary); }
    }
    .divider { width: 1px; height: 36px; background: var(--border-color); }
  }
}

@keyframes bannerIn { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;

  > :deep(*) {
    animation: cardIn 0.4s calc(var(--i) * 0.05s) ease both;
  }
}

@keyframes cardIn { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-card {
  padding: 24px;
  animation: chartIn 0.5s ease;

  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;

    h3 { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 2px; }
    .chart-sub { font-size: 12px; color: var(--text-tertiary); }
    .chart-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: var(--role-color);
      &.dot-cool { background: #06b6d4; }
      &.dot-usage { background: #8b5cf6; }
      &.dot-trend { background: #06b6d4; }
    }
  }
  .chart { height: 300px; }
}

@keyframes chartIn { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

.block-card {
  padding: 24px;
  animation: chartIn 0.5s ease;

  .block-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 2px; }
    .block-sub { font-size: 12px; color: var(--text-tertiary); }
  }
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;

  .title-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    &.pending { background: #f59e0b; }
    &.approved { background: #10b981; }
    &.rejected { background: #ef4444; }
    &.completed { background: #3b82f6; }
    &.cancelled { background: #9ca3af; }
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

.action-row {
  display: flex;
  gap: 8px;

  .action-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.3s;

    .el-icon { font-size: 14px; }

    &.approve {
      background: rgba(16, 185, 129, 0.1);
      color: #10b981;
      &:hover { background: #10b981; color: white; transform: scale(1.05); }
    }
    &.reject {
      background: rgba(var(--role-color-rgb), 0.1);
      color: var(--role-color);
      &:hover { background: var(--role-color); color: white; transform: scale(1.05); }
    }
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

@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .charts-grid { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
  .banner-stats { display: none; }
}
</style>
