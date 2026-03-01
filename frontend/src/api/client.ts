export interface GlucoseReading {
  id: string
  timestamp: string
  value_mgdl: number
  trend: string
}

export interface InsulinDose {
  id: string
  timestamp: string
  dose_type: 'bolus' | 'correction' | 'temp_basal'
  units: number
  duration_minutes: number | null
  metadata: Record<string, unknown>
}

export interface HeartRateReading {
  id: string
  timestamp: string
  bpm: number
}

async function apiFetch<T>(path: string, start: Date, end: Date): Promise<T[]> {
  const params = new URLSearchParams({
    start: start.toISOString(),
    end: end.toISOString(),
  })
  const res = await fetch(`${path}?${params}`)
  const json = await res.json()
  if (json.error) throw new Error(json.error)
  return json.data
}

export const fetchGlucose = (start: Date, end: Date) =>
  apiFetch<GlucoseReading>('/api/glucose', start, end)

export const fetchInsulin = (start: Date, end: Date) =>
  apiFetch<InsulinDose>('/api/insulin', start, end)

export const fetchHeartRate = (start: Date, end: Date) =>
  apiFetch<HeartRateReading>('/api/heart-rate', start, end)
