import { beforeEach, afterEach, describe, it, expect, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useThemeStore, THEME_MODE } from '../theme'

/**
 * 主题持久化修复的单元测试
 *
 * 覆盖场景：
 * 1. 初始主题读取优先级（DOM > localStorage > 系统偏好）
 * 2. applyTheme 同步 DOM + localStorage
 * 3. toggleTheme 双向切换
 * 4. initTheme MutationObserver 防篡改
 * 5. localStorage 持久化（模拟页面刷新）
 */

describe('theme store - 初始主题读取', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    // 默认模拟系统浅色偏好
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.useRealTimers()
    document.documentElement.removeAttribute('data-theme')
  })

  it('DOM 属性存在时优先从 DOM 读取（模拟 index.html 内联脚本预设）', () => {
    document.documentElement.setAttribute('data-theme', 'dark')
    localStorage.setItem('theme-mode', 'light') // 即使 localStorage 是 light

    const store = useThemeStore()
    expect(store.mode).toBe('dark')
  })

  it('DOM 无属性时从 localStorage 读取', () => {
    localStorage.setItem('theme-mode', 'dark')

    const store = useThemeStore()
    expect(store.mode).toBe('dark')
  })

  it('DOM 和 localStorage 都无值时回退到系统浅色偏好', () => {
    const store = useThemeStore()
    expect(store.mode).toBe('light')
  })

  it('DOM 和 localStorage 都无值时回退到系统暗色偏好', () => {
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: true }))

    const store = useThemeStore()
    expect(store.mode).toBe('dark')
  })
})

describe('theme store - applyTheme', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('applyTheme 设置 DOM data-theme 属性', () => {
    const store = useThemeStore()
    store.applyTheme('dark')

    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })

  it('applyTheme 写入 localStorage', () => {
    const store = useThemeStore()
    store.applyTheme('dark')

    expect(localStorage.getItem('theme-mode')).toBe('dark')
  })

  it('applyTheme 更新 store.mode', () => {
    const store = useThemeStore()
    expect(store.mode).toBe('light')

    store.applyTheme('dark')
    expect(store.mode).toBe('dark')
  })
})

describe('theme store - toggleTheme', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('从 light 切换到 dark', () => {
    const store = useThemeStore()
    expect(store.isDark).toBe(false)

    store.toggleTheme()
    expect(store.isDark).toBe(true)
    expect(store.mode).toBe('dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })

  it('从 dark 切换到 light', () => {
    const store = useThemeStore()
    store.applyTheme('dark')
    expect(store.isDark).toBe(true)

    store.toggleTheme()
    expect(store.isDark).toBe(false)
    expect(store.mode).toBe('light')
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')
  })

  it('连续切换最终回到初始值', () => {
    const store = useThemeStore()
    const initial = store.mode

    store.toggleTheme()
    store.toggleTheme()

    expect(store.mode).toBe(initial)
  })
})

describe('theme store - initTheme MutationObserver 防篡改', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.useRealTimers()
  })

  it('initTheme 设置 MutationObserver 监听 data-theme 篡改', () => {
    const store = useThemeStore()
    store.applyTheme('dark')
    store.initTheme()

    // 模拟外部代码篡改 data-theme 为 light
    document.documentElement.setAttribute('data-theme', 'light')

    // MutationObserver 是异步的，需要等一个微任务
    return Promise.resolve().then(() => {
      // 观察器应检测到篡改并恢复为 store 的 dark
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
    })
  })

  it('initTheme 通过 setTimeout 延迟二次同步覆盖篡改', () => {
    const store = useThemeStore()
    store.applyTheme('dark')
    store.initTheme()

    // 模拟初始化阶段外部篡改
    document.documentElement.setAttribute('data-theme', 'light')

    // setTimeout(() => ..., 0) 应恢复正确主题
    vi.advanceTimersByTime(0)

    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })

  it('initTheme 通过 requestAnimationFrame 二次同步', () => {
    // requestAnimationFrame 在 fake timers 下需要手动触发
    let rafCallback = null
    vi.stubGlobal('requestAnimationFrame', (cb) => {
      rafCallback = cb
      return 1
    })

    const store = useThemeStore()
    store.applyTheme('dark')
    store.initTheme()

    // 模拟篡改
    document.documentElement.setAttribute('data-theme', 'light')

    // 触发 raf 回调
    if (rafCallback) rafCallback(performance.now())

    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')

    vi.unstubAllGlobals()
  })
})

describe('theme store - localStorage 持久化（模拟页面刷新）', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('dark 主题在模拟刷新后保持持久化', () => {
    // 第一次加载：设置 dark
    let store = useThemeStore()
    store.applyTheme('dark')
    expect(localStorage.getItem('theme-mode')).toBe('dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')

    // 模拟页面刷新：清除 DOM 属性（模拟内联脚本会从 localStorage 恢复）
    document.documentElement.setAttribute('data-theme', 'dark') // 内联脚本恢复

    // 重新创建 pinia + store（模拟刷新后重新初始化）
    setActivePinia(createPinia())
    store = useThemeStore()
    expect(store.mode).toBe('dark')
  })

  it('light 主题在模拟刷新后保持持久化', () => {
    let store = useThemeStore()
    store.applyTheme('light')
    expect(localStorage.getItem('theme-mode')).toBe('light')

    // 模拟刷新：内联脚本从 localStorage 恢复
    document.documentElement.setAttribute('data-theme', 'light')

    setActivePinia(createPinia())
    store = useThemeStore()
    expect(store.mode).toBe('light')
  })

  it('store.mode 与 DOM data-theme 在 initTheme 后保持一致', () => {
    const store = useThemeStore()
    store.applyTheme('dark')
    store.initTheme()

    expect(store.mode).toBe(document.documentElement.getAttribute('data-theme'))
  })
})

describe('theme store - getInitialTheme 非法值边界', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('DOM 属性为无效值时跳过 DOM 回退到 localStorage', () => {
    document.documentElement.setAttribute('data-theme', 'blue')
    localStorage.setItem('theme-mode', 'dark')

    const store = useThemeStore()
    expect(store.mode).toBe('dark')
  })

  it('DOM 属性为空串时跳过 DOM 回退到 localStorage', () => {
    document.documentElement.setAttribute('data-theme', '')
    localStorage.setItem('theme-mode', 'dark')

    const store = useThemeStore()
    expect(store.mode).toBe('dark')
  })

  it('DOM 为 light 但 localStorage 为 dark 时 DOM 优先', () => {
    document.documentElement.setAttribute('data-theme', 'light')
    localStorage.setItem('theme-mode', 'dark')

    const store = useThemeStore()
    expect(store.mode).toBe('light')
  })

  it('localStorage 值大小写不匹配时回退到系统偏好', () => {
    localStorage.setItem('theme-mode', 'Dark')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: true }))

    const store = useThemeStore()
    expect(store.mode).toBe('dark')
  })

  it('localStorage 值含空格时回退到系统偏好', () => {
    localStorage.setItem('theme-mode', ' dark ')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))

    const store = useThemeStore()
    expect(store.mode).toBe('light')
  })

  it('localStorage 值为 null（未设置）时回退到系统偏好', () => {
    const store = useThemeStore()
    expect(store.mode).toBe('light')
  })

  it('matchMedia 不存在时默认返回 light', () => {
    vi.stubGlobal('matchMedia', undefined)

    const store = useThemeStore()
    expect(store.mode).toBe('light')
  })

  it('matchMedia 调用抛错时默认返回 light', () => {
    vi.stubGlobal('matchMedia', vi.fn(() => {
      throw new Error('matchMedia not supported')
    }))

    const store = useThemeStore()
    expect(store.mode).toBe('light')
  })
})

describe('theme store - applyTheme 边界', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('applyTheme 连续调用以最后一次为准', () => {
    const store = useThemeStore()
    store.applyTheme('dark')
    store.applyTheme('light')
    store.applyTheme('dark')

    expect(store.mode).toBe('dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
    expect(localStorage.getItem('theme-mode')).toBe('dark')
  })

  it('applyTheme 幂等：重复设置相同值不产生副作用', () => {
    const store = useThemeStore()
    store.applyTheme('dark')
    const domBefore = document.documentElement.getAttribute('data-theme')
    const lsBefore = localStorage.getItem('theme-mode')

    store.applyTheme('dark')
    store.applyTheme('dark')

    expect(document.documentElement.getAttribute('data-theme')).toBe(domBefore)
    expect(localStorage.getItem('theme-mode')).toBe(lsBefore)
    expect(store.mode).toBe('dark')
  })

  it('applyTheme 用 light 覆盖已存的 dark', () => {
    const store = useThemeStore()
    store.applyTheme('dark')
    expect(localStorage.getItem('theme-mode')).toBe('dark')

    store.applyTheme('light')
    expect(localStorage.getItem('theme-mode')).toBe('light')
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')
  })

  it('applyTheme 用 dark 覆盖已存的 light', () => {
    const store = useThemeStore()
    store.applyTheme('light')
    expect(localStorage.getItem('theme-mode')).toBe('light')

    store.applyTheme('dark')
    expect(localStorage.getItem('theme-mode')).toBe('dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })
})

describe('theme store - toggleTheme 边界', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('快速连续切换奇数次后状态翻转', () => {
    const store = useThemeStore()
    const initial = store.mode

    for (let i = 0; i < 5; i++) store.toggleTheme()

    expect(store.mode).not.toBe(initial)
  })

  it('快速连续切换偶数次后状态不变', () => {
    const store = useThemeStore()
    const initial = store.mode

    for (let i = 0; i < 10; i++) store.toggleTheme()

    expect(store.mode).toBe(initial)
  })

  it('toggleTheme 在 initTheme 之前调用仍正常工作', () => {
    const store = useThemeStore()
    // 不调用 initTheme，直接 toggle
    store.toggleTheme()

    expect(store.mode).toBe('dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
    expect(localStorage.getItem('theme-mode')).toBe('dark')
  })

  it('toggleTheme 100 次后状态仍与初始一致', () => {
    const store = useThemeStore()
    const initial = store.mode

    for (let i = 0; i < 100; i++) store.toggleTheme()

    expect(store.mode).toBe(initial)
  })
})

describe('theme store - initTheme 边界', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.useRealTimers()
  })

  it('重复调用 initTheme 不报错且 observer 正常工作', () => {
    const store = useThemeStore()
    store.applyTheme('dark')

    expect(() => {
      store.initTheme()
      store.initTheme()
      store.initTheme()
    }).not.toThrow()

    // 最后一个 observer 仍能防篡改
    document.documentElement.setAttribute('data-theme', 'light')
    return Promise.resolve().then(() => {
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
    })
  })

  it('initTheme 对 light 主题同样具有防篡改能力', () => {
    const store = useThemeStore()
    store.applyTheme('light')
    store.initTheme()

    document.documentElement.setAttribute('data-theme', 'dark')

    return Promise.resolve().then(() => {
      expect(document.documentElement.getAttribute('data-theme')).toBe('light')
    })
  })

  it('连续多次外部篡改 observer 每次都能恢复', () => {
    const store = useThemeStore()
    store.applyTheme('dark')
    store.initTheme()

    // 第一次篡改
    document.documentElement.setAttribute('data-theme', 'light')
    return Promise.resolve()
      .then(() => {
        expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
        // 第二次篡改
        document.documentElement.setAttribute('data-theme', 'light')
      })
      .then(() => {
        expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
        // 第三次篡改
        document.documentElement.setAttribute('data-theme', 'light')
      })
      .then(() => {
        expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
      })
  })

  it('initTheme 后 store 自身 applyTheme 不被 observer 阻断', () => {
    const store = useThemeStore()
    store.applyTheme('light')
    store.initTheme()

    // store 自身切换主题，应正常生效
    store.applyTheme('dark')

    return Promise.resolve().then(() => {
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
      expect(store.mode).toBe('dark')
    })
  })

  it('initTheme 后 toggleTheme 正常工作', () => {
    const store = useThemeStore()
    store.initTheme()
    const before = store.mode

    store.toggleTheme()

    expect(store.mode).not.toBe(before)
    return Promise.resolve().then(() => {
      expect(document.documentElement.getAttribute('data-theme')).toBe(store.mode)
    })
  })
})

describe('theme store - localStorage 持久化边界', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('localStorage 为空串时回退到系统偏好', () => {
    localStorage.setItem('theme-mode', '')
    document.documentElement.removeAttribute('data-theme')

    const store = useThemeStore()
    expect(store.mode).toBe('light')
  })

  it('localStorage 值非法时刷新后降级到系统偏好', () => {
    localStorage.setItem('theme-mode', 'purple')
    document.documentElement.removeAttribute('data-theme')

    const store = useThemeStore()
    expect(store.mode).toBe('light')
  })

  it('localStorage 值非法且系统暗色时降级到 dark', () => {
    localStorage.setItem('theme-mode', 'invalid')
    document.documentElement.removeAttribute('data-theme')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: true }))

    const store = useThemeStore()
    expect(store.mode).toBe('dark')
  })

  it('多次连续刷新后主题仍然保持一致', () => {
    // 第一轮
    let store = useThemeStore()
    store.applyTheme('dark')

    // 模拟刷新 1
    document.documentElement.setAttribute('data-theme', 'dark')
    setActivePinia(createPinia())
    store = useThemeStore()
    expect(store.mode).toBe('dark')

    // 模拟刷新 2
    document.documentElement.setAttribute('data-theme', 'dark')
    setActivePinia(createPinia())
    store = useThemeStore()
    expect(store.mode).toBe('dark')

    // 模拟刷新 3
    document.documentElement.setAttribute('data-theme', 'dark')
    setActivePinia(createPinia())
    store = useThemeStore()
    expect(store.mode).toBe('dark')
  })

  it('切换主题后刷新保持新主题', () => {
    let store = useThemeStore()
    store.applyTheme('dark')
    store.toggleTheme() // 切到 light
    expect(store.mode).toBe('light')

    // 模拟刷新
    document.documentElement.setAttribute('data-theme', 'light')
    setActivePinia(createPinia())
    store = useThemeStore()
    expect(store.mode).toBe('light')
    expect(localStorage.getItem('theme-mode')).toBe('light')
  })
})

describe('theme store - isDark getter 边界', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({ matches: false }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('mode 为 dark 时 isDark 为 true', () => {
    document.documentElement.setAttribute('data-theme', 'dark')
    const store = useThemeStore()
    expect(store.isDark).toBe(true)
  })

  it('mode 为 light 时 isDark 为 false', () => {
    document.documentElement.setAttribute('data-theme', 'light')
    const store = useThemeStore()
    expect(store.isDark).toBe(false)
  })

  it('applyTheme 后 isDark 实时更新', () => {
    const store = useThemeStore()
    expect(store.isDark).toBe(false)

    store.applyTheme('dark')
    expect(store.isDark).toBe(true)

    store.applyTheme('light')
    expect(store.isDark).toBe(false)
  })
})

describe('theme store - THEME_MODE 常量', () => {
  it('导出 LIGHT 和 DARK 常量', () => {
    expect(THEME_MODE.LIGHT).toBe('light')
    expect(THEME_MODE.DARK).toBe('dark')
  })

  it('LIGHT 和 DARK 值互不相等', () => {
    expect(THEME_MODE.LIGHT).not.toBe(THEME_MODE.DARK)
  })
})
