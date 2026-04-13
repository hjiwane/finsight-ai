import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import type { Transaction } from "../types/index"
import { formatINR } from "../types/index"

interface Props {
  transactions: Transaction[]
}

export function SpendingChart({ transactions }: Props) {
  const data = [...transactions]
    .slice(0, 20)
    .reverse()
    .map((t, i) => ({
      i,
      amount: t.amount,
    }))

  return (
    <ResponsiveContainer width="100%" height={140}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
        <defs>
          <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#7F77DD" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#7F77DD" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis dataKey="i" hide />
        <YAxis tickFormatter={(v) => `₹${v}`} tick={{ fontSize: 10 }} />
        <Tooltip
          formatter={(v: number) => formatINR(v)}
          contentStyle={{ fontSize: 12, borderRadius: 6 }}
        />
        <Area
          type="monotone"
          dataKey="amount"
          stroke="#7F77DD"
          strokeWidth={2}
          fill="url(#grad)"
          dot={false}
          animationDuration={300}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}