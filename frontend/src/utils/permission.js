// 权限控制工具函数

// 权限配置
const permissions = {
  // 管理员权限
  admin: {
    dashboard: true,
    users: {
      view: true,
      add: true,
      edit: true,
      delete: true
    },
    channels: {
      view: true,
      add: true,
      edit: true,
      delete: true
    },
    database: {
      view: true,
      manage: true
    },
    scheduler: {
      view: true,
      manage: true
    },
    settings: {
      view: true,
      edit: true
    }
  },
  
  // 经理权限
  manager: {
    dashboard: true,
    users: {
      view: true,
      add: true,
      edit: true,
      delete: false
    },
    channels: {
      view: true,
      add: true,
      edit: true,
      delete: true
    },
    database: {
      view: true,
      manage: false
    },
    scheduler: {
      view: true,
      manage: true
    },
    settings: {
      view: false,
      edit: false
    }
  },
  
  // 编辑权限
  editor: {
    dashboard: true,
    users: {
      view: false,
      add: false,
      edit: false,
      delete: false
    },
    channels: {
      view: true,
      add: true,
      edit: true,
      delete: false
    },
    database: {
      view: false,
      manage: false
    },
    scheduler: {
      view: false,
      manage: false
    },
    settings: {
      view: false,
      edit: false
    }
  },
  
  // 查看者权限
  viewer: {
    dashboard: true,
    users: {
      view: false,
      add: false,
      edit: false,
      delete: false
    },
    channels: {
      view: true,
      add: false,
      edit: false,
      delete: false
    },
    database: {
      view: false,
      manage: false
    },
    scheduler: {
      view: false,
      manage: false
    },
    settings: {
      view: false,
      edit: false
    }
  }
}

/**
 * 检查用户是否有特定权限
 * @param {Object} user - 用户对象
 * @param {string} resource - 资源名称
 * @param {string} action - 操作名称
 * @returns {boolean} - 是否有权限
 */
export const checkPermission = (user, resource, action = 'view') => {
  if (!user || !user.role) {
    return false
  }
  
  const rolePermissions = permissions[user.role]
  if (!rolePermissions) {
    return false
  }
  
  const resourcePermissions = rolePermissions[resource]
  if (typeof resourcePermissions === 'boolean') {
    return resourcePermissions
  }
  
  if (resourcePermissions && typeof resourcePermissions === 'object') {
    return resourcePermissions[action] || false
  }
  
  return false
}

/**
 * 获取用户角色的权限列表
 * @param {string} role - 角色名称
 * @returns {Object} - 权限列表
 */
export const getRolePermissions = (role) => {
  return permissions[role] || {}
}

/**
 * 检查用户是否可以访问特定页面
 * @param {Object} user - 用户对象
 * @param {string} page - 页面名称
 * @returns {boolean} - 是否可以访问
 */
export const canAccessPage = (user, page) => {
  return checkPermission(user, page)
}

/**
 * 检查用户是否可以执行特定操作
 * @param {Object} user - 用户对象
 * @param {string} resource - 资源名称
 * @param {string} action - 操作名称
 * @returns {boolean} - 是否可以执行
 */
export const canPerformAction = (user, resource, action) => {
  return checkPermission(user, resource, action)
}
