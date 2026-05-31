"use client";

import React from "react";
import { AreaChart, Area, XAxis, Tooltip, ResponsiveContainer } from "recharts";
import { MoreHorizontal } from "lucide-react";

interface TrendAreaChartProps {
  title: string;
  description: string;
  data: any[];
  dataKey: string;
  xAxisKey?: string;
  color?: string;
  valuePrefix?: string;
  valueSuffix?: string;
}

export default function TrendAreaChart({
  title,
  description,
  data,
  dataKey,
  xAxisKey = "date",
  color = "var(--color-primary)",
  valuePrefix = "",
  valueSuffix = "",
}: TrendAreaChartProps) {
  // Membuat ID gradient unik agar tidak bentrok jika ada 2 chart di 1 halaman
  const gradientId = `colorGradient-${dataKey}`;

  return (
    <div className="bg-theme-card p-6 rounded-xl border border-theme-border shadow-sm lg:col-span-2 flex flex-col transition-colors duration-300">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-lg font-semibold text-theme-main">{title}</h2>
          <p className="text-sm text-theme-muted">{description}</p>
        </div>
        <MoreHorizontal className="w-5 h-5 text-theme-muted cursor-pointer" />
      </div>
      <div className="w-full mt-4">
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey={xAxisKey}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: "var(--text-muted)" }}
              dy={10}
            />
            <Tooltip
              contentStyle={{
                borderRadius: "8px",
                border: "none",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                backgroundColor: "var(--bg-card)",
                color: "var(--text-main)",
              }}
              formatter={(value: any) => [
                `${valuePrefix}${new Intl.NumberFormat("id-ID").format(Number(value))} ${valueSuffix}`,
                "", // Menyembunyikan nama key default
              ]}
              labelStyle={{ fontWeight: "bold" }}
            />
            <Area
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              strokeWidth={3}
              fillOpacity={1}
              fill={`url(#${gradientId})`}
              activeDot={{
                r: 6,
                fill: color,
                stroke: "var(--bg-card)",
                strokeWidth: 2,
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
