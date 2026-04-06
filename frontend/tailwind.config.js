/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: '#ffffff',
          secondary: '#f4f4f5',
          tertiary: '#e4e4e7',
        },
        surface: {
          DEFAULT: '#fafafa',
          hover: '#f4f4f5',
        },
        border: {
          DEFAULT: '#e4e4e7',
          light: '#d4d4d8',
        },
        primary: {
          DEFAULT: '#0891b2',
          hover: '#0e7490',
          muted: '#06b6d4',
        },
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6',
        text: {
          primary: '#18181b',
          secondary: '#52525b',
          muted: '#71717a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '8px',
      },
    },
  },
  plugins: [],
}