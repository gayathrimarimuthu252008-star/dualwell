/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dualbg: "#F7F8FC",
        dualcard: "#FFFFFF",
        primary: {
          DEFAULT: "#4F7DF3",
          hover: "#3B66D4",
          soft: "#EAF0FF",
        },
        mint: "#DDF7E8",
        cream: "#FFF4DF",
        dualtext: {
          primary: "#263247",
          secondary: "#748096",
        },
        bordercolor: "#E5E9F2",
        risk: {
          green: "#239B68",
          yellow: "#E6A23C",
          red: "#E05252",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
