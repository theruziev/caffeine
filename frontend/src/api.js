import axios from 'axios'

const client = axios.create({
  baseURL: 'http://127.0.0.1:8000/v1',
  timeout: 1000,
  headers: { 'X-Client': 'Caffeine web-client' }
})

export const User = {
  login: async (email, password) => await client.post('/user/auth', { email: email, password: password }),
  register: async (email, password, captcha) => await client.post('/user/register', {
    email: email, password: password, captcha: captcha
  }),
  refresh: async () => await client.get('/user/refresh'),
  activate: async (token) => await client.post(`/user/activate/${token}`),
  resetPasswordRequest: async (email, captcha) => await client.post('/user/reset-password', {
    email: email, captcha: captcha
  }),
  resetPasswordCheck: async (token) => await client.get(`/user/reset-password/${token}`),
  resetPassword: async (token, password) => await client.post(`/user/reset-password/${token}`, {
    password: password
  }),
  getById: async (uid) => await client.get(`/user/${uid}`),
  me: async () => await client.get('/user/me'),
  changeStatus: async (uid, status) => await client.post(`/user/${uid}/change_status`, { status: status }),
  changeType: async (uid, type) => await client.post(`/user/${uid}/change_type`, { type: type }),
  search: async (filter, paginator, sort) => await client.post(`/user/search`, {
    filter: filter,
    paginator: paginator,
    sort: sort
  }),

}

export const App = {
  info: async () => await client.get("/info"),
  health: async () => await client.get("/health"),
}
