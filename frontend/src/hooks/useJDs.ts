import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/endpoints'

export function useJDList() {
  return useQuery({
    queryKey: ['jds'],
    queryFn: () => api.listJDs(),
  })
}

export function useJDDetail(jdId: string | null) {
  return useQuery({
    queryKey: ['jds', jdId],
    queryFn: () => api.getJD(jdId!),
    enabled: !!jdId,
  })
}

export function useSaveJD() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ title, text }: { title: string; text: string }) =>
      api.saveJD(title, text),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jds'] }),
  })
}

export function useDeleteJD() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (jdId: string) => api.deleteJD(jdId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jds'] }),
  })
}

export function useJDCandidates(jdId: string | null) {
  return useQuery({
    queryKey: ['jds', jdId, 'candidates'],
    queryFn: () => api.getJDCandidates(jdId!),
    enabled: !!jdId,
  })
}
