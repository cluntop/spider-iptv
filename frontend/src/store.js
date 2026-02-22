import { configureStore } from '@reduxjs/toolkit'

// 简单的用户认证reducer
const authReducer = (state = {
  isAuthenticated: false,
  user: null,
  token: null
}, action) => {
  switch (action.type) {
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.token
      }
    case 'LOGOUT':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        token: null
      }
    default:
      return state
  }
}

// 简单的频道reducer
const channelsReducer = (state = {
  channels: [],
  loading: false,
  error: null
}, action) => {
  switch (action.type) {
    case 'FETCH_CHANNELS_REQUEST':
      return {
        ...state,
        loading: true
      }
    case 'FETCH_CHANNELS_SUCCESS':
      return {
        ...state,
        loading: false,
        channels: action.payload
      }
    case 'FETCH_CHANNELS_FAILURE':
      return {
        ...state,
        loading: false,
        error: action.payload
      }
    default:
      return state
  }
}

// 配置store
const store = configureStore({
  reducer: {
    auth: authReducer,
    channels: channelsReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false
    })
})

export default store
