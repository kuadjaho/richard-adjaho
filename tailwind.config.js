module.exports = {
  content: ["./index.html", "./assets/js/**/*.js"],
  theme: {
    extend: {
      colors: { ivoire: "#faf8f4", sable: "#efe9df", encre: "#1a1d23", foret: "#14532d", or: "#b8860b" },
      fontFamily: {
        serif: ['"Playfair Display"', "Georgia", "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
};
