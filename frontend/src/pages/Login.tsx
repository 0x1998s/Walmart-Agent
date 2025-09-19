// 🛒 沃尔玛AI Agent平台 - 登录页面
// Walmart AI Agent Platform - Login Page

import React, { useState } from 'react'
import { Form, Input, Button, Card, message, Spin } from 'antd'
import { UserOutlined, LockOutlined, EyeInvisibleOutlined, EyeTwoTone } from '@ant-design/icons'
import { useMutation } from 'react-query'

import { api } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'

interface LoginForm {
  username: string
  password: string
}

const Login: React.FC = () => {
  const { login } = useAuthStore()
  const [form] = Form.useForm()

  // 登录mutation
  const loginMutation = useMutation(
    (credentials: LoginForm) => api.post('/auth/login', credentials),
    {
      onSuccess: (response) => {
        const { access_token, refresh_token, user } = response
        
        login(access_token, refresh_token, {
          id: user.id,
          username: user.username,
          email: user.email,
          fullName: user.full_name,
          role: user.role,
          department: user.department,
          isActive: user.is_active,
          isSuperuser: user.is_superuser
        })
        
        message.success('登录成功！')
        
        // 跳转到仪表盘
        window.location.href = '/dashboard'
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
      }
    }
  )

  const handleLogin = (values: LoginForm) => {
    loginMutation.mutate(values)
  }

  // 演示账号登录
  const handleDemoLogin = () => {
    form.setFieldsValue({
      username: 'admin',
      password: 'walmart_admin_2024'
    })
    
    loginMutation.mutate({
      username: 'admin',
      password: 'walmart_admin_2024'
    })
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <Card
        style={{
          width: '100%',
          maxWidth: '400px',
          borderRadius: '12px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}
        bodyStyle={{ padding: '40px' }}
      >
        {/* Logo和标题 */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            fontSize: '48px',
            marginBottom: '16px'
          }}>
            🛒
          </div>
          <h1 style={{
            fontSize: '24px',
            fontWeight: 'bold',
            margin: 0,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            沃尔玛AI Agent平台
          </h1>
          <p style={{ color: '#666', margin: '8px 0 0 0' }}>
            企业级智能助手解决方案
          </p>
        </div>

        {/* 登录表单 */}
        <Form
          form={form}
          name="login"
          onFinish={handleLogin}
          layout="vertical"
          requiredMark={false}
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 2, message: '用户名至少2个字符' }
            ]}
          >
            <Input
              prefix={<UserOutlined style={{ color: '#1890ff' }} />}
              placeholder="用户名"
              size="large"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#1890ff' }} />}
              placeholder="密码"
              size="large"
              style={{ borderRadius: '8px' }}
              iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: '16px' }}>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              block
              loading={loginMutation.isLoading}
              style={{
                borderRadius: '8px',
                height: '48px',
                fontSize: '16px',
                fontWeight: 500,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none'
              }}
            >
              {loginMutation.isLoading ? <Spin size="small" /> : '登录'}
            </Button>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Button
              type="default"
              size="large"
              block
              onClick={handleDemoLogin}
              disabled={loginMutation.isLoading}
              style={{
                borderRadius: '8px',
                height: '48px',
                fontSize: '16px',
                borderColor: '#d9d9d9'
              }}
            >
              使用演示账号登录
            </Button>
          </Form.Item>
        </Form>

        {/* 底部信息 */}
        <div style={{
          textAlign: 'center',
          marginTop: '32px',
          padding: '16px',
          background: 'rgba(0, 0, 0, 0.02)',
          borderRadius: '8px',
          fontSize: '12px',
          color: '#666'
        }}>
          <div style={{ marginBottom: '8px' }}>
            <strong>演示账号信息：</strong>
          </div>
          <div>用户名: admin</div>
          <div>密码: walmart_admin_2024</div>
          <div style={{ marginTop: '8px', fontSize: '11px', opacity: 0.8 }}>
            * 演示环境，数据仅供测试使用
          </div>
        </div>

        {/* 版权信息 */}
        <div style={{
          textAlign: 'center',
          marginTop: '24px',
          fontSize: '12px',
          color: '#999'
        }}>
          <div>© 2024 沃尔玛AI Agent平台</div>
          <div>企业级智能助手解决方案</div>
        </div>
      </Card>
    </div>
  )
}

export default Login
