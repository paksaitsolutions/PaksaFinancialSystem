# Paksa Financial System - Developer Documentation

## Table of Contents
1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Architecture Overview](#architecture-overview)
4. [API Development](#api-development)
5. [Frontend Development](#frontend-development)
6. [Database Schema](#database-schema)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Code Style & Best Practices](#code-style--best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)

## Development Environment Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker (optional)

### Backend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/paksaitsolutions/paksa-financial-system.git
   cd paksa-financial-system/backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\\venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run serve
   ```

## Project Structure

### Backend Structure
```
backend/
├── alembic/                 # Database migrations
├── app/
│   ├── api/                 # API endpoints
│   ├── core/                # Core functionality
│   ├── db/                  # Database models and session
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   ├── tests/               # Backend tests
│   ├── utils/               # Utility functions
│   ├── config.py            # Application configuration
│   ├── main.py              # FastAPI application
│   └── __init__.py
├── tests/                   # Integration tests
├── alembic.ini              # Alembic configuration
├── requirements.txt          # Production dependencies
└── requirements-dev.txt      # Development dependencies
```

### Frontend Structure
```
frontend/
├── public/                  # Static files
├── src/
│   ├── assets/              # Static assets
│   ├── components/          # Reusable components
│   ├── composables/         # Vue 3 composables
│   ├── layouts/             # Layout components
│   ├── router/              # Vue Router configuration
│   ├── services/            # API services
│   ├── stores/              # Pinia stores
│   ├── types/               # TypeScript types
│   ├── utils/               # Utility functions
│   ├── views/               # Page components
│   ├── App.vue              # Root component
│   └── main.ts              # Application entry point
├── tests/                   # Frontend tests
├── .env.development         # Development environment variables
├── .env.production          # Production environment variables
├── package.json             # Project dependencies
└── vite.config.ts           # Vite configuration
```

## Architecture Overview

### Backend Architecture
- **API Layer**: FastAPI for RESTful endpoints
- **Service Layer**: Business logic and data processing
- **Data Access Layer**: SQLAlchemy for database operations
- **Authentication**: JWT-based authentication
- **Background Tasks**: Celery for asynchronous processing
- **Caching**: Redis for caching frequent queries

### Frontend Architecture
- **UI Framework**: Vue 3 with Composition API
- **State Management**: Pinia
- **Styling**: Tailwind CSS with custom components
- **Form Handling**: VeeValidate with Yup
- **HTTP Client**: Axios with request/response interceptors

## API Development

### Creating a New Endpoint
1. Create a new router file in `app/api/v1/`
2. Define your route handlers
3. Add the router to `app/api/v1/__init__.py`
4. Create corresponding Pydantic models in `app/schemas/`
5. Write service functions in `app/services/`
6. Add API documentation using OpenAPI

### Example Endpoint
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas.item import Item, ItemCreate, ItemUpdate
from ..services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=List[Item])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    service: ItemService = Depends()
):
    return await service.list_items(skip=skip, limit=limit)
```

## Frontend Development

### Creating a New Page
1. Create a new Vue component in `src/views/`
2. Add the route in `src/router/index.ts`
3. Create necessary components in `src/components/`
4. Add API services in `src/services/`
5. Create Pinia stores if needed in `src/stores/`

### Example Vue Component
```vue
<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Items</h1>
    <div v-if="loading">Loading...</div>
    <div v-else>
      <div v-for="item in items" :key="item.id" class="mb-2 p-2 border rounded">
        {{ item.name }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useItemStore } from '@/stores/item';

const itemStore = useItemStore();
const items = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    items.value = await itemStore.fetchItems();
  } catch (error) {
    console.error('Failed to fetch items:', error);
  } finally {
    loading.value = false;
  }
});
</script>
```

## Database Schema

### Migrations
1. Create a new migration:
   ```bash
   alembic revision --autogenerate -m "description of changes"
   ```

2. Apply migrations:
   ```bash
   alembic upgrade head
   ```

### Models
Example SQLAlchemy model:
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..db.base_class import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## Testing

### Backend Tests
```bash
pytest
```

### Frontend Tests
```bash
npm test
```

### E2E Tests
```bash
npm run test:e2e
```

## Deployment

### Production Build
1. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Build and run the backend with Docker:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

### Environment Variables
Required production environment variables:
```
DATABASE_URL=postgresql://user:password@db:5432/paksa
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
ENVIRONMENT=production
```

## Code Style & Best Practices

### Python
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all public functions
- Keep functions small and focused
- Use dependency injection
- Write tests for new features

### JavaScript/TypeScript
- Use TypeScript for type safety
- Follow Vue 3 Composition API patterns
- Use Pinia for state management
- Write reusable components
- Add JSDoc comments for complex functions

## Troubleshooting

### Common Issues
- **Database connection issues**: Check PostgreSQL logs and connection string
- **CORS errors**: Verify CORS settings in FastAPI config
- **Vue dev server not starting**: Check for port conflicts and Node.js version
- **API 500 errors**: Check backend logs for detailed error messages

### Debugging
- Backend: Use `uvicorn --reload --log-level debug`
- Frontend: Use Vue DevTools and browser developer tools
- Database: Use `pgAdmin` or `TablePlus` to inspect the database

## Contributing

### Workflow
1. Create a new branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Write tests
4. Run linter and tests
5. Commit your changes: `git commit -m "Add your feature"`
6. Push to the branch: `git push origin feature/your-feature`
7. Create a pull request

### Code Review
- All code must be reviewed by at least one other developer
- Ensure all tests pass
- Update documentation as needed
- Follow the project's coding standards

### Reporting Issues
When reporting issues, please include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Environment details
5. Any relevant logs or screenshots
