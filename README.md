# WasteWise

A premium futuristic eco-app for waste classification, carbon tracking, and green rewards.

## Project Structure

- `backend/`: FastAPI application and SQLite database.
- `cinematic-scroll/public/`: Static frontend files (HTML/JS) served by the backend.

## Hosting with Docker

The project is ready for containerized hosting (e.g., Google Cloud Run, AWS App Runner).

### Local Testing with Docker Compose

1. Install [Docker](https://docs.docker.com/get-docker/).
2. Run the following command in the root directory:
   ```bash
   docker-compose up --build
   ```
3. Access the app at `http://localhost:8000`.

### Manual Docker Build

```bash
docker build -t wastewise .
docker run -p 8000:8000 wastewise
```

## Hosting on Google Cloud Run

1. Build and push the image to Google Artifact Registry:
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT-ID]/wastewise
   ```
2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy wastewise --image gcr.io/[PROJECT-ID]/wastewise --platform managed
   ```

## Local Development (without Docker)

### Backend
1. Navigate to `backend/`.
2. Create a virtual environment: `python -m venv venv`.
3. Activate it: `venv\Scripts\activate`.
4. Install dependencies: `pip install -r requirements.txt`.
5. Run: `python main.py`.

### Frontend
The frontend consists of static files in `cinematic-scroll/public/`. They are automatically served by the FastAPI backend at `http://localhost:8000`.

---
Built with ❤️ by the WasteWise Team.
