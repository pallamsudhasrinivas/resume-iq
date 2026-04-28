import client from './client'
import type { DashboardStats, JDCandidatesResponse, JDDetail, JDEntry, JDListResponse, Session, SessionListResponse } from '../types'

export const api = {
  analyze: async (
    files: File[],
    opts: { jobDescription: string; jdId?: never } | { jdId: string; jobDescription?: never },
  ): Promise<Session> => {
    const form = new FormData()
    if (opts.jdId) {
      form.append('jd_id', opts.jdId)
    } else {
      form.append('job_description', opts.jobDescription!)
    }
    files.forEach((f) => form.append('resumes', f))
    const { data } = await client.post<Session>('/analyze', form)
    return data
  },

  listSessions: async (params: {
    limit?: number
    offset?: number
    search?: string
  }): Promise<SessionListResponse> => {
    const { data } = await client.get<SessionListResponse>('/sessions', { params })
    return data
  },

  getSession: async (id: string): Promise<Session> => {
    const { data } = await client.get<Session>(`/sessions/${id}`)
    return data
  },

  deleteSession: async (id: string): Promise<void> => {
    await client.delete(`/sessions/${id}`)
  },

  getDashboardStats: async (): Promise<DashboardStats> => {
    const { data } = await client.get<DashboardStats>('/dashboard/stats')
    return data
  },

  saveJD: async (title: string, text: string): Promise<JDEntry> => {
    const { data } = await client.post<JDEntry>('/jds', { title, text })
    return data
  },

  listJDs: async (params?: { limit?: number; offset?: number }): Promise<JDListResponse> => {
    const { data } = await client.get<JDListResponse>('/jds', { params })
    return data
  },

  getJD: async (jdId: string): Promise<JDDetail> => {
    const { data } = await client.get<JDDetail>(`/jds/${jdId}`)
    return data
  },

  deleteJD: async (jdId: string): Promise<void> => {
    await client.delete(`/jds/${jdId}`)
  },

  getJDCandidates: async (jdId: string): Promise<JDCandidatesResponse> => {
    const { data } = await client.get<JDCandidatesResponse>(`/jds/${jdId}/candidates`)
    return data
  },
}
