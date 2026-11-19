<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner glass-card">
      <div class="banner-content">
        <div class="banner-text">
          <h2>{{ greeting }}，{{ userStore.displayName }}</h2>
          <p>{{ dateStr }} · {{ weekStr }}</p>
        </div>
        <div class="banner-stats" v-if="stats.totalClassrooms !== undefined">
          <div class="quick-stat">
            <span class="qs-value">{{ stats.availableClassrooms || 0 }}</span>
            <span class="qs-label">可用</span>
          </div>
          <div class="divider"></div>
          <div class="quick-stat">
            <span class="qs-value warn">{{ stats.pendingApprovals || 0 }}</span>
            <span class="qs-label">待审</span>
          </div>
        </div>
      </div>
      <div class="banner-deco">
        <div class="ring"></div>
        <div class="ring ring-2"></div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div v-for="(card, i) in statCards" :key="card.label" :style="{ '--i': i }">
        <StatCard v-bind="card" />
      </div>
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

    <!-- 最近预约 -->
    <div class="recent-card glass-card">
      <div class="recent-header">
        <div>
          <h3>最近预约</h3>
          <span class="chart-sub">最新 5 条</span>
        </div>
        <el-button text type="primary" @click="$router.push('/reservations')">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <el-table
        :data="recentReservations"
        :loading="loading"
        stripe
        :row-class-name="rowClass"
      >
        <el-table-column prop="title" label="预约主题" min-width="160">
          <template #default="{ row }">
            <div class="title-cell">
              <span class="title-dot" :class="row.status?.toLowerCase()"></span>
              {{ row.title }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="classroomName" label="教室" width="120" />
        <el-table-column prop="userName" label="预约人" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span class="status-tag" :class="row.status?.toLowerCase()">
              {{ statusText(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="startTime" label="开始时间" width="180" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import StatCard from '@/components/StatCard.vue'
import { ArrowRight } from '@element-plus/icons-vue'
import { dashboardApi, reservationApi } from '@/api'
import { useUserStore } from '@/stores/user'

use([CanvasRenderer, PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const userStore = useUserStore()
const stats = reactive({})
const recentReservations = ref([])
const loading = ref(false)

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

const weekStr = computed(() => {
  const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return days[new Date().getDay()]
})

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

const statusText = (s) => ({
  PENDING: '待审批', APPROVED: '已通过', REJECTED: '已驳回',
  COMPLETED: '已完成', CANCELLED: '已取消'
}[s] || s)

const rowClass = ({ row, rowIndex }) => {
  return `row-${rowIndex}`
}

// 饼图 - 环形 + 渐变
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
      label: {
        show: true,
        fontSize: 14,
        fontWeight: 'bold',
        formatter: '{b}\n{c}'
      }
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

// 柱状图 - 渐变填充
const barOption = computed(() => {
  const colors = ['#10b981', '#f59e0b', '#9ca3af']
  return {
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
      itemStyle: {
        borderRadius: [8, 8, 0, 0]
      },
      animationDuration: 1200,
      animationEasing: 'cubicOut',
      data: [
        { value: stats.availableClassrooms || 0, itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#34d399' }, { offset: 1, color: '#10b981' }] } } },
        { value: stats.maintenanceClassrooms || 0, itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#fbbf24' }, { offset: 1, color: '#f59e0b' }] } } },
        { value: (stats.totalClassrooms || 0) - (stats.availableClassrooms || 0) - (stats.maintenanceClassrooms || 0), itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#cbd5e1' }, { offset: 1, color: '#94a3b8' }] } } }
      ]
    }]
  }
})

onMounted(async () => {
  loading.value = true
  try {
    const res = await dashboardApi.getStats()
    Object.assign(stats, res.data)
    const res2 = await reservationApi.getAll({ page: 1, pageSize: 5 })
    recentReservations.value = res2.data.list || []
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

// 欢迎横幅
.welcome-banner {
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.05));
  animation: bannerIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);

  .banner-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    z-index: 1;
  }

  .banner-text {
    h2 {
      font-size: 24px;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 4px;
      background: linear-gradient(135deg, #1e293b, #4f46e5);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    p {
      font-size: 14px;
      color: #64748b;
    }
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
        color: #6366f1;
        font-variant-numeric: tabular-nums;
        &.warn { color: #f59e0b; }
      }
      .qs-label {
        font-size: 12px;
        color: #94a3b8;
      }
    }
    .divider {
      width: 1px;
      height: 36px;
      background: rgba(148, 163, 184, 0.2);
    }
  }

  .banner-deco {
    position: absolute;
    right: -40px;
    top: -40px;
    width: 200px;
    height: 200px;

    .ring {
      position: absolute;
      inset: 0;
      border-radius: 50%;
      border: 2px solid rgba(99, 102, 241, 0.2);
      animation: ringRotate 15s linear infinite;
    }
    .ring-2 {
      inset: 30px;
      border-color: rgba(139, 92, 246, 0.15);
      animation-duration: 10s;
      animation-direction: reverse;
    }
  }
}

@keyframes bannerIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes ringRotate {
  to { transform: rotate(360deg); }
}

// 统计卡片网格
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;

  > div {
    animation: cardIn 0.5s var(--i) cubic-bezier(0.4, 0, 0.2, 1) both;
  }
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

// 图表
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-card {
  padding: 24px;
  animation: chartIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);

  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;

    h3 {
      font-size: 16px;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 2px;
    }
    .chart-sub {
      font-size: 11px;
      color: #94a3b8;
    }
    .chart-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #6366f1;
      box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
      animation: dotPulse 2s ease-in-out infinite;
      &.dot-cool {
        background: #06b6d4;
        box-shadow: 0 0 0 4px rgba(6, 182, 212, 0.15);
      }
    }
  }
  .chart { height: 300px; }
}

@keyframes chartIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes dotPulse {
  0%, 100% { box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15); }
  50% { box-shadow: 0 0 0 8px rgba(99, 102, 241, 0.05); }
}

// 最近预约
.recent-card {
  padding: 24px;
  animation: chartIn 0.7s cubic-bezier(0.4, 0, 0.2, 1);

  .recent-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      font-size: 16px;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 2px;
    }
    .chart-sub {
      font-size: 11px;
      color: #94a3b8;
    }
  }
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 8px;

  .title-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
    &.pending { background: #f59e0b; }
    &.approved { background: #10b981; }
    &.rejected { background: #ef4444; }
    &.completed { background: #3b82f6; }
    &.cancelled { background: #9ca3af; }
  }
}

.status-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;

  &.pending { background: rgba(245, 158, 11, 0.12); color: #f59e0b; }
  &.approved { background: rgba(16, 185, 129, 0.12); color: #10b981; }
  &.rejected { background: rgba(239, 68, 68, 0.12); color: #ef4444; }
  &.completed { background: rgba(59, 130, 246, 0.12); color: #3b82f6; }
  &.cancelled { background: rgba(156, 163, 175, 0.12); color: #9ca3af; }
}

// 表格行动画
:deep(.el-table__row) {
  animation: rowIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
}

@keyframes rowIn {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

// 响应式
@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .charts-grid { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
  .banner-stats { display: none; }
}
</style>
