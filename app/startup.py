"""Application Startup - Preload resources"""
from app.services.kb_singleton import preload_kb

def initialize_app():
    """Initialize application resources at startup"""
    print("🚀 Initializing application...")
    preload_kb()
    print("✅ Application ready\n")

if __name__ == "__main__":
    initialize_app()
