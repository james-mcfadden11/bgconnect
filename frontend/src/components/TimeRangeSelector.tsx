export type TimeRange = '3h' | '6h' | '12h' | '24h'

interface Props {
  value: TimeRange
  onChange: (range: TimeRange) => void
}

const OPTIONS: TimeRange[] = ['3h', '6h', '12h', '24h']

export function TimeRangeSelector({ value, onChange }: Props) {
  return (
    <div style={{ display: 'flex', gap: 4 }}>
      {OPTIONS.map((range) => (
        <button
          key={range}
          onClick={() => onChange(range)}
          style={{
            padding: '6px 16px',
            border: '1px solid',
            borderColor: value === range ? '#3b82f6' : '#d1d5db',
            background: value === range ? '#3b82f6' : 'white',
            color: value === range ? 'white' : '#374151',
            borderRadius: 6,
            cursor: 'pointer',
            fontSize: 14,
            fontWeight: value === range ? 600 : 400,
          }}
        >
          {range}
        </button>
      ))}
    </div>
  )
}
