import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Progress, Table, Tag, Badge, message } from 'antd'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { DatabaseOutlined, VideoCameraOutlined, UserOutlined, ScheduleOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'

// 模拟数据
const mockChannelData = [
  { name: '央视综合', status: 'online', viewers: 1200, quality: '高清' },
  { name: '央视新闻', status: 'online', viewers: 980, quality: '高清' },
  { name: '湖南卫视', status: 'offline', viewers: 0, quality: '标清' },
  { name: '江苏卫视', status: 'online', viewers: 750, quality: '高清' },
  { name: '浙江卫视', status: 'online', viewers: 620, quality: '高清' }
]

// 模拟流量数据
const mockTrafficData = [
  { name: '1月', value: 400 },
  { name: '2月', value: 300 },
  { name: '3月', value: 500 },
  { name: '4月', value: 600 },
  { name: '5月', value: 700 },
  { name: '6月', value: 800 },
  { name: '7月', value: 900 }
]

const Dashboard = () => {
  const [systemStats, setSystemStats] = useState({
    totalChannels: 120,
    onlineChannels: 105,
    totalUsers: 50,
    scheduledTasks: 20
  })

  const [recentActivities, setRecentActivities] = useState([
    { id: 1, action: '添加新频道', channel: '央视体育', time: '2026-02-22 10:30', status: 'success' },
    { id: 2, action: '更新数据源', source: 'IPTV源1', time: '2026-02-22 09:15', status: 'success' },
    { id: 3, action: '系统维护', message: '数据库备份', time: '2026-02-21 23:00', status: 'success' },
    { id: 4, action: '添加新频道', channel: '东方卫视', time: '2026-02-21 16:45', status: 'failed' }
  ])

  useEffect(() => {
    // 模拟获取系统统计数据
    // 实际项目中应该调用真实的API
    setTimeout(() => {
      message.info('系统数据已更新')
    }, 1000)
  }, [])

  return (
    <div className="dashboard-container">
      <h1>系统仪表盘</h1>
      
      {/* 系统概览卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="总频道数" 
              value={systemStats.totalChannels} 
              prefix={<VideoCameraOutlined />}
              suffix="个"
            />
            <Progress 
              percent={(systemStats.onlineChannels / systemStats.totalChannels) * 100} 
              status="active" 
              style={{ marginTop: 16 }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="在线频道" 
              value={systemStats.onlineChannels} 
              prefix={<CheckCircleOutlined />}
              suffix="个"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="总用户数" 
              value={systemStats.totalUsers} 
              prefix={<UserOutlined />}
              suffix="人"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="定时任务" 
              value={systemStats.scheduledTasks} 
              prefix={<ScheduleOutlined />}
              suffix="个"
            />
          </Card>
        </Col>
      </Row>

      {/* 数据统计和频道状态 */}
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="系统流量趋势" style={{ height: 400 }}>
            <ResponsiveContainer width="100%" height="80%">
              <AreaChart data={mockTrafficData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" />
                <YAxis />
                <CartesianGrid strokeDasharray="3 3" />
                <Tooltip />
                <Area type="monotone" dataKey="value" stroke="#8884d8" fillOpacity={1} fill="url(#colorValue)" />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="频道状态" style={{ height: 400, overflow: 'auto' }}>
            <Table 
              dataSource={mockChannelData} 
              columns={[
                {
                  title: '频道名称',
                  dataIndex: 'name',
                  key: 'name'
                },
                {
                  title: '状态',
                  dataIndex: 'status',
                  key: 'status',
                  render: (status) => (
                    <Tag color={status === 'online' ? 'green' : 'red'}>
                      {status === 'online' ? '在线' : '离线'}
                    </Tag>
                  )
                },
                {
                  title: '观看人数',
                  dataIndex: 'viewers',
                  key: 'viewers'
                },
                {
                  title: '画质',
                  dataIndex: 'quality',
                  key: 'quality',
                  render: (quality) => (
                    <Badge status="success" text={quality} />
                  )
                }
              ]}
              pagination={false}
            />
          </Card>
        </Col>
      </Row>

      {/* 最近活动 */}
      <Card title="最近活动" style={{ marginTop: 16 }}>
        <Table 
          dataSource={recentActivities} 
          columns={[
            {
              title: '操作',
              dataIndex: 'action',
              key: 'action'
            },
            {
              title: '详情',
              dataIndex: 'channel',
              key: 'detail',
              render: (channel, record) => (
                <span>{channel || record.source || record.message || '-'}</span>
              )
            },
            {
              title: '时间',
              dataIndex: 'time',
              key: 'time'
            },
            {
              title: '状态',
              dataIndex: 'status',
              key: 'status',
              render: (status) => (
                <Tag color={status === 'success' ? 'green' : 'red'}>
                  {status === 'success' ? '成功' : '失败'}
                </Tag>
              )
            }
          ]}
          pagination={{ pageSize: 5 }}
        />
      </Card>
    </div>
  )
}

export default Dashboard
