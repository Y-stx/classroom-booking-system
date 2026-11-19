import { defineStore } from 'pinia'

// 主题模式
export const THEME_MODE = {
  LIGHT: 'light',
  DARK: 'dark'
}

// 获取初始主题：优先读 DOM 属性（由 index.html 内联脚本预设），其次 localStorage，最后系统偏好
const getInitialTheme = () => {
  const domTheme = document.documentElement.getAttribute('data-theme')
  if (domTheme === 'light' || domTheme === 'dark') return domTheme
  const saved = localStorage.getItem('theme-mode')
  if (saved === 'light' || saved === 'dark') return saved
  try {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return THEME_MODE.DARK
    }
  } catch (e) {
    // matchMedia 不可用或抛错时回退到浅色
  }
  return THEME_MODE.LIGHT
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    mode: getInitialTheme(),
    _observer: null
  }),
  getters: {
    isDark: (state) => state.mode === THEME_MODE.DARK
  },
  actions: {
    // 应用主题到 DOM
    applyTheme(mode) {
      this.mode = mode
      document.documentElement.setAttribute('data-theme', mode)
      localStorage.setItem('theme-mode', mode)
    },
    // 切换主题
    toggleTheme() {
      const next = this.isDark ? THEME_MODE.LIGHT : THEME_MODE.DARK
      this.applyTheme(next)
    },
    // 初始化（页面加载时调用，确保 DOM 与 store 一致）
    initTheme() {
      this.applyTheme(this.mode)
      // 防御：监听 data-theme 被外部代码篡改时，自动同步回 store 的值
      if (this._observer) this._observer.disconnect()
      this._observer = new MutationObserver(() => {
        const current = document.documentElement.getAttribute('data-theme')
        if (current !== this.mode) {
          document.documentElement.setAttribute('data-theme', this.mode)
        }
      })
      this._observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
      // 延迟二次同步，覆盖外部代码在初始化阶段的篡改
      setTimeout(() => this.applyTheme(this.mode), 0)
      requestAnimationFrame(() => this.applyTheme(this.mode))
    }
  }
})
