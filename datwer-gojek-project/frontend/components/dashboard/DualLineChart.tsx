"use client";

import React from "react";
import {
  LineChart,
  Line,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { MoreHorizontal } from "lucide-react";

interface DualLineChartProps {
  title: string;
  data: any[];
  line1Key: string;
  line1Name: string;
  line1Color: string;
  line2Key: string;
  line2Name: string;
  line2Color: string;
}

export default function DualLineChart({
  title,
  data,
  line1Key,
  line1Name,
  line1Color,
  line2Key,
  line2Name,
  line2Color,
}: DualLineChartProps) {
  return (
    <div className="bg-theme-card p-6 rounded-xl border border-theme-border shadow-sm lg:col-span-2 flex flex-col transition-colors duration-300">
      <div className="flex justify-between items-start mb-6">
        <h2 className="text-lg font-semibold text-theme-main">{title}</h2>
        <MoreHorizontal className="w-5 h-5 text-theme-muted cursor-pointer" />
      </div>
      <div className="flex-1 w-full mt-2 relative">
        <ResponsiveContainer width="100%" height={280}>
          <LineChart
            data={data}
            margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="var(--border-color)"
              opacity={0.5}
            />
            <Tooltip
              contentStyle={{
                borderRadius: "8px",
                border: "none",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                backgroundColor: "var(--bg-card)",
                color: "var(--text-main)",
              }}
              labelStyle={{ fontWeight: "bold", marginBottom: "4px" }}
            />
            {/* Garis Utama */}
            <Line
              type="monotone"
              dataKey={line1Key}
              name={line1Name}
              stroke={line1Color}
              strokeWidth={5}
              dot={false}
              activeDot={{
                r: 6,
                fill: line1Color,
                stroke: "var(--bg-card)",
                strokeWidth: 2,
              }}
            />
            {/* Garis Sekunder (Dashed) */}
            <Line
              type="monotone"
              dataKey={line2Key}
              name={line2Name}
              stroke={line2Color}
              strokeWidth={5}
              strokeDasharray="8 8"
              dot={false}
              activeDot={{
                r: 6,
                fill: line2Color,
                stroke: "var(--bg-card)",
                strokeWidth: 2,
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Custom Legend Horizontal */}
      <div className="flex justify-center items-center space-x-6 mt-4">
        <div className="flex items-center text-xs font-medium text-theme-muted">
          <div
            className="w-3 h-3 rounded-full mr-2"
            style={{ backgroundColor: line1Color }}
          ></div>
          {line1Name}
        </div>
        <div className="flex items-center text-xs font-medium text-theme-muted">
          <div
            className="w-3 h-3 rounded-full mr-2"
            style={{ backgroundColor: line2Color }}
          ></div>
          {line2Name}
        </div>
      </div>
    </div>
  );
}
