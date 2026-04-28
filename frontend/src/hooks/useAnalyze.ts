import { useMutation } from '@tanstack/react-query'
import { api } from '../api/endpoints'

type AnalyzeArgs =
  | { files: File[]; jobDescription: string; jdId?: never }
  | { files: File[]; jdId: string; jobDescription?: never }

export function useAnalyze() {
  return useMutation({
    mutationFn: ({ files, jobDescription, jdId }: AnalyzeArgs) =>
      jdId
        ? api.analyze(files, { jdId })
        : api.analyze(files, { jobDescription: jobDescription! }),
  })
}
