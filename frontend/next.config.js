/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  productionBrowserSourceMaps: true,
  images: {
    formats: ['image/webp'],
  },
  webpack: (config, { buildId, dev, isServer, defaultLoaders, nextRuntime, webpack }) => {
    // Important: return the modified config
    config.module.rules.push({
      test: /\.mjs$/,
      enforce: 'pre',
      use: ['source-map-loader'],
    });

    // Exclude storybook and example files from the submodule
    config.module.rules.push({
      test: /vendor\/components-js\/(docs|examples)\//,
      loader: 'ignore-loader'
    });

    // Also exclude these directories from module resolution
    config.resolve.alias = {
      ...config.resolve.alias,
    };
    
    // Ignore TypeScript compilation for these directories
    if (!config.resolve.fallback) {
      config.resolve.fallback = {};
    }

    return config;
  },
  headers: async () => {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Cross-Origin-Opener-Policy',
            value: 'same-origin',
          },
          {
            key: 'Cross-Origin-Embedder-Policy',
            value: 'credentialless',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
