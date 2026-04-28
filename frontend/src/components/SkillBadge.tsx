interface Props {
  skill: string
  variant: 'matched' | 'missing' | 'bonus'
}

const CLASSES: Record<Props['variant'], string> = {
  matched: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
  missing: 'bg-red-50 text-red-700 border border-red-200',
  bonus:   'bg-blue-50 text-blue-700 border border-blue-200',
}

export default function SkillBadge({ skill, variant }: Props) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${CLASSES[variant]}`}>
      {skill}
    </span>
  )
}
