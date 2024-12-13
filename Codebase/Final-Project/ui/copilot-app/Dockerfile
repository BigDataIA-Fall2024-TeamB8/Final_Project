# Use the official Node.js 18 image as the base
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Install necessary build tools (useful for some dependencies)
RUN apk add --no-cache libc6-compat bash

# Copy package.json and package-lock.json first (leverage Docker cache)
COPY package*.json ./

# Install all dependencies (including devDependencies)
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port Next.js will run on
EXPOSE 3000

# Command to run Next.js in development mode
CMD ["npm", "run", "dev"]
