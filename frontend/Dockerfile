# --- Build stage ---
FROM node:22-alpine AS build

WORKDIR /app

ARG VITE_API_URL
ARG VITE_WS_URL

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

# --- Serve stage ---
FROM nginx:alpine

# Copy custom nginx config (uses envsubst for $PORT)
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copy built SPA
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

# nginx:alpine image auto-runs envsubst on /etc/nginx/templates/*.template
CMD ["nginx", "-g", "daemon off;"]
