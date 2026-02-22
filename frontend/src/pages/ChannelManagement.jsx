import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Modal, Form, Input, Select, Switch, Tag, message, Popconfirm, Space, InputNumber, Checkbox } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, ReloadOutlined, CheckCircleOutlined, CloseCircleOutlined, DeleteRowOutlined, PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons'

const { Option } = Select

// 模拟频道数据
const mockChannels = [
  { id: 1, name: '央视综合', category: '央视', status: true, url: 'http://example.com/channel1', viewers: 1200, quality: '高清' },
  { id: 2, name: '央视新闻', category: '央视', status: true, url: 'http://example.com/channel2', viewers: 980, quality: '高清' },
  { id: 3, name: '湖南卫视', category: '卫视', status: false, url: 'http://example.com/channel3', viewers: 0, quality: '标清' },
  { id: 4, name: '江苏卫视', category: '卫视', status: true, url: 'http://example.com/channel4', viewers: 750, quality: '高清' },
  { id: 5, name: '浙江卫视', category: '卫视', status: true, url: 'http://example.com/channel5', viewers: 620, quality: '高清' },
  { id: 6, name: '东方卫视', category: '卫视', status: true, url: 'http://example.com/channel6', viewers: 580, quality: '高清' },
  { id: 7, name: '北京卫视', category: '卫视', status: true, url: 'http://example.com/channel7', viewers: 450, quality: '标清' },
  { id: 8, name: '广东卫视', category: '卫视', status: true, url: 'http://example.com/channel8', viewers: 380, quality: '标清' }
]

// 频道分类选项
const categories = ['央视', '卫视', '地方', '体育', '电影', '综艺', '少儿', '新闻', '财经']

const ChannelManagement = () => {
  const [channels, setChannels] = useState(mockChannels)
  const [filteredChannels, setFilteredChannels] = useState(mockChannels)
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [currentChannel, setCurrentChannel] = useState({})
  const [searchText, setSearchText] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [selectedRowKeys, setSelectedRowKeys] = useState([])
  const [selectedRows, setSelectedRows] = useState([])
  const [form] = Form.useForm()

  useEffect(() => {
    // 模拟获取频道数据
    // 实际项目中应该调用真实的API
    setTimeout(() => {
      message.info('频道数据已更新')
    }, 1000)
  }, [])

  // 搜索和筛选频道
  useEffect(() => {
    let result = [...channels]
    
    if (searchText) {
      result = result.filter(channel => 
        channel.name.toLowerCase().includes(searchText.toLowerCase())
      )
    }
    
    if (selectedCategory) {
      result = result.filter(channel => channel.category === selectedCategory)
    }
    
    setFilteredChannels(result)
  }, [searchText, selectedCategory, channels])

  // 打开添加频道模态框
  const showAddModal = () => {
    setIsEditing(false)
    setCurrentChannel({})
    form.resetFields()
    setIsModalVisible(true)
  }

  // 打开编辑频道模态框
  const showEditModal = (channel) => {
    setIsEditing(true)
    setCurrentChannel(channel)
    form.setFieldsValue(channel)
    setIsModalVisible(true)
  }

  // 保存频道
  const handleSave = (values) => {
    try {
      if (isEditing) {
        // 编辑现有频道
        const updatedChannels = channels.map(channel => 
          channel.id === currentChannel.id ? { ...channel, ...values } : channel
        )
        setChannels(updatedChannels)
        message.success('频道更新成功')
      } else {
        // 添加新频道
        const newChannel = {
          id: Date.now(),
          ...values,
          viewers: 0
        }
        setChannels([...channels, newChannel])
        message.success('频道添加成功')
      }
      setIsModalVisible(false)
    } catch (error) {
      message.error('操作失败，请重试')
    }
  }

  // 删除频道
  const handleDelete = (id) => {
    try {
      const updatedChannels = channels.filter(channel => channel.id !== id)
      setChannels(updatedChannels)
      message.success('频道删除成功')
    } catch (error) {
      message.error('删除失败，请重试')
    }
  }

  // 切换频道状态
  const handleStatusChange = (id, status) => {
    try {
      const updatedChannels = channels.map(channel => 
        channel.id === id ? { ...channel, status } : channel
      )
      setChannels(updatedChannels)
      message.success(`频道已${status ? '启用' : '禁用'}`)
    } catch (error) {
      message.error('操作失败，请重试')
    }
  }

  // 刷新频道列表
  const handleRefresh = () => {
    // 模拟刷新频道数据
    message.info('频道列表正在刷新...')
    setTimeout(() => {
      message.success('频道列表刷新成功')
    }, 1000)
  }

  // 批量删除频道
  const handleBatchDelete = () => {
    try {
      if (selectedRowKeys.length === 0) {
        message.warning('请先选择要删除的频道')
        return
      }
      
      const updatedChannels = channels.filter(channel => 
        !selectedRowKeys.includes(channel.id)
      )
      setChannels(updatedChannels)
      setSelectedRowKeys([])
      setSelectedRows([])
      message.success(`成功删除 ${selectedRowKeys.length} 个频道`)
    } catch (error) {
      message.error('批量删除失败，请重试')
    }
  }

  // 批量启用频道
  const handleBatchEnable = () => {
    try {
      if (selectedRowKeys.length === 0) {
        message.warning('请先选择要启用的频道')
        return
      }
      
      const updatedChannels = channels.map(channel => 
        selectedRowKeys.includes(channel.id) ? { ...channel, status: true } : channel
      )
      setChannels(updatedChannels)
      setSelectedRowKeys([])
      setSelectedRows([])
      message.success(`成功启用 ${selectedRowKeys.length} 个频道`)
    } catch (error) {
      message.error('批量启用失败，请重试')
    }
  }

  // 批量禁用频道
  const handleBatchDisable = () => {
    try {
      if (selectedRowKeys.length === 0) {
        message.warning('请先选择要禁用的频道')
        return
      }
      
      const updatedChannels = channels.map(channel => 
        selectedRowKeys.includes(channel.id) ? { ...channel, status: false } : channel
      )
      setChannels(updatedChannels)
      setSelectedRowKeys([])
      setSelectedRows([])
      message.success(`成功禁用 ${selectedRowKeys.length} 个频道`)
    } catch (error) {
      message.error('批量禁用失败，请重试')
    }
  }

  // 处理表格选择变化
  const handleSelectChange = (selectedRowKeys, selectedRows) => {
    setSelectedRowKeys(selectedRowKeys)
    setSelectedRows(selectedRows)
  }

  return (
    <div className="channel-management-container">
      <h1>频道管理</h1>
      
      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', gap: 16 }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={showAddModal}
            >
              添加频道
            </Button>
            <Button 
              icon={<ReloadOutlined />} 
              onClick={handleRefresh}
            >
              刷新列表
            </Button>
          </div>
          
          {/* 批量操作按钮 */}
          <div style={{ display: 'flex', gap: 16 }}>
            <Button 
              danger 
              icon={<DeleteRowOutlined />} 
              onClick={handleBatchDelete}
              disabled={selectedRowKeys.length === 0}
            >
              批量删除 ({selectedRowKeys.length})
            </Button>
            <Button 
              type="primary" 
              icon={<PlayCircleOutlined />} 
              onClick={handleBatchEnable}
              disabled={selectedRowKeys.length === 0}
            >
              批量启用
            </Button>
            <Button 
              icon={<PauseCircleOutlined />} 
              onClick={handleBatchDisable}
              disabled={selectedRowKeys.length === 0}
            >
              批量禁用
            </Button>
          </div>
          
          <div style={{ display: 'flex', gap: 16, flex: 1, minWidth: 350, justifyContent: 'flex-end' }}>
            <Input
              placeholder="搜索频道名称"
              prefix={<SearchOutlined />}
              style={{ width: 200 }}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
            <Select
              placeholder="选择分类"
              style={{ width: 120 }}
              value={selectedCategory}
              onChange={setSelectedCategory}
              allowClear
            >
              {categories.map(category => (
                <Option key={category} value={category}>{category}</Option>
              ))}
            </Select>
          </div>
        </div>
      </Card>

      {/* 频道列表 */}
      <Card>
        <Table 
          dataSource={filteredChannels} 
          columns={[
            {
              title: 'ID',
              dataIndex: 'id',
              key: 'id',
              width: 80
            },
            {
              title: '频道名称',
              dataIndex: 'name',
              key: 'name',
              sorter: (a, b) => a.name.localeCompare(b.name)
            },
            {
              title: '分类',
              dataIndex: 'category',
              key: 'category',
              filters: categories.map(category => ({
                text: category,
                value: category
              })),
              onFilter: (value, record) => record.category === value,
              render: (category) => (
                <Tag color="blue">{category}</Tag>
              )
            },
            {
              title: '状态',
              dataIndex: 'status',
              key: 'status',
              render: (status, record) => (
                <Switch
                  checked={status}
                  onChange={(checked) => handleStatusChange(record.id, checked)}
                  checkedChildren={<CheckCircleOutlined />}
                  unCheckedChildren={<CloseCircleOutlined />}
                />
              )
            },
            {
              title: '观看人数',
              dataIndex: 'viewers',
              key: 'viewers',
              sorter: (a, b) => a.viewers - b.viewers
            },
            {
              title: '画质',
              dataIndex: 'quality',
              key: 'quality',
              render: (quality) => (
                <Tag color={quality === '高清' ? 'green' : 'orange'}>
                  {quality}
                </Tag>
              )
            },
            {
              title: '操作',
              key: 'action',
              render: (_, record) => (
                <Space size="middle">
                  <Button 
                    icon={<EditOutlined />} 
                    onClick={() => showEditModal(record)}
                  >
                    编辑
                  </Button>
                  <Popconfirm
                    title="确定要删除这个频道吗？"
                    onConfirm={() => handleDelete(record.id)}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button 
                      danger 
                      icon={<DeleteOutlined />}
                    >
                      删除
                    </Button>
                  </Popconfirm>
                </Space>
              )
            }
          ]}
          rowKey="id"
          rowSelection={{
            selectedRowKeys,
            onChange: handleSelectChange,
            selections: [
              {
                key: 'all-data',
                text: '选择全部数据',
                onSelect: () => {
                  const allKeys = filteredChannels.map(channel => channel.id)
                  setSelectedRowKeys(allKeys)
                  setSelectedRows(filteredChannels)
                }
              },
              {
                key: 'online',
                text: '选择在线频道',
                onSelect: () => {
                  const onlineChannels = filteredChannels.filter(channel => channel.status)
                  const onlineKeys = onlineChannels.map(channel => channel.id)
                  setSelectedRowKeys(onlineKeys)
                  setSelectedRows(onlineChannels)
                }
              },
              {
                key: 'offline',
                text: '选择离线频道',
                onSelect: () => {
                  const offlineChannels = filteredChannels.filter(channel => !channel.status)
                  const offlineKeys = offlineChannels.map(channel => channel.id)
                  setSelectedRowKeys(offlineKeys)
                  setSelectedRows(offlineChannels)
                }
              }
            ]
          }}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true
          }}
          scroll={{ x: 800 }}
        />
      </Card>

      {/* 频道编辑模态框 */}
      <Modal
        title={isEditing ? '编辑频道' : '添加频道'}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Form.Item
            name="name"
            label="频道名称"
            rules={[{ required: true, message: '请输入频道名称!' }]}
          >
            <Input placeholder="请输入频道名称" />
          </Form.Item>
          
          <Form.Item
            name="category"
            label="分类"
            rules={[{ required: true, message: '请选择分类!' }]}
          >
            <Select placeholder="请选择分类">
              {categories.map(category => (
                <Option key={category} value={category}>{category}</Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="url"
            label="频道地址"
            rules={[{ required: true, message: '请输入频道地址!' }]}
          >
            <Input placeholder="请输入频道地址" />
          </Form.Item>
          
          <Form.Item
            name="quality"
            label="画质"
            rules={[{ required: true, message: '请选择画质!' }]}
          >
            <Select placeholder="请选择画质">
              <Option value="标清">标清</Option>
              <Option value="高清">高清</Option>
              <Option value="超清">超清</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="status"
            label="状态"
            initialValue={true}
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
          
          <Form.Item style={{ textAlign: 'right' }}>
            <Button onClick={() => setIsModalVisible(false)} style={{ marginRight: 8 }}>
              取消
            </Button>
            <Button type="primary" htmlType="submit">
              {isEditing ? '更新' : '添加'}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ChannelManagement
