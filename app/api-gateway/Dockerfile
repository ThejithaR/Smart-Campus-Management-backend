# Use a Node.js base image (choose a version appropriate for your project)
FROM node:18-alpine 

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
# This allows caching of node_modules layer if package files don't change
COPY package.json ./
COPY package-lock.json ./ 

# Install dependencies
RUN npm install --production # Or `yarn install --production` if using yarn
# Use --production flag to install only production dependencies

# Copy the rest of the application code
COPY . .

# Expose the port the application listens on
# Standard practice is often 3000, but I'll assume 8000 for consistency with other services
EXPOSE 8000

# Command to run the application
# Assumes your main entry file is server.js
CMD ["node", "server.js"]