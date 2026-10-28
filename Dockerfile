# ===============================
# Stage 1: Build React Frontend
# ===============================

FROM node:24 AS frontend

WORKDIR /frontend

COPY UI/package*.json ./

RUN npm install

COPY UI/ .

RUN npm run build


# ===============================
# Stage 2: Backend
# ===============================

FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy React build
COPY --from=frontend /frontend/dist ./static

RUN mkdir -p snapshots clips

EXPOSE 7860

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","7860"]