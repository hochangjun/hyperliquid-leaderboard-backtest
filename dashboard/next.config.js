/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    BACKEND_URL: process.env.BACKEND_URL,
    LEADERBOARD_URL: process.env.LEADERBOARD_URL,
  },
}

module.exports = nextConfig