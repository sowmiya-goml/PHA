#!/usr/bin/env python3
"""Application startup script."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import uvicorn
from pha.core.config import settings

def main():
    """Start the FastAPI application."""
    uvicorn.run(
        "pha.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()