FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# change ownership to node user
RUN chown -R node:node /app

# switch to non-root user
USER node

EXPOSE 3000

CMD ["node", "server.js"]

