/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        artisan: {
          50: '#fffbeb',
          100: '#fef3c7',
          500: '#d97706',
          600: '#b45309',
          700: '#92400e',
          800: '#78350f',
          900: '#451a03',
        },
        terracotta: {
          500: '#e05638',
          600: '#c84326',
        },
        indigoCraft: {
          600: '#1e3a8a',
          700: '#1e1b4b',
        }
      }
    },
  },
  plugins: [],
}
