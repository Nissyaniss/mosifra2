const defaultTheme = require("tailwindcss/defaultTheme");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/templates/**/*.{html,js}",
    "./src/accounts/templates/**/*.{html,js}",
    "./src/profiles/templates/**/*.{html,js}",
    "./src/offers/templates/**/*.{html,js}",
    "./src/invitations/templates/**/*.{html,js}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", ...defaultTheme.fontFamily.sans],
      },
      colors: {
        brand: {
          primary: "#567BCD",
          primaryDark: "#4d6db5ff",
          surface: "#DFEAFF",
        },
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
  ],
}
