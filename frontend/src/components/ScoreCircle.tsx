interface Props {
  score: number
  size?: 'sm' | 'md' | 'lg'
}

type Tier = 'strong' | 'good' | 'partial' | 'poor'

const TIER_CONFIG: Record<Tier, { color: string; bg: string }> = {
  strong:  { color: '#10b981', bg: '#ecfdf5' },
  good:    { color: '#3b82f6', bg: '#eff6ff' },
  partial: { color: '#f59e0b', bg: '#fffbeb' },
  poor:    { color: '#ef4444', bg: '#fef2f2' },
}

const SIZES = {
  sm: { dim: 60, stroke: 5, fontSize: 13 },
  md: { dim: 80, stroke: 6, fontSize: 18 },
  lg: { dim: 100, stroke: 7, fontSize: 22 },
}

function getTier(score: number): Tier {
  if (score >= 80) return 'strong'
  if (score >= 60) return 'good'
  if (score >= 40) return 'partial'
  return 'poor'
}

export default function ScoreCircle({ score, size = 'md' }: Props) {
  const tier = getTier(score)
  const { color, bg } = TIER_CONFIG[tier]
  const { dim, stroke, fontSize } = SIZES[size]
  const radius = (dim - stroke * 2) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: dim, height: dim }}>
      <svg width={dim} height={dim} className="-rotate-90">
        <circle cx={dim / 2} cy={dim / 2} r={radius} fill={bg} stroke="#e5e7eb" strokeWidth={stroke} />
        <circle
          cx={dim / 2}
          cy={dim / 2}
          r={radius}
          fill="transparent"
          stroke={color}
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <span className="absolute font-bold" style={{ fontSize, color }}>
        {Math.round(score)}
      </span>
    </div>
  )
}
