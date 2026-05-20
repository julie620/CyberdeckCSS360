# Dockerfile
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY api/ ./api/
RUN pip install -r api/requirements.txt
COPY --from=frontend-builder /app/dist ./dist
EXPOSE 5000
CMD ["python", "api/api.py"]