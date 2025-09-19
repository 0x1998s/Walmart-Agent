// 🛒 沃尔玛AI Agent平台 - 聊天界面
// Walmart AI Agent Platform - Chat Interface

import React, { useState, useEffect, useRef } from 'react'
import { 
  Layout, Input, Button, List, Avatar, Card, Select, Tag, 
  Spin, message, Divider, Tooltip, Space, Empty, Alert 
} from 'antd'
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  ClearOutlined,
  HistoryOutlined,
  ThunderboltOutlined,
  CopyOutlined
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from 'react-query'

import { api } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'

const { Content, Sider } = Layout
const { TextArea } = Input
const { Option } = Select

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  agent_id?: string
  agent_name?: string
  metadata?: any
}

interface Conversation {
  conversation_id: string
  messages: ChatMessage[]
  total_messages: number
  created_at: string
  updated_at: string
}

interface Agent {
  id: string
  name: string
  description: string
  is_active: boolean
}

const ChatInterface: React.FC = () => {
  const { user } = useAuthStore()
  const queryClient = useQueryClient()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const [currentMessage, setCurrentMessage] = useState('')
  const [selectedAgent, setSelectedAgent] = useState<string>()
  const [currentConversationId, setCurrentConversationId] = useState<string>()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isTyping, setIsTyping] = useState(false)

  // WebSocket连接
  const [ws, setWs] = useState<WebSocket | null>(null)

  // 获取可用Agent列表
  const { data: agents, isLoading: agentsLoading } = useQuery<Agent[]>(
    'agents',
    () => api.get('/agents'),
    {
      staleTime: 5 * 60 * 1000, // 5分钟
    }
  )

  // 获取对话历史
  const { data: conversations, isLoading: conversationsLoading } = useQuery<Conversation[]>(
    'conversations',
    () => api.get('/chat/conversations'),
    {
      staleTime: 2 * 60 * 1000, // 2分钟
    }
  )

  // 发送消息mutation
  const sendMessageMutation = useMutation(
    (messageData: {
      message: string
      conversation_id?: string
      preferred_agent_id?: string
    }) => api.post('/chat/message', messageData),
    {
      onSuccess: (response) => {
        const newMessage: ChatMessage = {
          id: response.id,
          role: 'assistant',
          content: response.message,
          timestamp: response.timestamp,
          agent_id: response.agent_id,
          agent_name: response.agent_name,
          metadata: response.metadata
        }
        
        setMessages(prev => [...prev, newMessage])
        setCurrentConversationId(response.conversation_id)
        setIsTyping(false)
        
        // 刷新对话列表
        queryClient.invalidateQueries('conversations')
      },
      onError: (error: any) => {
        message.error(`发送消息失败: ${error.message}`)
        setIsTyping(false)
      }
    }
  )

  // 初始化WebSocket连接
  useEffect(() => {
    if (user?.id) {
      const websocket = new WebSocket(`ws://localhost:8080/api/v1/ws/chat/${user.id}`)
      
      websocket.onopen = () => {
        console.log('WebSocket连接已建立')
        setWs(websocket)
      }
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.type === 'message') {
          const newMessage: ChatMessage = {
            id: data.data.message_id || Date.now().toString(),
            role: 'assistant',
            content: data.data.message,
            timestamp: data.timestamp,
            agent_id: data.data.agent_id,
            agent_name: data.data.agent_name,
            metadata: data.data.metadata
          }
          
          setMessages(prev => [...prev, newMessage])
          setIsTyping(false)
        } else if (data.type === 'status' && data.data.status === 'processing') {
          setIsTyping(true)
        }
      }
      
      websocket.onclose = () => {
        console.log('WebSocket连接已断开')
        setWs(null)
      }
      
      websocket.onerror = (error) => {
        console.error('WebSocket错误:', error)
        message.error('实时连接失败，将使用HTTP模式')
      }
      
      return () => {
        websocket.close()
      }
    }
  }, [user?.id])

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: currentMessage.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)

    // 优先使用WebSocket
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'chat',
        data: {
          message: currentMessage.trim(),
          conversation_id: currentConversationId,
          preferred_agent_id: selectedAgent
        }
      }))
    } else {
      // 使用HTTP API
      sendMessageMutation.mutate({
        message: currentMessage.trim(),
        conversation_id: currentConversationId,
        preferred_agent_id: selectedAgent
      })
    }

    setCurrentMessage('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const loadConversation = (conversation: Conversation) => {
    setMessages(conversation.messages)
    setCurrentConversationId(conversation.conversation_id)
  }

  const clearCurrentChat = () => {
    setMessages([])
    setCurrentConversationId(undefined)
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
    message.success('消息已复制到剪贴板')
  }

  const getSuggestions = () => [
    "分析Q4销售数据趋势",
    "查看库存周转率情况", 
    "生成客户行为分析报告",
    "预测下季度销售情况",
    "分析商品品类表现"
  ]

  return (
    <Layout style={{ height: '100vh' }}>
      {/* 侧边栏 - 对话历史 */}
      <Sider width={300} theme="light" style={{ borderRight: '1px solid #f0f0f0' }}>
        <div style={{ padding: '16px' }}>
          <h3>对话历史</h3>
          <Button 
            type="primary" 
            block 
            style={{ marginBottom: '16px' }}
            onClick={clearCurrentChat}
          >
            新建对话
          </Button>
          
          {conversationsLoading ? (
            <Spin />
          ) : conversations && conversations.length > 0 ? (
            <List
              dataSource={conversations}
              renderItem={(conversation) => (
                <List.Item
                  style={{ 
                    cursor: 'pointer',
                    backgroundColor: currentConversationId === conversation.conversation_id ? '#e6f7ff' : 'transparent'
                  }}
                  onClick={() => loadConversation(conversation)}
                >
                  <List.Item.Meta
                    avatar={<HistoryOutlined />}
                    title={`对话 ${conversation.conversation_id.slice(-8)}`}
                    description={`${conversation.total_messages} 条消息`}
                  />
                </List.Item>
              )}
            />
          ) : (
            <Empty description="暂无对话历史" />
          )}
        </div>
      </Sider>

      {/* 主聊天区域 */}
      <Layout>
        <Content style={{ display: 'flex', flexDirection: 'column' }}>
          {/* 聊天头部 */}
          <div style={{ 
            padding: '16px', 
            borderBottom: '1px solid #f0f0f0',
            backgroundColor: '#fafafa'
          }}>
            <Space>
              <span>选择Agent：</span>
              <Select
                style={{ width: 200 }}
                placeholder="自动选择最佳Agent"
                allowClear
                value={selectedAgent}
                onChange={setSelectedAgent}
                loading={agentsLoading}
              >
                {agents?.map(agent => (
                  <Option key={agent.id} value={agent.id} disabled={!agent.is_active}>
                    <Space>
                      <RobotOutlined style={{ color: agent.is_active ? '#52c41a' : '#d9d9d9' }} />
                      {agent.name}
                    </Space>
                  </Option>
                ))}
              </Select>
              
              <Tooltip title="清空当前对话">
                <Button icon={<ClearOutlined />} onClick={clearCurrentChat}>
                  清空
                </Button>
              </Tooltip>
            </Space>
          </div>

          {/* 消息列表 */}
          <div style={{ 
            flex: 1, 
            padding: '16px', 
            overflowY: 'auto',
            backgroundColor: '#f9f9f9'
          }}>
            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', marginTop: '100px' }}>
                <RobotOutlined style={{ fontSize: '64px', color: '#d9d9d9' }} />
                <h2 style={{ color: '#999', marginTop: '16px' }}>
                  欢迎使用沃尔玛AI Agent平台
                </h2>
                <p style={{ color: '#666' }}>
                  选择一个Agent开始对话，或者尝试以下建议：
                </p>
                <div style={{ marginTop: '24px' }}>
                  {getSuggestions().map((suggestion, index) => (
                    <Tag
                      key={index}
                      style={{ 
                        margin: '4px', 
                        cursor: 'pointer',
                        padding: '8px 12px',
                        fontSize: '14px'
                      }}
                      onClick={() => setCurrentMessage(suggestion)}
                    >
                      {suggestion}
                    </Tag>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg, index) => (
                  <div
                    key={msg.id}
                    style={{
                      display: 'flex',
                      justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      marginBottom: '16px'
                    }}
                  >
                    <div style={{ maxWidth: '70%' }}>
                      <Card
                        size="small"
                        style={{
                          backgroundColor: msg.role === 'user' ? '#1890ff' : '#fff',
                          color: msg.role === 'user' ? '#fff' : '#000',
                          borderRadius: '12px',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                        }}
                        bodyStyle={{ padding: '12px 16px' }}
                      >
                        <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                          <Avatar 
                            icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                            style={{ 
                              marginRight: '8px',
                              backgroundColor: msg.role === 'user' ? '#fff' : '#1890ff',
                              color: msg.role === 'user' ? '#1890ff' : '#fff'
                            }}
                            size="small"
                          />
                          <div style={{ flex: 1 }}>
                            <div style={{ marginBottom: '4px' }}>
                              <strong>
                                {msg.role === 'user' ? '我' : (msg.agent_name || 'AI助手')}
                              </strong>
                              <span style={{ 
                                marginLeft: '8px', 
                                fontSize: '12px', 
                                opacity: 0.7 
                              }}>
                                {new Date(msg.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                            <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                              {msg.content}
                            </div>
                            {msg.metadata?.chart_suggestions && (
                              <div style={{ marginTop: '8px' }}>
                                <Divider style={{ margin: '8px 0' }} />
                                <div style={{ fontSize: '12px', opacity: 0.8 }}>
                                  💡 建议图表：
                                  {msg.metadata.chart_suggestions.map((chart: any, i: number) => (
                                    <Tag key={i} style={{ margin: '2px', fontSize: '11px' }}>
                                      {chart.title}
                                    </Tag>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                          <Button
                            type="text"
                            size="small"
                            icon={<CopyOutlined />}
                            onClick={() => copyMessage(msg.content)}
                            style={{ 
                              marginLeft: '8px',
                              color: msg.role === 'user' ? '#fff' : '#666'
                            }}
                          />
                        </div>
                      </Card>
                    </div>
                  </div>
                ))}
                
                {isTyping && (
                  <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
                    <Card
                      size="small"
                      style={{
                        backgroundColor: '#fff',
                        borderRadius: '12px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                      }}
                      bodyStyle={{ padding: '12px 16px' }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar 
                          icon={<RobotOutlined />}
                          style={{ marginRight: '8px', backgroundColor: '#1890ff' }}
                          size="small"
                        />
                        <Spin size="small" />
                        <span style={{ marginLeft: '8px', color: '#666' }}>
                          AI正在思考中...
                        </span>
                      </div>
                    </Card>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* 输入区域 */}
          <div style={{ 
            padding: '16px', 
            borderTop: '1px solid #f0f0f0',
            backgroundColor: '#fff'
          }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <TextArea
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入您的问题... (Shift+Enter换行，Enter发送)"
                autoSize={{ minRows: 1, maxRows: 4 }}
                style={{ flex: 1 }}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSendMessage}
                disabled={!currentMessage.trim() || isTyping}
                style={{ height: 'auto' }}
              >
                发送
              </Button>
            </div>
            
            {/* 连接状态指示器 */}
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
              {ws && ws.readyState === WebSocket.OPEN ? (
                <span style={{ color: '#52c41a' }}>
                  <ThunderboltOutlined /> 实时连接已建立
                </span>
              ) : (
                <span style={{ color: '#faad14' }}>
                  <HistoryOutlined /> 使用HTTP模式
                </span>
              )}
            </div>
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

export default ChatInterface
