const ENV_VARS = {
  NODE_ENV: process.env.NODE_ENV,
  NEXT_PUBLIC_VERCEL_ENV: process.env.NEXT_PUBLIC_VERCEL_ENV,
  NEXT_PUBLIC_API_BASE_URL:
    process.env.NEXT_PUBLIC_API_BASE_URL || process.env.API_BASE_URL
}

export default ENV_VARS
