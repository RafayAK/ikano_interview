FROM node:22-bookworm-slim

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

EXPOSE 4321
# Keep the server in the foreground so Docker can manage its lifecycle.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4321"]
