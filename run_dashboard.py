#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick Start Script for DeltaMusic Dashboard
Run this to test the dashboard locally
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required = ["fastapi", "uvicorn", "pydantic"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"  ❌ {package} - NOT INSTALLED")
    
    if missing:
        print("\n⚠️  Missing dependencies detected!")
        print(f"   Run: pip install {' '.join(missing)}")
        print(f"   Or: pip install -r dashboard/requirements.txt\n")
        return False
    
    print("✅ All dependencies installed!\n")
    return True


def check_files():
    """Check if required files exist"""
    print("📁 Checking required files...")
    
    required_files = [
        "dashboard/server.py",
        "dashboard/index.html",
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - NOT FOUND")
            all_exist = False
    
    if not all_exist:
        print("\n❌ Some required files are missing!")
        return False
    
    print("✅ All required files found!\n")
    return True


def start_dashboard():
    """Start the dashboard server"""
    print("🚀 Starting Dashboard Server...\n")
    print("=" * 60)
    print("📊 DeltaMusic Statistics Dashboard")
    print("=" * 60)
    print(f"🌐 URL:     http://localhost:8000")
    print(f"📖 API:     http://localhost:8000/docs")
    print(f"🔄 Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    # Import and run
    try:
        import uvicorn
        from dashboard.server import dashboard_app
        
        uvicorn.run(
            dashboard_app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        print("\nℹ️  Make sure:")
        print("  1. Bot is running (or MongoDB is accessible)")
        print("  2. No other service is using port 8000")
        print("  3. All dependencies are installed")


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("🎵 DeltaMusic Dashboard - Quick Start")
    print("=" * 60 + "\n")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check files
    if not check_files():
        sys.exit(1)
    
    # Start dashboard
    try:
        start_dashboard()
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
