import React, { useState, useEffect } from 'react'
import { Card, Form, Input, Select, Switch, Button, message, Divider, Space, Upload, Alert } from 'antd'
import { SaveOutlined, ReloadOutlined, UploadOutlined, SettingOutlined, DatabaseOutlined, ScheduleOutlined, WifiOutlined } from '@ant-design/icons'
import { canPerformAction } from '../utils/permission'

const { Option } = Select
const { TextArea } = Input

// 模拟系统配置数据
const mockSystemConfig = {
  // 基本设置
  basic: {
    siteName: 'IPTV管理系统',
    siteDescription: '专业的IPTV频道管理系统',
    siteLogo: '',
    adminEmail: 'admin@example.com',
    timezone: 'Asia/Shanghai'
  },
  
  // 数据库设置
  database: {
    autoBackup: true,
    backupInterval: 24, // 小时
    maxBackups: 5,
    optimizeInterval: 72 // 小时
  },
  
  // 爬虫设置
  crawler: {
    enabled: true,
    interval: 60, // 分钟
    timeout: 30, // 秒
    maxRetries: 3,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  },
  
  // 网络设置
  network: {
    proxyEnabled: false,
    proxyUrl: '',
    timeout: 10, // 秒
    retryInterval: 5 // 秒
  }
}

const SystemSettings = () => {
  const [systemConfig, setSystemConfig] = useState(mockSystemConfig)
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()
  const [currentUser, setCurrentUser] = useState({
    // 模拟当前用户
    id: 1,
    username: 'admin',
    role: 'admin'
  })

  useEffect(() => {
    // 模拟获取系统配置数据
    // 实际项目中应该调用真实的API
    setTimeout(() => {
      form.setFieldsValue(systemConfig)
      message.info('系统配置已加载')
    }, 1000)
  }, [])

  // 检查用户是否有编辑权限
  const canEdit = canPerformAction(currentUser, 'settings', 'edit')

  // 保存系统配置
  const handleSave = (values) => {
    try {
      setLoading(true)
      // 模拟保存配置
      // 实际项目中应该调用真实的API
      setTimeout(() => {
        setSystemConfig(values)
        message.success('系统配置保存成功')
        setLoading(false)
      }, 1000)
    } catch (error) {
      message.error('保存失败，请重试')
      setLoading(false)
    }
  }

  // 重置配置
  const handleReset = () => {
    form.setFieldsValue(systemConfig)
    message.info('配置已重置')
  }

  // 恢复默认配置
  const handleRestoreDefault = () => {
    // 模拟恢复默认配置
    const defaultConfig = {
      basic: {
        siteName: 'IPTV管理系统',
        siteDescription: '专业的IPTV频道管理系统',
        siteLogo: '',
        adminEmail: 'admin@example.com',
        timezone: 'Asia/Shanghai'
      },
      database: {
        autoBackup: true,
        backupInterval: 24,
        maxBackups: 5,
        optimizeInterval: 72
      },
      crawler: {
        enabled: true,
        interval: 60,
        timeout: 30,
        maxRetries: 3,
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      network: {
        proxyEnabled: false,
        proxyUrl: '',
        timeout: 10,
        retryInterval: 5
      }
    }
    form.setFieldsValue(defaultConfig)
    message.info('已恢复默认配置')
  }

  if (!canEdit) {
    return (
      <div className="system-settings-container">
        <h1>系统设置</h1>
        <Alert 
          message="权限不足" 
          description="您没有权限修改系统设置" 
          type="warning" 
          showIcon 
        />
      </div>
    )
  }

  return (
    <div className="system-settings-container">
      <h1>系统设置</h1>
      
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        style={{ maxWidth: 800 }}
      >
        {/* 基本设置 */}
        <Card title={<Space><SettingOutlined /> 基本设置</Space>} style={{ marginBottom: 16 }}>
          <Form.Item
            name={['basic', 'siteName']}
            label="站点名称"
            rules={[{ required: true, message: '请输入站点名称!' }]}
          >
            <Input placeholder="请输入站点名称" />
          </Form.Item>
          
          <Form.Item
            name={['basic', 'siteDescription']}
            label="站点描述"
          >
            <TextArea placeholder="请输入站点描述" rows={3} />
          </Form.Item>
          
          <Form.Item
            name={['basic', 'siteLogo']}
            label="站点Logo"
          >
            <Upload.Dragger
              name="file"
              action="/api/upload"
              listType="picture"
              maxCount={1}
            >
              <p className="ant-upload-drag-icon">
                <UploadOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">
                支持 JPG, PNG, GIF 格式，最大 2MB
              </p>
            </Upload.Dragger>
          </Form.Item>
          
          <Form.Item
            name={['basic', 'adminEmail']}
            label="管理员邮箱"
            rules={[
              { required: true, message: '请输入管理员邮箱!' },
              { type: 'email', message: '请输入有效的邮箱地址!' }
            ]}
          >
            <Input placeholder="请输入管理员邮箱" />
          </Form.Item>
          
          <Form.Item
            name={['basic', 'timezone']}
            label="时区"
          >
            <Select placeholder="请选择时区">
              <Option value="Asia/Shanghai">亚洲/上海</Option>
              <Option value="America/New_York">美洲/纽约</Option>
              <Option value="Europe/London">欧洲/伦敦</Option>
              <Option value="Asia/Tokyo">亚洲/东京</Option>
            </Select>
          </Form.Item>
        </Card>

        {/* 数据库设置 */}
        <Card title={<Space><DatabaseOutlined /> 数据库设置</Space>} style={{ marginBottom: 16 }}>
          <Form.Item
            name={['database', 'autoBackup']}
            label="自动备份"
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
          
          <Form.Item
            name={['database', 'backupInterval']}
            label="备份间隔（小时）"
            rules={[{ required: true, message: '请输入备份间隔!' }]}
          >
            <Input type="number" min={1} max={168} placeholder="请输入备份间隔" />
          </Form.Item>
          
          <Form.Item
            name={['database', 'maxBackups']}
            label="最大备份数"
            rules={[{ required: true, message: '请输入最大备份数!' }]}
          >
            <Input type="number" min={1} max={100} placeholder="请输入最大备份数" />
          </Form.Item>
          
          <Form.Item
            name={['database', 'optimizeInterval']}
            label="优化间隔（小时）"
            rules={[{ required: true, message: '请输入优化间隔!' }]}
          >
            <Input type="number" min={1} max={168} placeholder="请输入优化间隔" />
          </Form.Item>
        </Card>

        {/* 爬虫设置 */}
        <Card title={<Space><ScheduleOutlined /> 爬虫设置</Space>} style={{ marginBottom: 16 }}>
          <Form.Item
            name={['crawler', 'enabled']}
            label="启用爬虫"
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
          
          <Form.Item
            name={['crawler', 'interval']}
            label="爬取间隔（分钟）"
            rules={[{ required: true, message: '请输入爬取间隔!' }]}
          >
            <Input type="number" min={1} max={1440} placeholder="请输入爬取间隔" />
          </Form.Item>
          
          <Form.Item
            name={['crawler', 'timeout']}
            label="超时时间（秒）"
            rules={[{ required: true, message: '请输入超时时间!' }]}
          >
            <Input type="number" min={1} max={300} placeholder="请输入超时时间" />
          </Form.Item>
          
          <Form.Item
            name={['crawler', 'maxRetries']}
            label="最大重试次数"
            rules={[{ required: true, message: '请输入最大重试次数!' }]}
          >
            <Input type="number" min={1} max={10} placeholder="请输入最大重试次数" />
          </Form.Item>
          
          <Form.Item
            name={['crawler', 'userAgent']}
            label="User-Agent"
            rules={[{ required: true, message: '请输入User-Agent!' }]}
          >
            <Input placeholder="请输入User-Agent" />
          </Form.Item>
        </Card>

        {/* 网络设置 */}
        <Card title={<Space><WifiOutlined /> 网络设置</Space>} style={{ marginBottom: 16 }}>
          <Form.Item
            name={['network', 'proxyEnabled']}
            label="启用代理"
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
          
          <Form.Item
            name={['network', 'proxyUrl']}
            label="代理地址"
          >
            <Input placeholder="请输入代理地址" />
          </Form.Item>
          
          <Form.Item
            name={['network', 'timeout']}
            label="超时时间（秒）"
            rules={[{ required: true, message: '请输入超时时间!' }]}
          >
            <Input type="number" min={1} max={60} placeholder="请输入超时时间" />
          </Form.Item>
          
          <Form.Item
            name={['network', 'retryInterval']}
            label="重试间隔（秒）"
            rules={[{ required: true, message: '请输入重试间隔!' }]}
          >
            <Input type="number" min={1} max={30} placeholder="请输入重试间隔" />
          </Form.Item>
        </Card>

        {/* 操作按钮 */}
        <Form.Item style={{ textAlign: 'right' }}>
          <Space>
            <Button onClick={handleReset} icon={<ReloadOutlined />}>
              重置
            </Button>
            <Button onClick={handleRestoreDefault}>
              恢复默认
            </Button>
            <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
              保存设置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </div>
  )
}

export default SystemSettings
