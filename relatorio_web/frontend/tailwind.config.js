/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        inteli: {
          // Paleta espelhando o slide do MBA (header azul-escuro, vermelho/coral logo)
          'navy': '#1B1F3B',
          'navy-dark': '#0F1226',
          'navy-light': '#2D2D6B',
          'petrol': '#1F4E5F',
          'red': '#E63946',
          'red-dark': '#C42E3B',
          'gray-bg': '#F4F5F7',
          'gray-card': '#FFFFFF',
          'gray-text': '#2C2C2C',
          'gray-muted': '#6B7280',
          'gray-border': '#E5E7EB',
        },
        // Cores funcionais para risco
        risk: {
          low: '#27AE60',
          medium: '#F39C12',
          high: '#E74C3C',
          neutral: '#3498DB',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        display: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        'card-hover': '0 4px 12px 0 rgba(0, 0, 0, 0.08)',
      },
    },
  },
  plugins: [],
}
