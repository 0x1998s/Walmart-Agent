// 🛒 沃尔玛AI Agent平台 - 主应用组件
// Walmart AI Agent Platform - Main App Component

import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ReactQueryDevtools } from 'react-query/devtools'

import Layout from '@/components/Layout'
import Dashboard from '@/pages/Dashboard'
import ChatInterface from '@/pages/ChatInterface'
import AgentManagement from '@/pages/AgentManagement'
import DocumentManagement from '@/pages/DocumentManagement'
import Analytics from '@/pages/Analytics'
import Settings from '@/pages/Settings'
import Login from '@/pages/Login'

import { useAuthStore } from '@/stores/authStore'
import { useThemeStore } from '@/stores/themeStore'

import './App.css'

// 创建React Query客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5分钟
    },
  },
})

const App: React.FC = () => {
  const { isAuthenticated } = useAuthStore()
  const { isDarkMode } = useThemeStore()

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        locale={zhCN}
        theme={{
          algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
          token: {
            colorPrimary: '#1890ff',
            colorSuccess: '#52c41a',
            colorWarning: '#faad14',
            colorError: '#f5222d',
            colorInfo: '#1890ff',
            borderRadius: 6,
            wireframe: false,
          },
          components: {
            Layout: {
              colorBgHeader: isDarkMode ? '#001529' : '#001529',
              colorBgBody: isDarkMode ? '#141414' : '#f0f2f5',
            },
            Menu: {
              colorBgContainer: isDarkMode ? '#001529' : '#001529',
              colorText: '#fff',
              colorItemTextSelected: '#1890ff',
            },
          },
        }}
      >
        <Router>
          <div className="App">
            {!isAuthenticated ? (
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="*" element={<Navigate to="/login" replace />} />
              </Routes>
            ) : (
              <Layout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/chat" element={<ChatInterface />} />
                  <Route path="/agents" element={<AgentManagement />} />
                  <Route path="/documents" element={<DocumentManagement />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </Layout>
            )}
          </div>
        </Router>
      </ConfigProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

export default App
