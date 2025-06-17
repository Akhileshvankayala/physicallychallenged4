/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#0056D2',
        secondary: '#009688',
        accent: '#FF5722',
        background: '#F8F9FA',
        text: '#212529',
      },
    },
  },
  plugins: [],
};