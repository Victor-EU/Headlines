FROM node:20-alpine AS base

WORKDIR /app

# Dev stage — used by docker-compose
FROM base AS dev
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
ENV HOSTNAME=0.0.0.0
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Build stage
FROM base AS builder
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM base AS production
ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
