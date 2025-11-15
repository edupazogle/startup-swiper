# Dockerfile for frontend
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY app/startup-swipe-schedu/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY app/startup-swipe-schedu/ .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve to run the application
RUN npm install -g serve

# Copy built application from build stage
COPY --from=build /app/dist ./dist

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# Run application
CMD ["serve", "-s", "dist", "-l", "3000"]
