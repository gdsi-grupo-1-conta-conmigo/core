# FastAPI Application with Supabase Authentication

A FastAPI application with user authentication using Supabase, structured following [FastAPI's bigger applications guide](https://fastapi.tiangolo.com/tutorial/bigger-applications/).

## Project Structure

```
app/
├── __init__.py              # Makes app a Python package
├── main.py                  # Main FastAPI application
├── dependencies.py          # Shared dependencies (Supabase client)
└── routers/
    ├── __init__.py          # Makes routers a Python package
    └── authentication.py    # Authentication routes (/auth/signup, /auth/login)
```

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export SUPABASE_URL="your_supabase_project_url"
   export SUPABASE_KEY="your_supabase_anon_key"
   ```

3. **Run the application**:
   ```bash
   fastapi dev app/main.py
   ```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /auth/signup` - User registration
- `POST /auth/login` - User authentication

## Documentation

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## Authentication

The application uses Supabase for authentication. Make sure to:
1. Create a Supabase project
2. Get your project URL and anon key
3. Set them as environment variables
