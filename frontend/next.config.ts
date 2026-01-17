import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  // Turbopack configuration (Next.js 16 uses Turbopack by default)
  turbopack: {
    // Turbopack handles module resolution automatically
    // The main fix is ensuring you run 'npm run dev' from the frontend directory
  },
};

export default nextConfig;
