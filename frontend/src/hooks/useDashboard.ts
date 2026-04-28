import { useQuery } from '@tanstack/react-query'
import { api } from '../api/endpoints'

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: api.getDashboardStats,
  })
}
