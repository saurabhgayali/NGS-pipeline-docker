"""
Initialization module for NGS Pipeline Web Wrapper
"""

import logging
import sys
from pathlib import Path

# Add the webapp directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/webapp.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

def initialize_app():
    """Initialize application on startup"""
    logger.info("Initializing NGS Pipeline Web Wrapper...")
    
    # Import and initialize settings
    try:
        from config.settings import (
            ensure_directories, 
            INPUT_QUEUE_DIR, 
            PROJECTS_DIR,
            BASE_DATA_DIR
        )
        
        logger.info("Loading configuration...")
        ensure_directories()
        
        logger.info(f"Base data directory: {BASE_DATA_DIR}")
        logger.info(f"Input queue directory: {INPUT_QUEUE_DIR}")
        logger.info(f"Projects directory: {PROJECTS_DIR}")
        
        logger.info("Application initialization complete ✓")
        return True
    
    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = initialize_app()
    sys.exit(0 if success else 1)
