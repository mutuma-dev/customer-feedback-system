// Next.js settings.
/** @type {import('next').NextConfig} */
const nextConfig = {
  // "standalone" makes `npm run build` produce a small self-contained server folder,
  // which the Dockerfile copies into the final image.
  output: "standalone",
};

export default nextConfig;
