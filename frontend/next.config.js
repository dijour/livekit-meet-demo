/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  productionBrowserSourceMaps: true,
  typescript: {
    // !! WARN !!
    // Dangerously allow production builds to successfully complete even if
    // your project has TypeScript errors.
    // !! WARN !!
    ignoreBuildErrors: true,
  },
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
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

    // Improve module resolution for vendor directory
    const path = require('path');
    
    // Debug logging for Vercel
    console.log('Next.js config __dirname:', __dirname);
    console.log('Resolved @ path:', path.resolve(__dirname));
    
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
      '@/vendor': path.resolve(__dirname, 'vendor'),
      '@/lib': path.resolve(__dirname, 'lib'),
      '@/components': path.resolve(__dirname, 'components'),
      '@/app': path.resolve(__dirname, 'app'),
      '@/styles': path.resolve(__dirname, 'styles'),
      '@/hooks': path.resolve(__dirname, 'hooks'),
      '@/types': path.resolve(__dirname, 'types'),
    };
    
    // Debug: log the final alias configuration
    console.log('Final webpack aliases:', config.resolve.alias);
    
    // Ensure vendor directory is properly resolved
    config.resolve.modules = [
      ...(config.resolve.modules || []),
      require('path').resolve(__dirname, 'vendor'),
      'node_modules'
    ];
    
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
