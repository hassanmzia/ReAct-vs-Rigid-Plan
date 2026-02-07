FROM node:18-alpine AS builder

WORKDIR /app

ARG REACT_APP_API_URL=http://172.168.1.95:8042
ARG REACT_APP_WS_URL=ws://172.168.1.95:8042
ARG REACT_APP_SITE_URL=http://172.168.1.95:3081

ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_WS_URL=$REACT_APP_WS_URL
ENV REACT_APP_SITE_URL=$REACT_APP_SITE_URL
ENV CI=false
ENV DISABLE_ESLINT_PLUGIN=true

COPY package.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
