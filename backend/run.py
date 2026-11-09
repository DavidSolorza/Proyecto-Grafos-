"""Backend entry point."""
from src.app import create_app
from src.core.config.settings import settings

app = create_app()

if __name__ == "__main__":
    print(f"🚀 Starting Flask API on http://{settings.HOST}:{settings.PORT}")
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG,
    )

