"use client";

import React from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

interface DonutChartProps {
  title: string;
  description: string;
  data: any[];
  dataKey: string;
  nameKey?: string;
  centerValue: string | number;
  centerLabel: string;
  colors?: string[];
}

export default function DonutChart({
  title,
  description,
  data,
  dataKey,
  nameKey = "name",
  centerValue,
  centerLabel,
  colors = [
    "var(--color-primary)",
    "var(--color-secondary)",
    "var(--color-tertiary)",
    "var(--color-quaternary)",
  ],
}: DonutChartProps) {
  return (
    <div className="bg-theme-card p-6 rounded-xl border border-theme-border shadow-sm flex flex-col transition-colors duration-300">
      <div className="mb-2">
        <h2 className="text-lg font-semibold text-theme-main">{title}</h2>
        <p className="text-sm text-theme-muted">{description}</p>
      </div>
      <div className="flex-1 w-full flex flex-col items-center justify-center relative mt-6">
        <div className="absolute top-[40%] left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none z-10">
          <span className="block text-2xl font-bold text-theme-main">
            {centerValue}
          </span>
          <span className="block text-xs text-theme-muted font-medium mt-1">
            {centerLabel}
          </span>
        </div>

        <div className="w-full">
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={data}
                innerRadius={70}
                outerRadius={90}
                paddingAngle={4}
                dataKey={dataKey}
                nameKey={nameKey}
                stroke="none"
                cx="50%"
                cy="50%"
              >
                {data.map((entry: any, index: number) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={colors[index % colors.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: any) =>
                  new Intl.NumberFormat("id-ID").format(Number(value))
                }
                contentStyle={{
                  borderRadius: "8px",
                  border: "none",
                  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                  backgroundColor: "var(--bg-card)",
                  color: "var(--text-main)",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Custom Grid Legend */}
        <div className="grid grid-cols-2 gap-x-8 gap-y-3 w-full px-2 mt-6">
          {data.map((item: any, idx: number) => (
            <div key={idx} className="flex items-center">
              <div
                className="w-3 h-3 rounded-full mr-2 shrink-0"
                style={{ backgroundColor: colors[idx % colors.length] }}
              ></div>
              <div className="flex flex-col">
                <span className="text-sm font-medium text-theme-main leading-none">
                  {item[nameKey]}
                </span>
                <span className="text-xs text-theme-muted mt-1">
                  {item.percentage ? `${item.percentage}%` : ""}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
