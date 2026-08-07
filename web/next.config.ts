import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      // Statisk EM-analyse ligger i public/EM2026/index.html.
      // Rewrite gir ren URL uten /index.html, og /em2026 virker også.
      { source: "/EM2026", destination: "/EM2026/index.html" },
      { source: "/em2026", destination: "/EM2026/index.html" },
    ];
  },

  async headers() {
    // Upublisert side: skal kun nås av den som har lenken.
    // X-Robots-Tag gjelder også ved direkte filhenting, der meta-taggen
    // i <head> ikke nødvendigvis blir lest.
    const noindex = [
      { key: "X-Robots-Tag", value: "noindex, nofollow, noarchive, nosnippet" },
    ];
    return [
      { source: "/EM2026", headers: noindex },
      { source: "/em2026", headers: noindex },
      { source: "/EM2026/:path*", headers: noindex },
    ];
  },
};

export default nextConfig;
