import React, { useState, useEffect } from 'react'
import { Card, Table, Button, message, Popconfirm, Modal, Form, Input, Select, Spin, Statistic, Row, Col } from 'antd'
import { DatabaseOutlined, ReloadOutlined, DeleteOutlined, CheckCircleOutlined, CloseCircleOutlined, WarningOutlined } from '@ant-design/icons'

const { Option } = Select

const DatabaseManagement = () => {
  const [loading, setLoading] = useState(false)
  const [dbStatus, setDbStatus] = useState(null)
  const [optimizing, setOptimizing] = useState(false)
  
  // 模拟数据库表结构
  const tableData = [
    {
      key: '1',
      name: 'iptv_channels',
      rows: 1250,
      size: '15.2 MB',
      indexes: 3,
      lastUpdated: '2024-01-15 10:30:00',
      status: 'healthy'
    },
    {
      key: '2',
      name: 'iptv_hotels',
      rows: 890,
      size: '8.7 MB',
      indexes: 2,
      lastUpdated: '2024-01-15 09:15:00',
      status: 'healthy'
    },
    {
      key: '3',
      name: 'iptv_multicast',
      rows: 520,
      size: '5.1 MB',
      indexes: 2,
      lastUpdated: '2024-01-15 08:45:00',
      status: 'warning'
    },
    {
      key: '4',
      name: 'iptv_udpxy',
      rows: 310,
      size: '3.2 MB',
      indexes: 1,
      lastUpdated: '2024-01-15 08:00:00',
      status: 'healthy'
    }
  ]
  
  useEffect(() => {
    checkDatabaseStatus()
  }, [])
  
  // 检查数据库状态
  const checkDatabaseStatus = async () => {
    setLoading(true)
    try {
      // 模拟API调用
      setTimeout(() => {
        setDbStatus({
          status: 'healthy',
          size: '32.2 MB',
          tables: 4,
          indexes: 8,
          lastCheck: new Date().toLocaleString(),
          connections: 5,
          uptime: '2 days, 14 hours, 30 minutes'
        })
        setLoading(false)
      }, 1000)
    } catch (error) {
      message.error('检查数据库状态失败')
      setLoading(false)
    }
  }
  
  // 优化数据库
  const optimizeDatabase = async () => {
    setOptimizing(true)
    try {
      // 模拟API调用
      setTimeout(() => {
        message.success('数据库优化完成')
        setOptimizing(false)
        checkDatabaseStatus() // 重新检查状态
      }, 2000)
    } catch (error) {
      message.error('数据库优化失败')
      setOptimizing(false)
    }
  }
  
  // 获取状态图标
  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14' }} />
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
      default:
        return null
    }
  }
  
  // 获取状态文本
  const getStatusText = (status) => {
    switch (status) {
      case 'healthy':
        return '健康'
      case 'warning':
        return '警告'
      case 'error':
        return '错误'
      default:
        return '未知'
    }
  }
  
  return (
    <div className="database-management">
      <Card
        title={
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <DatabaseOutlined style={{ marginRight: 8 }} />
              数据库管理
            </div>
            <div>
              <Button
                icon={<ReloadOutlined />}
                onClick={checkDatabaseStatus}
                loading={loading}
                style={{ marginRight: 8 }}
              >
                刷新状态
              </Button>
              <Button
                type="primary"
                onClick={optimizeDatabase}
                loading={optimizing}
                disabled={!dbStatus}
              >
                优化数据库
              </Button>
            </div>
          </div>
        }
        bordered={false}
      >
        {/* 数据库状态概览 */}
        {dbStatus && (
          <div style={{ marginBottom: 24 }}>
            <Row gutter={16}>
              <Col span={6}>
                <Card size="small">
                  <Statistic 
                    title="数据库状态" 
                    value={getStatusText(dbStatus.status)}
                    prefix={getStatusIcon(dbStatus.status)}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic title="数据库大小" value={dbStatus.size} />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic title="表数量" value={dbStatus.tables} />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic title="索引数量" value={dbStatus.indexes} />
                </Card>
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={8}>
                <Card size="small">
                  <Statistic title="当前连接数" value={dbStatus.connections} />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Statistic title="运行时间" value={dbStatus.uptime} />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Statistic title="最后检查" value={dbStatus.lastCheck} />
                </Card>
              </Col>
            </Row>
          </div>
        )}
        
        {/* 数据库表结构 */}
        <Card title="数据库表结构" size="small">
          <Table
            dataSource={tableData}
            columns={[
              {
                title: '表名',
                dataIndex: 'name',
                key: 'name'
              },
              {
                title: '记录数',
                dataIndex: 'rows',
                key: 'rows'
              },
              {
                title: '大小',
                dataIndex: 'size',
                key: 'size'
              },
              {
                title: '索引数',
                dataIndex: 'indexes',
                key: 'indexes'
              },
              {
                title: '最后更新',
                dataIndex: 'lastUpdated',
                key: 'lastUpdated'
              },
              {
                title: '状态',
                dataIndex: 'status',
                key: 'status',
                render: (status) => (
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    {getStatusIcon(status)}
                    <span style={{ marginLeft: 4 }}>{getStatusText(status)}</span>
                  </div>
                )
              }
            ]}
            pagination={false}
          />
        </Card>
      </Card>
    </div>
  )
}

export default DatabaseManagement
