import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 60_000,
})

client.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      'An unexpected error occurred'
    return Promise.reject(new Error(message))
  },
)

export default client
