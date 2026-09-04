/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        groww: {
          green: "#00d09c",
          darkGreen: "#00b386",
          red: "#eb5b3c",
          darkRed: "#d44527",
          blue: "#5367ff",
        },
      },
    },
  },
  plugins: [],
};
