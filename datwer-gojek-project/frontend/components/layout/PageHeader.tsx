"use client";

import React, { useState, useEffect } from "react";
import { Calendar, MapPin, Download, Sun, Moon } from "lucide-react";

interface PageHeaderProps {
  title: string;
  description: string;
}

export default function PageHeader({ title, description }: PageHeaderProps) {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    if (document.documentElement.classList.contains("dark")) {
      setIsDarkMode(true);
    }
  }, []);

  const toggleTheme = () => {
    if (isDarkMode) {
      document.documentElement.classList.remove("dark");
      setIsDarkMode(false);
    } else {
      document.documentElement.classList.add("dark");
      setIsDarkMode(true);
    }
  };

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-theme-main">
          {title}
        </h1>
        <p className="text-sm text-theme-muted mt-1">{description}</p>
      </div>
      <div className="flex items-center space-x-3">
        <button className="flex items-center px-4 py-2 bg-theme-card border border-theme-border rounded-md text-sm font-medium text-theme-main shadow-sm hover:opacity-80 transition-opacity">
          <Calendar className="w-4 h-4 mr-2 text-theme-muted" />
          Last 30 Days
        </button>
        <button className="flex items-center px-4 py-2 bg-theme-card border border-theme-border rounded-md text-sm font-medium text-theme-main shadow-sm hover:opacity-80 transition-opacity">
          <MapPin className="w-4 h-4 mr-2 text-theme-muted" />
          All Cities
        </button>
        <button className="flex items-center px-4 py-2 bg-theme-main text-theme-base rounded-md text-sm font-medium shadow-sm hover:opacity-90 transition-opacity">
          <Download className="w-4 h-4 mr-2" />
          Export
        </button>

        <button
          onClick={toggleTheme}
          className="flex items-center justify-center p-2.5 bg-theme-card border border-theme-border rounded-md text-theme-muted hover:text-theme-main shadow-sm transition-all"
        >
          {isDarkMode ? (
            <Sun className="w-4 h-4" />
          ) : (
            <Moon className="w-4 h-4" />
          )}
        </button>
      </div>
    </div>
  );
}
