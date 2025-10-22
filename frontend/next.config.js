/** @type {import('next').NextConfig} */

const nextConfig = {
  typescript: {
    // Allow production builds to successfully complete even if there are type errors.
    ignoreBuildErrors: true
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'avatars.githubusercontent.com',
        port: '',
        pathname: '**'
      }
    ]
  },
  productionBrowserSourceMaps: process.env.NODE_ENV === 'production',
  webpack: (config, { isServer, dev }) => {
    if (!dev && isServer) {
      config.devtool = 'source-map'
    }
    // Suppress TS type-checking errors from react-markdown type packages during build
    config.ignoreWarnings = [
      ...(config.ignoreWarnings || []),
      {
        module: /react-markdown[\\/]/,
        message:
          /Type .* does not satisfy the constraint|Cannot find namespace 'JSX'/
      }
    ]
    return config
  }
}

const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true'
})

module.exports = withBundleAnalyzer(nextConfig)
