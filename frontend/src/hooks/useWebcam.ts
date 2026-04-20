import { useRef, useCallback, useState } from 'react'

export function useWebcam(onFrame: (b64: string, seq: number) => void, intervalMs = 1000) {
  const streamRef = useRef<MediaStream | null>(null)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const timerRef = useRef<number | null>(null)
  const seqRef = useRef(0)
  const [active, setActive] = useState(false)

  const start = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }

      if (!canvasRef.current) {
        canvasRef.current = document.createElement('canvas')
      }

      timerRef.current = window.setInterval(() => {
        const video = videoRef.current
        const canvas = canvasRef.current
        if (!video || !canvas) return
        canvas.width = video.videoWidth || 640
        canvas.height = video.videoHeight || 480
        const ctx = canvas.getContext('2d')
        if (!ctx) return
        ctx.drawImage(video, 0, 0)
        const b64 = canvas.toDataURL('image/jpeg', 0.7).split(',')[1]
        onFrame(b64, seqRef.current++)
      }, intervalMs)

      setActive(true)
    } catch (err) {
      console.error('Webcam error:', err)
    }
  }, [onFrame, intervalMs])

  const stop = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current)
    streamRef.current?.getTracks().forEach(t => t.stop())
    streamRef.current = null
    setActive(false)
  }, [])

  return { videoRef, active, start, stop }
}
