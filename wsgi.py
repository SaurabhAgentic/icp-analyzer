from src.core.app import app

# Gunicorn configuration
timeout = 120  # Increase timeout to 120 seconds
workers = 2    # Reduce number of workers to conserve memory
worker_class = 'gthread'  # Use threads for better memory usage
threads = 4    # Number of threads per worker
max_requests = 1000  # Restart workers after handling this many requests
max_requests_jitter = 50  # Add randomness to the restart interval

if __name__ == "__main__":
    app.run() 