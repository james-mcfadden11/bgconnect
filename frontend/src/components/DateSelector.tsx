interface Props {
  value: string        // 'YYYY-MM-DD'
  onChange: (date: string) => void
}

const today = new Date().toISOString().slice(0, 10)

function shift(dateStr: string, days: number): string {
  const [y, m, d] = dateStr.split('-').map(Number)
  const date = new Date(y, m - 1, d + days)
  return date.toISOString().slice(0, 10)
}

export function DateSelector({ value, onChange }: Props) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
      <button
        onClick={() => onChange(shift(value, -1))}
        style={navBtn}
        aria-label="Previous day"
      >
        ‹
      </button>
      <input
        type="date"
        value={value}
        max={today}
        onChange={(e) => onChange(e.target.value)}
        style={{
          border: '1px solid #d1d5db',
          borderRadius: 6,
          padding: '6px 10px',
          fontSize: 14,
          color: '#374151',
          cursor: 'pointer',
        }}
      />
      <button
        onClick={() => onChange(shift(value, 1))}
        disabled={value >= today}
        style={{ ...navBtn, opacity: value >= today ? 0.3 : 1 }}
        aria-label="Next day"
      >
        ›
      </button>
    </div>
  )
}

const navBtn: React.CSSProperties = {
  padding: '6px 10px',
  border: '1px solid #d1d5db',
  borderRadius: 6,
  background: 'white',
  color: '#374151',
  cursor: 'pointer',
  fontSize: 16,
  lineHeight: 1,
}
