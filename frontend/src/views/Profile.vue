<template>
  <div class="profile-page">
    <!-- 资料卡 -->
    <div class="profile-card glass-card">
      <div class="profile-header">
        <div class="avatar-wrap">
          <div class="avatar">{{ userStore.displayName.charAt(0) }}</div>
          <span class="avatar-ring"></span>
          <span class="avatar-ring avatar-ring-2"></span>
        </div>
        <div class="header-info">
          <h2>{{ userStore.displayName }}</h2>
          <span class="role-tag" :class="userStore.role?.toLowerCase()">{{ roleText }}</span>
        </div>
      </div>

      <el-form :model="form" label-width="100px" class="profile-form">
        <el-form-item label="用户名">
          <el-input :value="form.username" disabled />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="院系">
          <el-input v-model="form.department" placeholder="请输入院系" />
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item>
          <button class="btn-gradient" @click="saveProfile">
            <el-icon><Check /></el-icon>
            <span>保存修改</span>
          </button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 密码卡 -->
    <div class="pwd-card glass-card">
      <div class="card-title">
        <div class="title-icon">
          <el-icon><Lock /></el-icon>
        </div>
        <div>
          <h3>修改密码</h3>
          <span>定期更换以保障账户安全</span>
        </div>
      </div>
      <el-form :model="pwdForm" label-width="100px">
        <el-form-item label="旧密码">
          <el-input v-model="pwdForm.oldPassword" type="password" show-password placeholder="请输入当前密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.newPassword" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="pwdForm.confirm" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
        <el-form-item>
          <button class="btn-gradient" @click="changePassword">
            <el-icon><Check /></el-icon>
            <span>修改密码</span>
          </button>
        </el-form-item>
      </el-form>

      <!-- 安全提示 -->
      <div class="security-tip">
        <el-icon><InfoFilled /></el-icon>
        <div>
          <p>建议密码包含：</p>
          <ul>
            <li>至少 8 位字符</li>
            <li>字母、数字组合</li>
            <li>避免使用常见密码</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Lock, InfoFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { userApi } from '@/api'

const userStore = useUserStore()
const form = reactive({})
const pwdForm = reactive({ oldPassword: '', newPassword: '', confirm: '' })

const roleText = computed(() => ({ ADMIN: '管理员', TEACHER: '教师', STUDENT: '学生' }[userStore.role] || ''))

const loadProfile = async () => {
  await userStore.fetchUserInfo()
  Object.assign(form, userStore.user)
}

const saveProfile = async () => {
  try {
    await userApi.update(form.id, form)
    ElMessage.success('保存成功')
    await userStore.fetchUserInfo()
  } catch (e) { /* handled */ }
}

const changePassword = async () => {
  if (!pwdForm.oldPassword || !pwdForm.newPassword) {
    ElMessage.warning('请填写完整')
    return
  }
  if (pwdForm.newPassword !== pwdForm.confirm) {
    ElMessage.warning('两次密码不一致')
    return
  }
  try {
    await userApi.updatePassword(pwdForm.oldPassword, pwdForm.newPassword)
    ElMessage.success('密码修改成功')
    Object.assign(pwdForm, { oldPassword: '', newPassword: '', confirm: '' })
  } catch (e) { /* handled */ }
}

onMounted(loadProfile)
</script>

<style lang="scss" scoped>
.profile-page {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

.profile-card, .pwd-card {
  padding: 32px;
  animation: cardIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);

  .avatar-wrap {
    position: relative;
    width: 72px;
    height: 72px;
  }

  .avatar {
    width: 72px; height: 72px;
    border-radius: 50%;
    background: var(--role-primary, #6366f1);
    color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 30px; font-weight: 700;
    position: relative;
    z-index: 1;
  }

  .avatar-ring {
    position: absolute;
    inset: -5px;
    border-radius: 50%;
    border: 1px solid rgba(99, 102, 241, 0.25);
  }
  .avatar-ring-2 { display: none; }

  h2 {
    font-size: 22px;
    font-weight: 700;
    color: var(--role-primary, #6366f1);
    margin-bottom: 8px;
  }

  .role-tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;

    &.admin { background: rgba(99, 102, 241, 0.15); color: #6366f1; }
    &.teacher { background: rgba(16, 185, 129, 0.15); color: #10b981; }
    &.student { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
  }
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;

  .title-icon {
    width: 40px; height: 40px;
    border-radius: 10px;
    background: var(--role-primary, #6366f1);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
  }
  h3 { font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 2px; }
  span { font-size: 12px; color: #94a3b8; }
}

.btn-gradient {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 24px;
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

.security-tip {
  display: flex;
  gap: 10px;
  padding: 16px;
  background: rgba(99, 102, 241, 0.05);
  border-radius: 10px;
  margin-top: 20px;

  .el-icon {
    color: #6366f1;
    font-size: 18px;
    flex-shrink: 0;
    margin-top: 2px;
  }

  p {
    font-size: 13px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 4px;
  }
  ul {
    padding-left: 16px;
    li {
      font-size: 12px;
      color: #64748b;
      line-height: 1.6;
    }
  }
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .profile-page { grid-template-columns: 1fr; }
}
</style>
