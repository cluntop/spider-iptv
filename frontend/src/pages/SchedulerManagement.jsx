import React, { useState, useEffect } from 'react'
import { Card, Table, Button, message, Popconfirm, Modal, Form, Input, Select, DatePicker, TimePicker, Switch, Spin } from 'antd'
import { ScheduleOutlined, ReloadOutlined, DeleteOutlined, EditOutlined, PlayCircleOutlined, PauseCircleOutlined, PlusOutlined } from '@ant-design/icons'

const { Option } = Select
const { RangePicker } = DatePicker
const { TextArea } = Input

const SchedulerManagement = () => {
  const [loading, setLoading] = useState(false)
  const [schedules, setSchedules] = useState([])
  const [editingSchedule, setEditingSchedule] = useState(null)
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [form] = Form.useForm()
  
  // 模拟调度任务数据
  useEffect(() => {
    fetchSchedules()
  }, [])
  
  // 获取调度任务列表
  const fetchSchedules = async () => {
    setLoading(true)
    try {
      // 模拟API调用
      setTimeout(() => {
        setSchedules([
          {
            key: '1',
            id: 1,
            name: '频道速度检查',
            type: 'channel_check',
            cron: '0 0 * * *', // 每天凌晨执行
            status: 'active',
            lastRun: '2024-01-15 00:00:00',
            nextRun: '2024-01-16 00:00:00',
            description: '检查所有频道的连接速度和稳定性'
          },
          {
            key: '2',
            id: 2,
            name: '数据源更新',
            type: 'source_update',
            cron: '0 6 * * *', // 每天早上6点执行
            status: 'active',
            lastRun: '2024-01-15 06:00:00',
            nextRun: '2024-01-16 06:00:00',
            description: '更新网络数据源和组播数据'
          },
          {
            key: '3',
            id: 3,
            name: '播放列表生成',
            type: 'playlist_generate',
            cron: '0 8 * * *', // 每天早上8点执行
            status: 'active',
            lastRun: '2024-01-15 08:00:00',
            nextRun: '2024-01-16 08:00:00',
            description: '生成最新的IPTV播放列表'
          },
          {
            key: '4',
            id: 4,
            name: '数据库优化',
            type: 'db_optimize',
            cron: '0 1 * * 0', // 每周日凌晨1点执行
            status: 'inactive',
            lastRun: '2024-01-14 01:00:00',
            nextRun: '2024-01-21 01:00:00',
            description: '优化数据库结构和索引'
          }
        ])
        setLoading(false)
      }, 1000)
    } catch (error) {
      message.error('获取调度任务失败')
      setLoading(false)
    }
  }
  
  // 立即执行调度任务
  const runScheduleNow = async (scheduleId) => {
    try {
      // 模拟API调用
      message.loading('任务执行中...')
      setTimeout(() => {
        message.success('任务执行完成')
        fetchSchedules() // 刷新列表
      }, 1500)
    } catch (error) {
      message.error('任务执行失败')
    }
  }
  
  // 切换调度任务状态
  const toggleScheduleStatus = async (scheduleId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'active' ? 'inactive' : 'active'
      // 模拟API调用
      message.loading('更新中...')
      setTimeout(() => {
        message.success(`任务已${newStatus === 'active' ? '启用' : '禁用'}`)
        fetchSchedules() // 刷新列表
      }, 1000)
    } catch (error) {
      message.error('更新失败')
    }
  }
  
  // 删除调度任务
  const deleteSchedule = async (scheduleId) => {
    try {
      // 模拟API调用
      message.loading('删除中...')
      setTimeout(() => {
        message.success('任务已删除')
        fetchSchedules() // 刷新列表
      }, 1000)
    } catch (error) {
      message.error('删除失败')
    }
  }
  
  // 编辑调度任务
  const editSchedule = (schedule) => {
    setEditingSchedule(schedule)
    form.setFieldsValue(schedule)
    setIsModalVisible(true)
  }
  
  // 新增调度任务
  const addSchedule = () => {
    setEditingSchedule(null)
    form.resetFields()
    setIsModalVisible(true)
  }
  
  // 保存调度任务
  const saveSchedule = async () => {
    try {
      const values = await form.validateFields()
      // 模拟API调用
      message.loading('保存中...')
      setTimeout(() => {
        message.success(editingSchedule ? '任务已更新' : '任务已添加')
        setIsModalVisible(false)
        fetchSchedules() // 刷新列表
      }, 1000)
    } catch (error) {
      message.error('保存失败')
    }
  }
  
  // 任务类型选项
  const scheduleTypes = [
    { value: 'channel_check', label: '频道速度检查' },
    { value: 'source_update', label: '数据源更新' },
    { value: 'playlist_generate', label: '播放列表生成' },
    { value: 'db_optimize', label: '数据库优化' },
    { value: 'custom', label: '自定义任务' }
  ]
  
  return (
    <div className="scheduler-management">
      <Card
        title={
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <ScheduleOutlined style={{ marginRight: 8 }} />
              调度管理
            </div>
            <div>
              <Button
                icon={<ReloadOutlined />}
                onClick={fetchSchedules}
                loading={loading}
                style={{ marginRight: 8 }}
              >
                刷新列表
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={addSchedule}
              >
                新增任务
              </Button>
            </div>
          </div>
        }
        bordered={false}
      >
        <Table
          dataSource={schedules}
          loading={loading}
          columns={[
            {
              title: '任务名称',
              dataIndex: 'name',
              key: 'name'
            },
            {
              title: '任务类型',
              dataIndex: 'type',
              key: 'type',
              render: (type) => {
                const typeOption = scheduleTypes.find(option => option.value === type)
                return typeOption ? typeOption.label : type
              }
            },
            {
              title: '执行周期',
              dataIndex: 'cron',
              key: 'cron'
            },
            {
              title: '状态',
              dataIndex: 'status',
              key: 'status',
              render: (status, record) => (
                <Switch
                  checked={status === 'active'}
                  onChange={() => toggleScheduleStatus(record.id, status)}
                  checkedChildren="启用"
                  unCheckedChildren="禁用"
                />
              )
            },
            {
              title: '最后执行',
              dataIndex: 'lastRun',
              key: 'lastRun'
            },
            {
              title: '下次执行',
              dataIndex: 'nextRun',
              key: 'nextRun'
            },
            {
              title: '操作',
              key: 'action',
              render: (_, record) => (
                <div>
                  <Button
                    icon={<PlayCircleOutlined />}
                    onClick={() => runScheduleNow(record.id)}
                    style={{ marginRight: 8 }}
                  >
                    立即执行
                  </Button>
                  <Button
                    icon={<EditOutlined />}
                    onClick={() => editSchedule(record)}
                    style={{ marginRight: 8 }}
                  >
                    编辑
                  </Button>
                  <Popconfirm
                    title="确定删除此任务吗？"
                    onConfirm={() => deleteSchedule(record.id)}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button icon={<DeleteOutlined />} danger>
                      删除
                    </Button>
                  </Popconfirm>
                </div>
              )
            }
          ]}
        />
        
        {/* 编辑/新增任务模态框 */}
        <Modal
          title={editingSchedule ? '编辑调度任务' : '新增调度任务'}
          open={isModalVisible}
          onOk={saveSchedule}
          onCancel={() => setIsModalVisible(false)}
          okText="保存"
          cancelText="取消"
        >
          <Form
            form={form}
            layout="vertical"
          >
            <Form.Item
              name="name"
              label="任务名称"
              rules={[{ required: true, message: '请输入任务名称' }]}
            >
              <Input placeholder="请输入任务名称" />
            </Form.Item>
            
            <Form.Item
              name="type"
              label="任务类型"
              rules={[{ required: true, message: '请选择任务类型' }]}
            >
              <Select placeholder="请选择任务类型">
                {scheduleTypes.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            
            <Form.Item
              name="cron"
              label="执行周期 (Cron表达式)"
              rules={[{ required: true, message: '请输入Cron表达式' }]}
            >
              <Input placeholder="例如: 0 0 * * * (每天凌晨执行)" />
            </Form.Item>
            
            <Form.Item
              name="description"
              label="任务描述"
            >
              <TextArea rows={3} placeholder="请输入任务描述" />
            </Form.Item>
          </Form>
        </Modal>
      </Card>
    </div>
  )
}

export default SchedulerManagement
