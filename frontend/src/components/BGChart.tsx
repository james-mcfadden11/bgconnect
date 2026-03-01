import {
  ComposedChart,
  Line,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import type { GlucoseReading, InsulinDose, HeartRateReading } from '../api/client'

interface Props {
  glucose: GlucoseReading[]
  insulin: InsulinDose[]
  heartRate: HeartRateReading[]
  startMs: number
  endMs: number
}

interface ChartPoint {
  time: number
  bg?: number
  hr?: number
}

function mergeData(glucose: GlucoseReading[], heartRate: HeartRateReading[]): ChartPoint[] {
  const map = new Map<number, ChartPoint>()

  for (const g of glucose) {
    const t = new Date(g.timestamp).getTime()
    map.set(t, { time: t, bg: g.value_mgdl })
  }

  for (const h of heartRate) {
    const t = new Date(h.timestamp).getTime()
    map.set(t, { ...(map.get(t) ?? { time: t }), hr: h.bpm })
  }

  return Array.from(map.values()).sort((a, b) => a.time - b.time)
}

function formatTick(timestamp: number): string {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function BGChart({ glucose, insulin, heartRate, startMs, endMs }: Props) {
  const merged = mergeData(glucose, heartRate)

  const bolusPoints = insulin
    .filter((d) => d.dose_type !== 'temp_basal')
    .map((d) => ({
      time: new Date(d.timestamp).getTime(),
      y: 45,
    }))

  return (
    <ResponsiveContainer width="100%" height={440}>
      <ComposedChart data={merged} margin={{ top: 10, right: 56, bottom: 10, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
        <XAxis
          dataKey="time"
          type="number"
          scale="time"
          domain={[startMs, endMs]}
          tickFormatter={formatTick}
          tick={{ fontSize: 11, fill: '#6b7280' }}
          tickCount={9}
        />
        <YAxis
          yAxisId="bg"
          orientation="left"
          domain={[40, 400]}
          tickCount={8}
          tick={{ fontSize: 11, fill: '#6b7280' }}
          label={{ value: 'mg/dL', angle: -90, position: 'insideLeft', offset: 10, style: { fontSize: 11, fill: '#9ca3af' } }}
        />
        <YAxis
          yAxisId="hr"
          orientation="right"
          domain={[40, 200]}
          tickCount={6}
          tick={{ fontSize: 11, fill: '#6b7280' }}
          label={{ value: 'bpm', angle: 90, position: 'insideRight', offset: 10, style: { fontSize: 11, fill: '#9ca3af' } }}
        />
        <ReferenceLine yAxisId="bg" y={70} stroke="#ef4444" strokeDasharray="4 4" strokeOpacity={0.7} />
        <ReferenceLine yAxisId="bg" y={180} stroke="#f97316" strokeDasharray="4 4" strokeOpacity={0.7} />
        <Line
          yAxisId="bg"
          dataKey="bg"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
          connectNulls
          isAnimationActive={false}
          name="BG"
        />
        <Line
          yAxisId="hr"
          dataKey="hr"
          stroke="#f472b6"
          strokeWidth={1.5}
          dot={false}
          connectNulls
          isAnimationActive={false}
          name="HR"
        />
        <Scatter
          yAxisId="bg"
          data={bolusPoints}
          dataKey="y"
          fill="#f97316"
          isAnimationActive={false}
          name="Bolus"
        />
        <Legend
          formatter={(value) => <span style={{ fontSize: 12, color: '#374151' }}>{value}</span>}
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
