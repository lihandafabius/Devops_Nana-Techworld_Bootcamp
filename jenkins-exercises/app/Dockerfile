# Build + Test
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# run test
RUN npm run test

# Production
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev # exclude dev dependencies like jest

COPY . .

# change ownership to node user
RUN chown -R node:node /app

# switch to non-root user
USER node

EXPOSE 3000

CMD ["node", "server.js"]

