/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    'client/templates/client/*.html',
    'core/templates/core/*.html',
    'team/templates/team/*.html',
    'leads/templates/leads/*.html',
    'dashboard/templates/dashboard/*.html',
    'userprofile/templates/userprofile/*.html',
    'core/templates/core/partials/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

