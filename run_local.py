#!/usr/bin/env python3
"""
Local Development Runner for Instagram Story Monitor
Run this script to start the app locally with proper setup
"""

import os
import sys
from dotenv import load_dotenv

def setup_environment():
    """Setup environment variables for local development"""
    
    # Load .env file if it exists
    load_dotenv()
    
    # Set default values if not provided
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
        print("⚠️  Using default SECRET_KEY for development")
    
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///instagram_monitor.db'
        print("📁 Using SQLite database for local development")
    
    print(f"🔐 SECRET_KEY: {os.environ['SECRET_KEY'][:20]}...")
    print(f"🗄️  DATABASE_URL: {os.environ['DATABASE_URL']}")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import selenium
        import sqlalchemy
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("🔧 Run: pip install -r requirements.txt")
        return False

def main():
    """Main function to start local development server"""
    
    print("🚀 Instagram Story Monitor - Local Development")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Import and run the app
    try:
        from app import app, create_tables
        
        print("\n📊 Creating database tables...")
        create_tables()
        
        print("\n🌐 Starting Flask development server...")
        print("🔗 Open your browser to: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 