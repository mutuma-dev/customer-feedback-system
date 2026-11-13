# Recipe for the frontend container image. It has TWO stages ("multi-stage build"):
# stage 1 builds the app, stage 2 keeps only what is needed to RUN it (a much smaller image).

# ---------- Stage 1: build ----------
FROM node:22-alpine AS build
WORKDIR /app

# The backend address is baked into the website at build time.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Copy the dependency lists first so Docker can cache the (slow) install step.
COPY package*.json ./
RUN npm ci

# Copy the code and build the production version.
COPY . .
RUN npm run build

# ---------- Stage 2: run ----------
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production PORT=3000 HOSTNAME=0.0.0.0

# Copy only the build output from stage 1 (no source code, no dev tools).
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
