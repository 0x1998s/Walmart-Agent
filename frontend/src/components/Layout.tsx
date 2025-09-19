// 🛒 沃尔玛AI Agent平台 - 布局组件
// Walmart AI Agent Platform - Layout Component

import React, { useState } from 'react'
import { Layout as AntLayout, Menu, Avatar, Dropdown, Button, Badge, Tooltip } from 'antd'
import {
  DashboardOutlined,
  MessageOutlined,
  RobotOutlined,
  FileTextOutlined,
  BarChartOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BellOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons'
import { useLocation, useNavigate } from 'react-router-dom'

import { useAuthStore } from '@/stores/authStore'
import { useThemeStore } from '@/stores/themeStore'

const { Header, Sider, Content } = AntLayout

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { sidebarCollapsed, toggleSidebar, isDarkMode, toggleDarkMode } = useThemeStore()
  
  const [notifications] = useState(3) // 模拟通知数量

  // 菜单项配置
  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: '智能对话',
    },
    {
      key: '/agents',
      icon: <RobotOutlined />,
      label: 'Agent管理',
    },
    {
      key: '/documents',
      icon: <FileTextOutlined />,
      label: '文档管理',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: '数据分析',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ]

  // 用户下拉菜单
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
      onClick: () => navigate('/profile')
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
      onClick: () => navigate('/settings')
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: () => {
        logout()
        navigate('/login')
      }
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      {/* 侧边栏 */}
      <Sider
        trigger={null}
        collapsible
        collapsed={sidebarCollapsed}
        width={240}
        theme="dark"
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
        }}
      >
        {/* Logo */}
        <div style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: sidebarCollapsed ? 'center' : 'flex-start',
          padding: sidebarCollapsed ? '0' : '0 24px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}>
          <div style={{
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            🛒
            {!sidebarCollapsed && <span>沃尔玛AI Agent</span>}
          </div>
        </div>

        {/* 菜单 */}
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ borderRight: 0, marginTop: '8px' }}
        />

        {/* 底部信息 */}
        {!sidebarCollapsed && (
          <div style={{
            position: 'absolute',
            bottom: '16px',
            left: '16px',
            right: '16px',
            padding: '12px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '8px',
            fontSize: '12px',
            color: 'rgba(255, 255, 255, 0.7)',
            textAlign: 'center'
          }}>
            <div>版本 v1.0.0</div>
            <div>企业级AI Agent平台</div>
          </div>
        )}
      </Sider>

      {/* 主内容区域 */}
      <AntLayout style={{ marginLeft: sidebarCollapsed ? 80 : 240 }}>
        {/* 顶部导航栏 */}
        <Header style={{
          padding: '0 24px',
          background: '#fff',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 99,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)'
        }}>
          {/* 左侧控制 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Button
              type="text"
              icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={toggleSidebar}
              style={{ fontSize: '16px', width: 40, height: 40 }}
            />
            
            {/* 面包屑导航 */}
            <div style={{ fontSize: '16px', fontWeight: 500, color: '#262626' }}>
              {menuItems.find(item => item.key === location.pathname)?.label || '页面'}
            </div>
          </div>

          {/* 右侧控制 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* 通知 */}
            <Tooltip title="通知">
              <Badge count={notifications} size="small">
                <Button
                  type="text"
                  icon={<BellOutlined />}
                  style={{ fontSize: '16px', width: 40, height: 40 }}
                />
              </Badge>
            </Tooltip>

            {/* 帮助 */}
            <Tooltip title="帮助">
              <Button
                type="text"
                icon={<QuestionCircleOutlined />}
                style={{ fontSize: '16px', width: 40, height: 40 }}
                onClick={() => window.open('/api/v1/docs', '_blank')}
              />
            </Tooltip>

            {/* 主题切换 */}
            <Tooltip title={isDarkMode ? '切换到浅色模式' : '切换到深色模式'}>
              <Button
                type="text"
                onClick={toggleDarkMode}
                style={{ fontSize: '16px', width: 40, height: 40 }}
              >
                {isDarkMode ? '🌞' : '🌙'}
              </Button>
            </Tooltip>

            {/* 用户信息 */}
            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              trigger={['click']}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                cursor: 'pointer',
                padding: '8px 12px',
                borderRadius: '8px',
                transition: 'background-color 0.3s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f5f5f5'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent'
              }}
              >
                <Avatar
                  size="small"
                  icon={<UserOutlined />}
                  style={{ backgroundColor: '#1890ff' }}
                />
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  <span style={{ fontSize: '14px', fontWeight: 500, lineHeight: 1.2 }}>
                    {user?.fullName || user?.username}
                  </span>
                  <span style={{ fontSize: '12px', color: '#666', lineHeight: 1.2 }}>
                    {user?.role === 'admin' ? '管理员' : '用户'}
                  </span>
                </div>
              </div>
            </Dropdown>
          </div>
        </Header>

        {/* 页面内容 */}
        <Content style={{
          margin: 0,
          minHeight: 'calc(100vh - 64px)',
          background: '#f0f2f5',
          overflow: 'auto'
        }}>
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  )
}

export default Layout
