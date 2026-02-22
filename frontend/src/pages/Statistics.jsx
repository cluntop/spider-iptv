import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Select, DatePicker, Button, Space, Statistic, Progress } from 'antd'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, RadarChart, Radar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Cell
} from 'recharts'
import { 
  AreaChartOutlined, 
  BarChartOutlined, 
  PieChartOutlined, 
  RadarChartOutlined, 
  CalendarOutlined,
  ReloadOutlined
} from '@ant-design/icons'

const { Option } = Select
const { RangePicker } = DatePicker

// 模拟系统运行数据
const mockSystemData = {
  cpu: [
    { time: '00:00', value: 30 },
    { time: '02:00', value: 25 },
    { time: '04:00', value: 20 },
    { time: '06:00', value: 40 },
    { time: '08:00', value: 60 },
    { time: '10:00', value: 70 },
    { time: '12:00', value: 50 },
    { time: '14:00', value: 65 },
    { time: '16:00', value: 75 },
    { time: '18:00', value: 80 },
    { time: '20:00', value: 60 },
    { time: '22:00', value: 40 }
  ],
  memory: [
    { time: '00:00', value: 45 },
    { time: '02:00', value: 40 },
    { time: '04:00', value: 35 },
    { time: '06:00', value: 50 },
    { time: '08:00', value: 65 },
    { time: '10:00', value: 70 },
    { time: '12:00', value: 60 },
    { time: '14:00', value: 65 },
    { time: '16:00', value: 75 },
    { time: '18:00', value: 80 },
    { time: '20:00', value: 70 },
    { time: '22:00', value: 55 }
  ],
  network: [
    { time: '00:00', upload: 10, download: 20 },
    { time: '02:00', upload: 5, download: 15 },
    { time: '04:00', upload: 3, download: 10 },
    { time: '06:00', upload: 15, download: 30 },
    { time: '08:00', upload: 25, download: 50 },
    { time: '10:00', upload: 30, download: 60 },
    { time: '12:00', upload: 20, download: 40 },
    { time: '14:00', upload: 25, download: 55 },
    { time: '16:00', upload: 35, download: 70 },
    { time: '18:00', upload: 40, download: 80 },
    { time: '20:00', upload: 25, download: 50 },
    { time: '22:00', upload: 15, download: 30 }
  ],
  channels: [
    { name: '央视综合', value: 1200 },
    { name: '央视新闻', value: 980 },
    { name: '湖南卫视', value: 850 },
    { name: '江苏卫视', value: 750 },
    { name: '浙江卫视', value: 620 },
    { name: '东方卫视', value: 580 }
  ],
  users: [
    { date: '1月', new: 20, active: 150 },
    { date: '2月', new: 35, active: 180 },
    { date: '3月', new: 45, active: 210 },
    { date: '4月', new: 30, active: 190 },
    { date: '5月', new: 50, active: 230 },
    { date: '6月', new: 65, active: 260 },
    { date: '7月', new: 80, active: 290 }
  ],
  systemHealth: [
    { subject: 'CPU', A: 80, fullMark: 100 },
    { subject: '内存', A: 70, fullMark: 100 },
    { subject: '磁盘', A: 60, fullMark: 100 },
    { subject: '网络', A: 90, fullMark: 100 },
    { subject: '服务', A: 85, fullMark: 100 },
    { subject: '数据库', A: 75, fullMark: 100 }
  ]
}

// 颜色配置
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']

const Statistics = () => {
  const [timeRange, setTimeRange] = useState(['7d'])
  const [dateRange, setDateRange] = useState(null)
  const [systemData, setSystemData] = useState(mockSystemData)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // 模拟获取统计数据
    // 实际项目中应该调用真实的API
    setTimeout(() => {
      setLoading(false)
    }, 1000)
  }, [timeRange, dateRange])

  // 刷新数据
  const handleRefresh = () => {
    setLoading(true)
    // 模拟刷新数据
    setTimeout(() => {
      // 随机生成一些新数据
      const newCpuData = mockSystemData.cpu.map(item => ({
        ...item,
        value: Math.floor(Math.random() * 50) + 30
      }))
      
      const newMemoryData = mockSystemData.memory.map(item => ({
        ...item,
        value: Math.floor(Math.random() * 40) + 40
      }))
      
      setSystemData({
        ...systemData,
        cpu: newCpuData,
        memory: newMemoryData
      })
      
      setLoading(false)
    }, 1000)
  }

  return (
    <div className="statistics-container">
      <h1>统计分析</h1>
      
      {/* 时间范围选择 */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Select
              value={timeRange}
              onChange={setTimeRange}
              style={{ width: 120 }}
            >
              <Option value="24h">最近24小时</Option>
              <Option value="7d">最近7天</Option>
              <Option value="30d">最近30天</Option>
              <Option value="90d">最近90天</Option>
            </Select>
            <RangePicker onChange={setDateRange} />
          </Space>
          
          <Button icon={<ReloadOutlined />} loading={loading} onClick={handleRefresh}>
            刷新数据
          </Button>
        </div>
      </Card>

      {/* 系统概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="CPU使用率" 
              value={systemData.cpu[systemData.cpu.length - 1].value} 
              suffix="%"
              prefix={<AreaChartOutlined />}
            />
            <Progress 
              percent={systemData.cpu[systemData.cpu.length - 1].value} 
              status="active" 
              style={{ marginTop: 16 }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="内存使用率" 
              value={systemData.memory[systemData.memory.length - 1].value} 
              suffix="%"
              prefix={<BarChartOutlined />}
            />
            <Progress 
              percent={systemData.memory[systemData.memory.length - 1].value} 
              status="active" 
              style={{ marginTop: 16 }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="网络上传" 
              value={systemData.network[systemData.network.length - 1].upload} 
              suffix="MB/s"
              prefix={<RadarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="网络下载" 
              value={systemData.network[systemData.network.length - 1].download} 
              suffix="MB/s"
              prefix={<RadarChartOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 系统运行状态 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title={<Space><AreaChartOutlined /> CPU使用率</Space>}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={systemData.cpu}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#8884d8" 
                  strokeWidth={2} 
                  name="CPU使用率(%)"
                  activeDot={{ r: 8 }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={12}>
          <Card title={<Space><BarChartOutlined /> 内存使用率</Space>}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={systemData.memory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#82ca9d" name="内存使用率(%)" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 网络流量和频道访问 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title={<Space><RadarChartOutlined /> 网络流量</Space>}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={systemData.network}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="upload" stroke="#8884d8" name="上传(MB/s)" />
                <Line type="monotone" dataKey="download" stroke="#82ca9d" name="下载(MB/s)" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={12}>
          <Card title={<Space><PieChartOutlined /> 频道访问量</Space>}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={systemData.channels}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {systemData.channels.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 用户数据和系统健康 */}
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title={<Space><CalendarOutlined /> 用户数据</Space>}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={systemData.users}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="new" fill="#8884d8" name="新增用户" />
                <Bar dataKey="active" fill="#82ca9d" name="活跃用户" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={12}>
          <Card title={<Space><RadarChartOutlined /> 系统健康状态</Space>}>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart outerRadius={90} data={systemData.systemHealth}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis angle={30} domain={[0, 100]} />
                <Radar
                  name="系统健康"
                  dataKey="A"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.6}
                />
                <Tooltip />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Statistics
