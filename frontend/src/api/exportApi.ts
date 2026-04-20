export const downloadCsv = (sessionId: string) => {
  const a = document.createElement('a')
  a.href = `/api/v1/export/csv/${sessionId}`
  a.download = `${sessionId}.csv`
  a.click()
}
