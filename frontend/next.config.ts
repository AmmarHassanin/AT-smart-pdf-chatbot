import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: "standalone",
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async rewrites() {
    // Only used when NEXT_PUBLIC_API_URL is empty (same-origin mode, e.g. in
    // Docker/Coolify): proxies browser calls to the backend container over
    // the internal compose network, so only one public domain is needed.
    if (process.env.NEXT_PUBLIC_API_URL) return [];
    const backend = process.env.BACKEND_INTERNAL_URL || "http://backend:8000";
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};

export default nextConfig;
