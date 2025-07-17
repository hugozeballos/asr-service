# Stage 1: builder
FROM node:18-alpine AS builder
WORKDIR /app

# 1) Declaramos el build-arg para la URL de la API
ARG NEXT_PUBLIC_API_BASE_URL
# 2) La convertimos en ENV para que Next la recoja al build
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

COPY package*.json ./
RUN npm install

COPY . ./
RUN npm run build

# Stage 2: runtime
FROM node:18-alpine
WORKDIR /app

ENV NODE_ENV=production \
    PORT=8080

# Copiamos solo los artefactos necesarios
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 8080

CMD ["npm", "start", "--", "-p", "8080"]
