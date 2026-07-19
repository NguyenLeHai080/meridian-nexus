FROM node:24-alpine@sha256:a0b9bf06e4e6193cf7a0f58816cc935ff8c2a908f81e6f1a95432d679c54fbfd AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

ARG VITE_API_URL=/api/v1
ARG VITE_BACKEND_URL=/
ARG VITE_APP_NAME="Meridian Nexus"
ENV VITE_API_URL=$VITE_API_URL \
    VITE_BACKEND_URL=$VITE_BACKEND_URL \
    VITE_APP_NAME=$VITE_APP_NAME
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.29-alpine@sha256:0c79d56aee561a1d81c63f00eee5fb5fe29279560cdc55e91425133104c7fbe6

USER root
RUN apk upgrade --no-cache
USER nginx

COPY deployment/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
