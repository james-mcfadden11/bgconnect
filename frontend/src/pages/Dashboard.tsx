import { useEffect, useState } from 'react'
import { BGChart } from '../components/BGChart'
import { DateSelector } from '../components/DateSelector'
import { fetchGlucose, fetchInsulin, fetchHeartRate } from '../api/client'
import type { GlucoseReading, InsulinDose, HeartRateReading } from '../api/client'

function dateToRange(dateStr: string): [Date, Date] {
  const [y, m, d] = dateStr.split('-').map(Number)
  const start = new Date(y, m - 1, d)           // local midnight
  const end = new Date(y, m - 1, d + 1)         // next local midnight
  return [start, end]
}

const todayStr = new Date().toISOString().slice(0, 10)

export function Dashboard() {
  const [selectedDate, setSelectedDate] = useState(todayStr)
  const [glucose, setGlucose] = useState<GlucoseReading[]>([])
  const [insulin, setInsulin] = useState<InsulinDose[]>([])
  const [heartRate, setHeartRate] = useState<HeartRateReading[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const [start, end] = dateToRange(selectedDate)
    setLoading(true)
    setError(null)

    Promise.all([
      fetchGlucose(start, end),
      fetchInsulin(start, end),
      fetchHeartRate(start, end),
    ])
      .then(([g, i, hr]) => {
        setGlucose(g)
        setInsulin(i)
        setHeartRate(hr)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [selectedDate])

  const [startMs, endMs] = dateToRange(selectedDate).map((d) => d.getTime()) as [number, number]
  const boluses = insulin.filter((d) => d.dose_type !== 'temp_basal')

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, sans-serif', padding: '24px', maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: '#111827', letterSpacing: '-0.3px' }}>BGConnect</h1>
        <DateSelector value={selectedDate} onChange={setSelectedDate} />
      </div>

      {loading && <p style={{ color: '#9ca3af' }}>Loading…</p>}
      {error && <p style={{ color: '#ef4444' }}>Error: {error}</p>}

      {!loading && !error && (
        <section>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 12 }}>
            <h2 style={{ margin: 0, fontSize: 15, fontWeight: 600, color: '#374151' }}>Overview</h2>
            <span style={{ fontSize: 13, color: '#9ca3af' }}>
              {glucose.length} BG readings · {boluses.length} boluses · {heartRate.length} HR samples
            </span>
          </div>
          <BGChart
            glucose={glucose}
            insulin={insulin}
            heartRate={heartRate}
            startMs={startMs}
            endMs={endMs}
          />
        </section>
      )}
    </div>
  )
}
