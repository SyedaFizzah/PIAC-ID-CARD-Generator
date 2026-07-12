/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        pia: {
          green: "#0A5C36",
          greenDark: "#06432A",
          gold: "#A6873C",
          cream: "#F5F0E6",
          tint: "#EAF2EC",
        },
      },
    },
  },
  plugins: [],
};
