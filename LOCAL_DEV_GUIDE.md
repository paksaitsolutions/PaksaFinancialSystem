# PaksaFinancialSystem: Local Development Guide

This guide will help you run the full project (frontend, backend, database, and Nginx) locally for development and testing.

---

## 1. Prerequisites
- **Node.js** (v16+ recommended)
- **npm** (v8+ recommended)
- **Python** (v3.9+ recommended)
- **PostgreSQL** (v13+ recommended)
- **Redis**
- **Nginx**
- **Docker & Docker Compose** (optional, for containerized setup)

---

## 2. Clone the Repository
```bash
git clone <your-repo-url>
cd PaksaFinancialSystem
```

---

## 3. Backend Setup

### a. Create and Activate Python Virtual Environment
```bash
cd backend
# On Windows:
python -m venv venv
.\venv\Scripts\activate
# On Linux/macOS:
# python3 -m venv venv
# source venv/bin/activate
```

### b. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### c. Configure Environment Variables
- Copy `.env.example` to `.env` and update values as needed.

### d. Run Database Migrations
```bash
alembic upgrade head
```

### e. Start Backend Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 4. Database & Redis Setup

- **PostgreSQL**: Ensure a local instance is running and matches your `.env` config.
- **Redis**: Ensure a local instance is running (default port 6379).

---

## 5. Frontend Setup

### a. Install Node.js Dependencies
```bash
cd ../frontend
npm install
```

### b. Build Frontend
```bash
npm run build
```
- Output will be in the `dist/` directory.

### c. (Optional) Run Frontend Dev Server
```bash
npm run dev
```
- Access at [http://localhost:5173](http://localhost:5173)

---

## 6. Nginx Setup (for Production-like Testing)

### a. Update Nginx Config
- Use the provided `frontend/nginx.conf`.
- Set the `root` directive to the absolute path of your `dist/` directory, e.g.:
  ```
  root /path/to/PaksaFinancialSystem/frontend/dist;
  ```
- Update the `proxy_pass` in the `/api/` location to point to your backend, e.g.:
  ```
  proxy_pass http://localhost:8000;
  ```

### b. Start or Reload Nginx
```bash
sudo nginx -c /path/to/PaksaFinancialSystem/frontend/nginx.conf
# Or reload if already running
sudo nginx -s reload
```

### c. Access the App
- Open [http://localhost](http://localhost) in your browser.

---

## 7. Troubleshooting
- **403/404 Errors**: Ensure `dist/` exists and Nginx has permission to read it.
- **API Errors**: Confirm backend is running and `proxy_pass` is correct.
- **Database Errors**: Check PostgreSQL and Redis are running and accessible.

---

## 8. Docker Compose (Alternative: All-in-One)
- You can use `docker-compose.nginx.yml` for a full stack local deployment:
```bash
docker compose -f docker-compose.nginx.yml up --build
```
- This will start all services (frontend, backend, db, redis, nginx) in containers.

---

## 9. Useful Commands
- **Stop all containers:**
  ```bash
  docker compose -f docker-compose.nginx.yml down
  ```
- **View logs:**
  ```bash
  docker compose -f docker-compose.nginx.yml logs -f
  ```

---

## 10. Support
If you encounter issues, check logs for each service and review the configuration files. For further help, contact the project maintainers.
