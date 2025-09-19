// 🛒 沃尔玛AI Agent平台 - 仪表盘页面
// Walmart AI Agent Platform - Dashboard Page

import React, { useState } from 'react'
import { Row, Col, Card, Statistic, Progress, Table, Tag, Button, Spin, Alert } from 'antd'
import {
  UserOutlined,
  RobotOutlined,
  MessageOutlined,
  BarChartOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { useQuery } from 'react-query'

import { api } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'

interface DashboardStats {
  totalAgents: number
  activeAgents: number
  totalMessages: number
  successRate: number
  averageResponseTime: number
  completedTasks: number
}

interface AgentStatus {
  id: string
  name: string
  status: string
  successRate: number
  responseTime: number
  currentTasks: number
}

const Dashboard = () => {
  const { user } = useAuthStore()
  const [timeRange, setTimeRange] = useState('24h')

  // 获取仪表盘统计数据
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery<DashboardStats>(
    ['dashboard-stats', timeRange],
    () => api.get(`/analytics/dashboard-stats?range=${timeRange}`),
    {
      refetchInterval: 30000, // 30秒刷新一次
    }
  )

  // 获取Agent状态
  const { data: agentStatuses, isLoading: agentsLoading } = useQuery<AgentStatus[]>(
    'agent-statuses',
    () => api.get('/agents/stats'),
    {
      refetchInterval: 10000, // 10秒刷新一次
    }
  )

  // 获取系统性能数据
  const { data: performanceData } = useQuery(
    ['performance-data', timeRange],
    () => api.get(`/analytics/performance?range=${timeRange}`),
    {
      refetchInterval: 60000, // 1分钟刷新一次
    }
  )

  const getResponseTimeChart = () => {
    return {
      title: {
        text: '响应时间趋势',
        left: 'center',
        textStyle: { fontSize: 16 }
      },
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}ms'
      },
      xAxis: {
        type: 'category',
        data: performanceData?.responseTime?.labels || []
      },
      yAxis: {
        type: 'value',
        name: '响应时间 (ms)'
      },
      series: [{
        data: performanceData?.responseTime?.values || [],
        type: 'line',
        smooth: true,
        itemStyle: { color: '#1890ff' },
        areaStyle: { opacity: 0.3 }
      }]
    }
  }

  const getSuccessRateChart = () => {
    return {
      title: {
        text: '成功率分布',
        left: 'center',
        textStyle: { fontSize: 16 }
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c}% ({d}%)'
      },
      series: [{
        name: '成功率',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '30',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: stats?.successRate || 0, name: '成功', itemStyle: { color: '#52c41a' } },
          { value: 100 - (stats?.successRate || 0), name: '失败', itemStyle: { color: '#f5222d' } }
        ]
      }]
    }
  }

  const agentColumns = [
    {
      title: 'Agent名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <span>
          <RobotOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          {text}
        </span>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const color = status === 'active' ? 'green' : 'red'
        const text = status === 'active' ? '运行中' : '已停止'
        return <Tag color={color}>{text}</Tag>
      }
    },
    {
      title: '成功率',
      dataIndex: 'successRate',
      key: 'successRate',
      render: (rate: number) => (
        <Progress 
          percent={Math.round(rate * 100)} 
          size="small" 
          status={rate > 0.8 ? 'success' : rate > 0.6 ? 'normal' : 'exception'}
        />
      )
    },
    {
      title: '平均响应时间',
      dataIndex: 'responseTime',
      key: 'responseTime',
      render: (time: number) => `${time.toFixed(2)}s`
    },
    {
      title: '当前任务',
      dataIndex: 'currentTasks',
      key: 'currentTasks',
      render: (count: number) => (
        <Tag color={count > 0 ? 'processing' : 'default'}>
          {count} 个任务
        </Tag>
      )
    }
  ]

  if (statsError) {
    return (
      <Alert
        message="数据加载失败"
        description="无法获取仪表盘数据，请检查网络连接或稍后重试。"
        type="error"
        showIcon
        style={{ margin: '20px' }}
      />
    )
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* 欢迎信息 */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ margin: 0, fontSize: '28px', fontWeight: 'bold' }}>
          🛒 沃尔玛AI Agent平台
        </h1>
        <p style={{ margin: '8px 0 0 0', color: '#666', fontSize: '16px' }}>
          欢迎回来，{user?.fullName || user?.username}！今天是 {new Date().toLocaleDateString('zh-CN')}
        </p>
      </div>

      {/* 核心指标卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="活跃Agent数量"
              value={statsLoading ? 0 : stats?.activeAgents}
              prefix={<RobotOutlined style={{ color: '#1890ff' }} />}
              loading={statsLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日消息处理"
              value={statsLoading ? 0 : stats?.totalMessages}
              prefix={<MessageOutlined style={{ color: '#52c41a' }} />}
              loading={statsLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="系统成功率"
              value={statsLoading ? 0 : stats?.successRate}
              suffix="%"
              prefix={<TrophyOutlined style={{ color: '#faad14' }} />}
              loading={statsLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均响应时间"
              value={statsLoading ? 0 : stats?.averageResponseTime}
              suffix="ms"
              prefix={<ClockCircleOutlined style={{ color: '#f5222d' }} />}
              loading={statsLoading}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="系统性能趋势" extra={
            <div>
              <Button 
                size="small" 
                type={timeRange === '1h' ? 'primary' : 'default'}
                onClick={() => setTimeRange('1h')}
              >
                1小时
              </Button>
              <Button 
                size="small" 
                type={timeRange === '24h' ? 'primary' : 'default'}
                onClick={() => setTimeRange('24h')}
                style={{ marginLeft: 8 }}
              >
                24小时
              </Button>
              <Button 
                size="small" 
                type={timeRange === '7d' ? 'primary' : 'default'}
                onClick={() => setTimeRange('7d')}
                style={{ marginLeft: 8 }}
              >
                7天
              </Button>
            </div>
          }>
            <ReactECharts 
              option={getResponseTimeChart()} 
              style={{ height: '300px' }}
              showLoading={!performanceData}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="任务成功率">
            <ReactECharts 
              option={getSuccessRateChart()} 
              style={{ height: '300px' }}
              showLoading={statsLoading}
            />
          </Card>
        </Col>
      </Row>

      {/* Agent状态表格 */}
      <Row>
        <Col span={24}>
          <Card 
            title="Agent状态监控" 
            extra={
              <Button 
                type="primary" 
                icon={<BarChartOutlined />}
                onClick={() => window.location.href = '/agents'}
              >
                管理Agent
              </Button>
            }
          >
            <Table
              columns={agentColumns}
              dataSource={agentStatuses}
              loading={agentsLoading}
              rowKey="id"
              pagination={{ pageSize: 10 }}
              size="middle"
            />
          </Card>
        </Col>
      </Row>

      {/* 系统健康状态 */}
      <Row style={{ marginTop: '24px' }}>
        <Col span={24}>
          <Card title="系统健康状态">
            <Row gutter={16}>
              <Col span={8}>
                <div style={{ textAlign: 'center', padding: '20px' }}>
                  <CheckCircleOutlined style={{ fontSize: '48px', color: '#52c41a' }} />
                  <h3>API服务</h3>
                  <p style={{ color: '#52c41a' }}>运行正常</p>
                </div>
              </Col>
              <Col span={8}>
                <div style={{ textAlign: 'center', padding: '20px' }}>
                  <CheckCircleOutlined style={{ fontSize: '48px', color: '#52c41a' }} />
                  <h3>数据库</h3>
                  <p style={{ color: '#52c41a' }}>连接正常</p>
                </div>
              </Col>
              <Col span={8}>
                <div style={{ textAlign: 'center', padding: '20px' }}>
                  <ExclamationCircleOutlined style={{ fontSize: '48px', color: '#faad14' }} />
                  <h3>向量数据库</h3>
                  <p style={{ color: '#faad14' }}>部分功能异常</p>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
