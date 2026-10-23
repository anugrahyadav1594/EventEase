/** Reusable chart components (all data comes from the backend). */
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

const PALETTE = ['#2563eb', '#0ea5e9', '#14b8a6', '#8b5cf6', '#f59e0b', '#ec4899', '#22c55e', '#64748b']

const axisStyle = { fontSize: 11, fill: '#7b8798' }

const tooltipStyle = {
  contentStyle: {
    borderRadius: 10,
    border: '1px solid #e2e8f0',
    fontSize: 12,
    boxShadow: '0 8px 24px rgba(15,23,42,0.12)',
  },
}

interface BarCardProps {
  data: Record<string, any>[]
  xKey: string
  bars: { key: string; color: string; name: string }[]
  stacked?: boolean
  height?: number
  valueFormatter?: (value: number) => string
}

export function BarCard({ data, xKey, bars, stacked = false, height = 270, valueFormatter }: BarCardProps) {
  return (
    <div className="chart-box" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: -18, bottom: 46 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4" vertical={false} />
          <XAxis
            dataKey={xKey}
            tick={axisStyle}
            angle={-28}
            textAnchor="end"
            interval={0}
            height={54}
            tickFormatter={(value: string) => (value.length > 16 ? `${value.slice(0, 15)}…` : value)}
          />
          <YAxis tick={axisStyle} tickFormatter={(value: number) => valueFormatter ? valueFormatter(value) : String(value)} />
          <Tooltip
            {...tooltipStyle}
            formatter={(value: any) => [valueFormatter ? valueFormatter(Number(value)) : value, '']}
          />
          {bars.length > 1 ? <Legend wrapperStyle={{ fontSize: 12 }} /> : null}
          {bars.map((bar) => (
            <Bar
              key={bar.key}
              dataKey={bar.key}
              name={bar.name}
              fill={bar.color}
              radius={[5, 5, 0, 0]}
              stackId={stacked ? 'stack' : undefined}
              maxBarSize={46}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function DonutCard({
  data,
  nameKey,
  valueKey,
  height = 270,
  valueFormatter,
}: {
  data: Record<string, any>[]
  nameKey: string
  valueKey: string
  height?: number
  valueFormatter?: (value: number) => string
}) {
  return (
    <div className="chart-box" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={nameKey}
            innerRadius="52%"
            outerRadius="80%"
            paddingAngle={2}
            stroke="#fff"
            strokeWidth={2}
          >
            {data.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} />
            ))}
          </Pie>
          <Tooltip
            {...tooltipStyle}
            formatter={(value: any, _name: any, item: any) => [
              valueFormatter ? valueFormatter(Number(value)) : value,
              item?.payload?.[nameKey] ?? '',
            ]}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

export { PALETTE }
