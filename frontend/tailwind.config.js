/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  prefix: 'tw-', // Add prefix to avoid conflicts with Vuetify
  corePlugins: {
    preflight: false, // Disable Tailwind's reset to avoid conflicts with Vuetify
  },
  theme: {
    extend: {
      colors: {
        primary: '#1867C0',
        secondary: '#5CBBF6',
        accent: '#82B1FF',
        error: '#FF5252',
        info: '#2196F3',
        success: '#4CAF50',
        warning: '#FFC107',
      },
      fontFamily: {
        sans: ['Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}