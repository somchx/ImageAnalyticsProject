export interface Session {
  id: string
  name: string
  source_type: string
  source_filename: string | null
  status: string
  created_at: number
  closed_at: number | null
  total_frames: number
  final_state: string | null
}

export type SourceType = 'WEBCAM' | 'VIDEO' | 'IMAGE'
