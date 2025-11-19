/**
 * Cumulative return line chart component
 */
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { formatPercent, formatDate } from '@/lib/utils';

interface DataPoint {
  date: string;
  [key: string]: number | string;
}

interface CumulativeReturnChartProps {
  data: DataPoint[];
  lines: {
    dataKey: string;
    name: string;
    color: string;
  }[];
  height?: number;
  yAxisLabel?: string;
}

export default function CumulativeReturnChart({
  data,
  lines,
  height = 400,
  yAxisLabel = 'Cumulative Return'
}: CumulativeReturnChartProps) {
  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="text-sm font-semibold mb-1">{formatDate(label)}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {formatPercent(entry.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis
          dataKey="date"
          tickFormatter={(value) => {
            const date = new Date(value);
            return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
          }}
          stroke="#666"
          style={{ fontSize: '12px' }}
        />
        <YAxis
          tickFormatter={(value) => formatPercent(value, 0)}
          label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }}
          stroke="#666"
          style={{ fontSize: '12px' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: '14px' }}
          iconType="line"
        />
        {lines.map((line) => (
          <Line
            key={line.dataKey}
            type="monotone"
            dataKey={line.dataKey}
            name={line.name}
            stroke={line.color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
