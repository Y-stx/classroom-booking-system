<template>
  <div class="classroom-list">
    <!-- 筛选栏 -->
    <div class="filter-bar glass-card">
      <div class="filter-left">
        <el-input v-model="query.keyword" placeholder="搜索教室名称/楼栋" clearable style="width: 220px" @keyup.enter="loadData">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="query.type" placeholder="类型" clearable style="width: 140px" @change="loadData">
          <el-option label="多媒体教室" value="MULTIMEDIA" />
          <el-option label="机房" value="COMPUTER" />
          <el-option label="实验室" value="LAB" />
          <el-option label="普通教室" value="NORMAL" />
        </el-select>
        <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px" @change="loadData">
          <el-option label="可用" value="AVAILABLE" />
          <el-option label="维护中" value="MAINTENANCE" />
          <el-option label="停用" value="DISABLED" />
        </el-select>
        <el-input-number v-model="query.minCapacity" :min="1" :max="500" controls-position="right" placeholder="最小容量" style="width: 130px" @change="loadData">
          <template #prepend>≥</template>
        </el-input-number>
        <button class="btn-gradient" @click="loadData">
          <el-icon><Search /></el-icon>
          <span>查询</span>
        </button>
      </div>
      <div class="filter-right">
        <button class="quick-chip" :class="{ active: !query.status }" @click="query.status = ''; loadData()">全部</button>
        <button class="quick-chip" :class="{ active: query.status === 'AVAILABLE' }" @click="query.status = 'AVAILABLE'; loadData()">
          <span class="chip-dot green"></span>可用
        </button>
        <button class="quick-chip" :class="{ active: query.status === 'MAINTENANCE' }" @click="query.status = 'MAINTENANCE'; loadData()">
          <span class="chip-dot amber"></span>维护
        </button>
      </div>
    </div>

    <!-- 空闲教室时段查询 -->
    <div class="availability-bar glass-card">
      <div class="avail-left">
        <span class="avail-label"><el-icon><Clock /></el-icon> 按时段查空闲教室</span>
        <el-date-picker v-model="availRange" type="datetimerange" range-separator="至" start-placeholder="开始时间" end-placeholder="结束时间" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DD HH:mm:ss" style="width: 380px" />
        <button class="btn-gradient" @click="loadAvailable">
          <el-icon><Search /></el-icon>
          <span>查询空闲</span>
        </button>
      </div>
      <div class="avail-right" v-if="availMode">
        <el-tag type="success" effect="light" round>空闲时段：{{ availRange?.[0] }} ~ {{ availRange?.[1] }}</el-tag>
        <button class="btn-text" @click="exitAvailMode">返回全部</button>
      </div>
    </div>

    <!-- 教室卡片网格 -->
    <div class="card-grid" v-if="classrooms.length">
      <div
        v-for="(room, idx) in classrooms"
        :key="room.id"
        class="room-card glass-card"
        :class="[room.status?.toLowerCase(), typeColor(room.type)]"
        :style="{ '--i': idx }"
        @mousemove="onTilt"
        @mouseleave="resetTilt"
        @click="showDetail(room)"
      >
        <div class="room-image">
          <img :src="getRoomImage(room.type)" :alt="room.name" class="room-photo" />
          <div class="image-overlay"></div>
          <span class="room-status" :class="room.status?.toLowerCase()">
            <span class="status-dot"></span>{{ statusText(room.status) }}
          </span>
          <span class="room-type-badge">{{ typeText(room.type) }}</span>
        </div>
        <div class="room-info">
          <h3>{{ room.name }}</h3>
          <div class="info-row">
            <span><el-icon><Location /></el-icon> {{ room.building }} {{ room.floor }}层</span>
          </div>
          <div class="info-row">
            <el-icon><User /></el-icon>
            <div class="capacity-block">
              <span class="capacity-text">容纳 {{ room.capacity }} 人</span>
              <div class="capacity-bar">
                <div class="capacity-fill" :style="{ width: Math.min(room.capacity / 200 * 100, 100) + '%' }"></div>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <div class="equip-tags" v-if="room.equipment">
              <span
                v-for="(tag, ti) in parseEquipment(room.equipment)"
                :key="ti"
                class="equip-chip"
                :title="tag"
              >{{ tag }}</span>
            </div>
            <div class="equip-tags empty" v-else>
              <span class="equip-chip muted">暂无设施</span>
            </div>
            <button class="reserve-btn" v-if="room.status === 'AVAILABLE'">
              预约
              <el-icon><ArrowRight /></el-icon>
            </button>
            <span class="disabled-text" v-else>不可预约</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state glass-card" v-else>
      <el-icon class="empty-icon"><Box /></el-icon>
      <p>{{ availMode ? '该时段内暂无空闲教室' : '暂无符合条件的教室' }}</p>
      <button class="btn-text" @click="availMode ? exitAvailMode() : resetQuery()">重置筛选</button>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > query.pageSize">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadData"
      />
    </div>

    <!-- 预约弹窗 -->
    <el-dialog v-model="reserveVisible" title="预约教室" width="500px" class="reserve-dialog">
      <template #header>
        <div class="dialog-header">
          <el-icon class="dialog-icon"><Calendar /></el-icon>
          <div>
            <h3>预约教室</h3>
            <span>{{ currentRoom?.name }}</span>
          </div>
        </div>
      </template>
      <div class="dialog-info" v-if="currentRoom">
        <div class="info-block">
          <el-icon><Location /></el-icon>
          <span>{{ currentRoom.building }} {{ currentRoom.floor }}层</span>
        </div>
        <div class="info-block">
          <el-icon><User /></el-icon>
          <span>容纳 {{ currentRoom.capacity }} 人</span>
        </div>
        <div class="info-block">
          <el-icon><VideoCamera /></el-icon>
          <span>{{ typeText(currentRoom.type) }}</span>
        </div>
        <div class="info-block full" v-if="currentRoom.equipment">
          <el-icon><Monitor /></el-icon>
          <div class="equip-detail">
            <span class="equip-label">设施配备</span>
            <div class="equip-list">
              <span v-for="(tag, ti) in parseEquipment(currentRoom.equipment)" :key="ti" class="equip-badge">
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="主题" prop="title">
          <el-input v-model="form.title" placeholder="如：数据结构课程" />
        </el-form-item>
        <el-form-item label="目的">
          <el-input v-model="form.purpose" type="textarea" :rows="2" placeholder="请简要描述使用目的" />
        </el-form-item>
        <el-form-item label="开始时间" prop="startTime">
          <el-date-picker v-model="form.startTime" type="datetime" placeholder="选择开始时间" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" prop="endTime">
          <el-date-picker v-model="form.endTime" type="datetime" placeholder="选择结束时间" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="预计人数">
          <el-input-number v-model="form.attendees" :min="1" :max="500" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reserveVisible = false">取消</el-button>
        <button class="btn-gradient dialog-submit" @click="submitReserve">
          <span>提交预约</span>
          <el-icon><ArrowRight /></el-icon>
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search, Location, User, ArrowRight,
  VideoCamera, EditPen, Calendar, Box, Monitor, Clock
} from '@element-plus/icons-vue'
import { classroomApi, reservationApi } from '@/api'

const classrooms = ref([])
const total = ref(0)
const query = reactive({ keyword: '', type: '', status: '', minCapacity: null, page: 1, pageSize: 12 })
const reserveVisible = ref(false)
const currentRoom = ref(null)
const formRef = ref()

// 空闲教室时段查询
const availRange = ref([])
const availMode = ref(false)

const form = reactive({ title: '', purpose: '', startTime: '', endTime: '', attendees: 1 })
const rules = {
  title: [{ required: true, message: '请输入预约主题', trigger: 'blur' }],
  startTime: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  endTime: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

const statusText = (s) => ({ AVAILABLE: '可用', MAINTENANCE: '维护中', DISABLED: '停用' }[s] || s)
const typeText = (t) => ({ MULTIMEDIA: '多媒体', COMPUTER: '机房', LAB: '实验室', NORMAL: '普通' }[t] || t)
const typeColor = (t) => ({
  MULTIMEDIA: 'type-multimedia',
  COMPUTER: 'type-computer',
  LAB: 'type-lab',
  NORMAL: 'type-normal'
}[t] || '')

const parseEquipment = (eq) => {
  if (!eq) return []
  return eq.split(/[,，]/).map(s => s.trim()).filter(Boolean)
}

const getRoomImage = (type) => {
  const map = {
    LAB: '/images/classrooms/lab.jpg',
    MULTIMEDIA: '/images/classrooms/multimedia.jpg',
    COMPUTER: '/images/classrooms/computer.jpg',
    NORMAL: '/images/classrooms/normal.jpg'
  }
  return map[type] || '/images/classrooms/normal.jpg'
}

const loadData = async () => {
  try {
    const res = await classroomApi.getList(query)
    classrooms.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (e) {
    classrooms.value = []
    total.value = 0
  }
}

const loadAvailable = async () => {
  if (!availRange.value || availRange.value.length !== 2) {
    ElMessage.warning('请选择开始和结束时间')
    return
  }
  try {
    const res = await classroomApi.getAvailable(availRange.value[0], availRange.value[1])
    classrooms.value = res.data || []
    total.value = classrooms.value.length
    availMode.value = true
    if (classrooms.value.length === 0) {
      ElMessage.info('该时段内暂无空闲教室')
    } else {
      ElMessage.success(`找到 ${classrooms.value.length} 间空闲教室`)
    }
  } catch (e) {
    classrooms.value = []
    total.value = 0
  }
}

const exitAvailMode = () => {
  availMode.value = false
  availRange.value = []
  loadData()
}

const resetQuery = () => {
  Object.assign(query, { keyword: '', type: '', status: '', minCapacity: null, page: 1 })
  loadData()
}

const showDetail = (room) => {
  if (room.status !== 'AVAILABLE') {
    ElMessage.warning('该教室当前不可预约')
    return
  }
  currentRoom.value = room
  Object.assign(form, { title: '', purpose: '', startTime: '', endTime: '', attendees: 1 })
  reserveVisible.value = true
}

const submitReserve = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await reservationApi.create({ classroomId: currentRoom.value.id, ...form })
      ElMessage.success('预约提交成功，等待审批')
      reserveVisible.value = false
    } catch (e) { /* handled */ }
  })
}

// 3D 倾斜
const onTilt = (e) => {
  const card = e.currentTarget
  const rect = card.getBoundingClientRect()
  const x = (e.clientX - rect.left) / rect.width - 0.5
  const y = (e.clientY - rect.top) / rect.height - 0.5
  card.style.transform = `perspective(1000px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg) translateY(-6px)`
}
const resetTilt = (e) => {
  e.currentTarget.style.transform = ''
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.classroom-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

// 筛选栏
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px;
  animation: fadeIn 0.4s ease;

  .filter-left {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
  .filter-right {
    display: flex;
    gap: 8px;
  }
}

// 空闲教室时段查询栏
.availability-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 14px 16px;
  animation: fadeIn 0.4s ease;

  .avail-left {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }
  .avail-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary);
    white-space: nowrap;

    .el-icon { color: var(--role-primary, var(--primary)); }
  }
  .avail-right {
    display: flex;
    align-items: center;
    gap: 10px;
  }
}

// 卡片网格
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.room-card {
  padding: 0;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s;
  animation: cardSlide 0.5s calc(var(--i) * 0.05s) cubic-bezier(0.4, 0, 0.2, 1) both;
  transform-style: preserve-3d;
}

@keyframes cardSlide {
  from { opacity: 0; transform: translateY(30px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

// 教室图片区
.room-image {
  height: 160px;
  position: relative;
  overflow: hidden;
  background: #f1f5f9;

  .room-photo {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .image-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      to bottom,
      rgba(0, 0, 0, 0.25) 0%,
      rgba(0, 0, 0, 0) 40%,
      rgba(0, 0, 0, 0) 60%,
      rgba(0, 0, 0, 0.35) 100%
    );
    pointer-events: none;
  }
}

.room-card:hover .room-photo {
  transform: scale(1.06);
}

.room-status {
  position: absolute;
  top: 12px; right: 12px;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);

  .status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
  }

  &.available { color: #10b981; .status-dot { background: #10b981; } }
  &.maintenance { color: #f59e0b; .status-dot { background: #f59e0b; } }
  &.disabled { color: #9ca3af; .status-dot { background: #9ca3af; } }
}

.room-type-badge {
  position: absolute;
  bottom: 12px; left: 12px;
  z-index: 2;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: white;
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(8px);
}

// 教室信息
.room-info {
  padding: 20px;

  h3 {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 12px;
    transition: color 0.3s;
  }

  .info-row {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;

    .el-icon { font-size: 16px; color: var(--text-tertiary); flex-shrink: 0; }
  }

  .capacity-block {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;

    .capacity-text { font-size: 13px; }

    .capacity-bar {
      width: 100%;
      height: 4px;
      background: var(--border-color-subtle);
      border-radius: 2px;
      overflow: hidden;

      .capacity-fill {
        height: 100%;
        border-radius: 2px;
        background: #10b981;
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
      }
    }
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--border-color-subtle);
    gap: 12px;

    .equip-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      flex: 1;
      min-width: 0;

      &.empty {
        .equip-chip {
          color: var(--text-muted);
          background: transparent;
          border: 1px dashed var(--border-color);
        }
      }
    }

    .equip-chip {
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 4px;
      background: rgba(var(--role-rgb, 99, 102, 241), 0.06);
      color: var(--role-primary, var(--primary));
      font-weight: 500;
      line-height: 1.6;
      white-space: nowrap;
      max-width: 72px;
      overflow: hidden;
      text-overflow: ellipsis;

      &.muted {
        background: transparent;
        border: 1px dashed var(--border-color);
        color: var(--text-muted);
      }
    }

    .reserve-btn {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 6px 14px;
      background: rgba(var(--role-rgb, 99, 102, 241), 0.04);
      color: var(--primary);
      border: none;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s;

      .el-icon { font-size: 14px; }
    }

    .disabled-text {
      font-size: 13px;
      color: var(--text-muted);
    }
  }
}

.room-card:hover h3 {
  color: var(--primary);
}

// 对话框信息区
.dialog-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 14px;
  background: var(--bg-secondary, #f8fafc);
  border-radius: 10px;
  margin-bottom: 16px;

  .info-block {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--text-secondary);

    .el-icon {
      font-size: 16px;
      color: var(--role-primary, var(--primary));
      flex-shrink: 0;
    }

    &.full {
      grid-column: 1 / -1;
      flex-direction: column;
      align-items: flex-start;
      gap: 6px;

      .equip-detail {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
        width: 100%;
      }

      .equip-label {
        font-size: 12px;
        color: var(--text-tertiary);
        flex-shrink: 0;
      }

      .equip-list {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
      }

      .equip-badge {
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 5px;
        background: var(--role-primary, var(--primary));
        color: white;
        font-weight: 500;
        line-height: 1.4;
      }
    }
  }
}

// 对话框
.dialog-header {
  display: flex;
  align-items: center;
  gap: 12px;

  .dialog-icon {
    width: 40px; height: 40px;
    border-radius: 10px;
    background: var(--role-primary, var(--primary));
    color: white;
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  h3 { font-size: 16px; font-weight: 700; color: var(--text-primary); }
  span { font-size: 12px; color: var(--text-tertiary); }
}

.dialog-submit {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: var(--role-primary, var(--primary));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  &:hover { filter: brightness(0.96); }
}
</style>
