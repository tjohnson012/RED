/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0A0A0A',
        surface: '#141414',
        border: '#262626',
        'text-primary': '#FAFAFA',
        'text-secondary': '#A1A1A1',
        'red-primary': '#DC2626',
        'red-hover': '#B91C1C',
        success: '#22C55E',
        failure: '#71717A',
        severity: {
          critical: '#DC2626',
          high: '#F97316',
          medium: '#EAB308',
          low: '#22C55E',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
