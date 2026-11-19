<template>
  <div class="stat-card" :style="{ '--accent': color, '--accent-rgb': colorRgb }">
    <!-- 图标色块 -->
    <div class="stat-icon-block">
      <el-icon><component :is="icon" /></el-icon>
    </div>
    <!-- 数据信息 -->
    <div class="stat-info">
      <span class="stat-label">{{ label }}</span>
      <div class="stat-value-row">
        <span class="stat-value">{{ displayValue }}</span>
        <span class="stat-trend" v-if="trend" :class="trend > 0 ? 'up' : 'down'">
          <el-icon>
            <CaretTop v-if="trend > 0" />
            <CaretBottom v-else />
          </el-icon>
          <span>{{ Math.abs(trend) }}%</span>
        </span>
      </div>
      <span class="stat-sub" v-if="sub">{{ sub }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { CaretTop, CaretBottom } from '@element-plus/icons-vue'

const props = defineProps({
  label: String,
  value: [Number, String],
  icon: { type: String, default: 'DataLine' },
  color: { type: String, default: '#6366f1' },
  trend: { type: Number, default: 0 },
  sub: { type: String, default: '' }
})

const hover = ref(false)
const displayValue = ref(0)

// 将十六进制颜色转为 rgb 字符串
const colorRgb = computed(() => {
  const hex = props.color.replace('#', '')
  if (hex.length !== 6) return '99, 102, 241'
  const r = parseInt(hex.slice(0, 2), 16)
  const g = parseInt(hex.slice(2, 4), 16)
  const b = parseInt(hex.slice(4, 6), 16)
  return `${r}, ${g}, ${b}`
})

const animateValue = (to) => {
  const num = Number(to)
  if (isNaN(num)) {
    displayValue.value = to
    return
  }
  const duration = 1000
  const start = 0
  const startTime = performance.now()
  const step = (now) => {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    // easeOutCubic
    const eased = 1 - Math.pow(1 - progress, 3)
    displayValue.value = Math.round(start + (num - start) * eased)
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

watch(() => props.value, (v) => animateValue(v))

onMounted(() => {
  setTimeout(() => animateValue(props.value), 100)
})
</script>

<style lang="scss" scoped>
.stat-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
  position: relative;
  overflow: hidden;

  &:hover {
    box-shadow: var(--card-shadow-hover);
    border-color: var(--border-color-strong);
  }
}

// 图标色块 — 参考 Geeker-Admin 的设计
.stat-icon-block {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(var(--accent-rgb), 0.1);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;

  .stat-label {
    font-size: 13px;
    color: var(--text-tertiary);
    font-weight: 500;
    white-space: nowrap;
  }

  .stat-value-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-top: 2px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
  }

  .stat-trend {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;

    .el-icon { font-size: 12px; }

    &.up {
      color: #10b981;
      background: rgba(16, 185, 129, 0.1);
    }
    &.down {
      color: #ef4444;
      background: rgba(239, 68, 68, 0.1);
    }
  }

  .stat-sub {
    font-size: 11px;
    color: var(--text-quaternary);
    margin-top: 2px;
  }
}
</style>
