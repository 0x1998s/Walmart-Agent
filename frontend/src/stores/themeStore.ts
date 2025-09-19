// 🛒 沃尔玛AI Agent平台 - 主题状态管理
// Walmart AI Agent Platform - Theme Store

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ThemeState {
  isDarkMode: boolean
  primaryColor: string
  language: 'zh-CN' | 'en-US'
  sidebarCollapsed: boolean
  compactMode: boolean
}

interface ThemeActions {
  toggleDarkMode: () => void
  setPrimaryColor: (color: string) => void
  setLanguage: (language: 'zh-CN' | 'en-US') => void
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  toggleCompactMode: () => void
  resetTheme: () => void
}

type ThemeStore = ThemeState & ThemeActions

const initialState: ThemeState = {
  isDarkMode: false,
  primaryColor: '#1890ff',
  language: 'zh-CN',
  sidebarCollapsed: false,
  compactMode: false,
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      toggleDarkMode: () => {
        const newDarkMode = !get().isDarkMode
        set({ isDarkMode: newDarkMode })
        
        // 更新HTML根元素的data-theme属性
        document.documentElement.setAttribute(
          'data-theme',
          newDarkMode ? 'dark' : 'light'
        )
      },

      setPrimaryColor: (color: string) => {
        set({ primaryColor: color })
        
        // 更新CSS变量
        document.documentElement.style.setProperty('--primary-color', color)
      },

      setLanguage: (language: 'zh-CN' | 'en-US') => {
        set({ language })
        
        // 更新HTML lang属性
        document.documentElement.lang = language === 'zh-CN' ? 'zh-CN' : 'en-US'
      },

      toggleSidebar: () => {
        set({ sidebarCollapsed: !get().sidebarCollapsed })
      },

      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed })
      },

      toggleCompactMode: () => {
        set({ compactMode: !get().compactMode })
      },

      resetTheme: () => {
        set({ ...initialState })
        
        // 重置HTML属性
        document.documentElement.setAttribute('data-theme', 'light')
        document.documentElement.lang = 'zh-CN'
        document.documentElement.style.removeProperty('--primary-color')
      },
    }),
    {
      name: 'theme-storage',
      onRehydrateStorage: () => (state) => {
        if (state) {
          // 应用持久化的主题设置
          document.documentElement.setAttribute(
            'data-theme',
            state.isDarkMode ? 'dark' : 'light'
          )
          document.documentElement.lang = state.language === 'zh-CN' ? 'zh-CN' : 'en-US'
          if (state.primaryColor !== initialState.primaryColor) {
            document.documentElement.style.setProperty('--primary-color', state.primaryColor)
          }
        }
      },
    }
  )
)
