import client from './client'

export const uploadImage = (file: File) => {
  const fd = new FormData()
  fd.append('file', file)
  return client.post('/upload/image', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data)
}

export const uploadVideo = (file: File) => {
  const fd = new FormData()
  fd.append('file', file)
  return client.post('/upload/video', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  }).then(r => r.data)
}
