import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Modal, Form, Input, Select, Switch, Tag, message, Popconfirm, Space, Divider } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, LockOutlined, UnlockOutlined, UserOutlined } from '@ant-design/icons'

const { Option } = Select

// 模拟用户数据
const mockUsers = [
  { id: 1, username: 'admin', email: 'admin@example.com', role: 'admin', status: true, createdAt: '2026-01-01', lastLogin: '2026-02-22' },
  { id: 2, username: 'editor', email: 'editor@example.com', role: 'editor', status: true, createdAt: '2026-01-05', lastLogin: '2026-02-21' },
  { id: 3, username: 'viewer', email: 'viewer@example.com', role: 'viewer', status: false, createdAt: '2026-01-10', lastLogin: '2026-02-20' },
  { id: 4, username: 'manager', email: 'manager@example.com', role: 'manager', status: true, createdAt: '2026-01-15', lastLogin: '2026-02-19' }
]

// 角色选项
const roles = [
  { value: 'admin', label: '管理员', description: '拥有系统所有权限' },
  { value: 'manager', label: '经理', description: '拥有管理权限，但不能修改系统设置' },
  { value: 'editor', label: '编辑', description: '只能编辑内容，不能管理用户' },
  { value: 'viewer', label: '查看者', description: '只能查看内容，不能编辑' }
]

const UserManagement = () => {
  const [users, setUsers] = useState(mockUsers)
  const [filteredUsers, setFilteredUsers] = useState(mockUsers)
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [currentUser, setCurrentUser] = useState({})
  const [searchText, setSearchText] = useState('')
  const [selectedRole, setSelectedRole] = useState('')
  const [form] = Form.useForm()

  useEffect(() => {
    // 模拟获取用户数据
    // 实际项目中应该调用真实的API
    setTimeout(() => {
      message.info('用户数据已更新')
    }, 1000)
  }, [])

  // 搜索和筛选用户
  useEffect(() => {
    let result = [...users]
    
    if (searchText) {
      result = result.filter(user => 
        user.username.toLowerCase().includes(searchText.toLowerCase()) ||
        user.email.toLowerCase().includes(searchText.toLowerCase())
      )
    }
    
    if (selectedRole) {
      result = result.filter(user => user.role === selectedRole)
    }
    
    setFilteredUsers(result)
  }, [searchText, selectedRole, users])

  // 打开添加用户模态框
  const showAddModal = () => {
    setIsEditing(false)
    setCurrentUser({})
    form.resetFields()
    setIsModalVisible(true)
  }

  // 打开编辑用户模态框
  const showEditModal = (user) => {
    setIsEditing(true)
    setCurrentUser(user)
    form.setFieldsValue(user)
    setIsModalVisible(true)
  }

  // 保存用户
  const handleSave = (values) => {
    try {
      if (isEditing) {
        // 编辑现有用户
        const updatedUsers = users.map(user => 
          user.id === currentUser.id ? { ...user, ...values } : user
        )
        setUsers(updatedUsers)
        message.success('用户更新成功')
      } else {
        // 添加新用户
        const newUser = {
          id: Date.now(),
          ...values,
          createdAt: new Date().toISOString().split('T')[0],
          lastLogin: '-' 
        }
        setUsers([...users, newUser])
        message.success('用户添加成功')
      }
      setIsModalVisible(false)
    } catch (error) {
      message.error('操作失败，请重试')
    }
  }

  // 删除用户
  const handleDelete = (id) => {
    try {
      const updatedUsers = users.filter(user => user.id !== id)
      setUsers(updatedUsers)
      message.success('用户删除成功')
    } catch (error) {
      message.error('删除失败，请重试')
    }
  }

  // 切换用户状态
  const handleStatusChange = (id, status) => {
    try {
      const updatedUsers = users.map(user => 
        user.id === id ? { ...user, status } : user
      )
      setUsers(updatedUsers)
      message.success(`用户已${status ? '启用' : '禁用'}`)
    } catch (error) {
      message.error('操作失败，请重试')
    }
  }

  return (
    <div className="user-management-container">
      <h1>用户管理</h1>
      
      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={showAddModal}
          >
            添加用户
          </Button>
          
          <div style={{ display: 'flex', gap: 16 }}>
            <Input
              placeholder="搜索用户名或邮箱"
              prefix={<SearchOutlined />}
              style={{ width: 250 }}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
            <Select
              placeholder="选择角色"
              style={{ width: 120 }}
              value={selectedRole}
              onChange={setSelectedRole}
              allowClear
            >
              {roles.map(role => (
                <Option key={role.value} value={role.value}>{role.label}</Option>
              ))}
            </Select>
          </div>
        </div>
      </Card>

      {/* 用户列表 */}
      <Card>
        <Table 
          dataSource={filteredUsers} 
          columns={[
            {
              title: 'ID',
              dataIndex: 'id',
              key: 'id',
              width: 80
            },
            {
              title: '用户名',
              dataIndex: 'username',
              key: 'username',
              sorter: (a, b) => a.username.localeCompare(b.username)
            },
            {
              title: '邮箱',
              dataIndex: 'email',
              key: 'email'
            },
            {
              title: '角色',
              dataIndex: 'role',
              key: 'role',
              filters: roles.map(role => ({
                text: role.label,
                value: role.value
              })),
              onFilter: (value, record) => record.role === value,
              render: (role) => {
                const roleInfo = roles.find(r => r.value === role)
                return (
                  <Tag color={getRoleColor(role)}>
                    {roleInfo?.label || role}
                  </Tag>
                )
              }
            },
            {
              title: '状态',
              dataIndex: 'status',
              key: 'status',
              render: (status, record) => (
                <Switch
                  checked={status}
                  onChange={(checked) => handleStatusChange(record.id, checked)}
                  checkedChildren={<UnlockOutlined />}
                  unCheckedChildren={<LockOutlined />}
                />
              )
            },
            {
              title: '创建时间',
              dataIndex: 'createdAt',
              key: 'createdAt',
              sorter: (a, b) => new Date(a.createdAt) - new Date(b.createdAt)
            },
            {
              title: '最后登录',
              dataIndex: 'lastLogin',
              key: 'lastLogin'
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
                    title="确定要删除这个用户吗？"
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
          pagination={{ pageSize: 10 }}
          scroll={{ x: 1000 }}
        />
      </Card>

      {/* 用户编辑模态框 */}
      <Modal
        title={isEditing ? '编辑用户' : '添加用户'}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: true, message: '请输入用户名!' }]}
          >
            <Input placeholder="请输入用户名" prefix={<UserOutlined />} />
          </Form.Item>
          
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱!' },
              { type: 'email', message: '请输入有效的邮箱地址!' }
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>
          
          {!isEditing && (
            <Form.Item
              name="password"
              label="密码"
              rules={[{ required: true, message: '请输入密码!' }]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
          )}
          
          <Form.Item
            name="role"
            label="角色"
            rules={[{ required: true, message: '请选择角色!' }]}
          >
            <Select placeholder="请选择角色">
              {roles.map(role => (
                <Option key={role.value} value={role.value}>
                  {role.label} - {role.description}
                </Option>
              ))}
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

// 根据角色获取颜色
const getRoleColor = (role) => {
  switch (role) {
    case 'admin': return 'red'
    case 'manager': return 'orange'
    case 'editor': return 'blue'
    case 'viewer': return 'green'
    default: return 'default'
  }
}

export default UserManagement
