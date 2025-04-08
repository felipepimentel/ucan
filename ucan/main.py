import argparse
import logging
import sys
from pathlib import Path

# Import version from the package
import ucan

from .ui import ChatApp

# Flag to track if logging has been configured
_logging_configured = False


def setup_logging():
    """Configure logging for the application"""
    global _logging_configured

    # Only configure logging once
    if _logging_configured:
        return logging.getLogger("UCAN")

    logger = logging.getLogger("UCAN")

    # Clear any existing handlers to be safe
    if logger.handlers:
        logger.handlers = []

    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent propagation to root logger

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler("ucan.log")
    file_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Mark logging as configured
    _logging_configured = True

    return logger


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="UCAN - Universal Conversation Assistant Navigator"
    )
    parser.add_argument(
        "--version", action="version", version=f"UCAN {ucan.__version__}"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--theme", choices=["light", "dark"], help="Set application theme"
    )
    parser.add_argument(
        "--high-contrast", action="store_true", help="Enable high contrast mode"
    )
    parser.add_argument("--workspace", type=str, help="Path to workspace directory")
    return parser.parse_args()


def main():
    """Main entry point for the application"""
    # Parse command line arguments
    args = parse_args()

    # Setup logging
    logger = setup_logging()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    # Log startup information
    logger.info(f"Starting UCAN {ucan.__version__}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")

    # Create config directory if it doesn't exist
    config_dir = Path.home() / ".ucan"
    config_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Config directory: {config_dir}")

    # Initialize and run the application
    app = ChatApp()

    # Set theme if specified in arguments
    if args.theme:
        app.theme_manager.set_theme(args.theme, args.high_contrast)

    # Set workspace if specified
    if args.workspace:
        workspace_path = Path(args.workspace)
        if workspace_path.exists() and workspace_path.is_dir():
            logger.info(f"Setting workspace to {workspace_path}")
            app.set_workspace(workspace_path)
        else:
            logger.warning(f"Workspace directory does not exist: {workspace_path}")

    # After app window appears, we will setup keyboard shortcuts
    # This ensures all UI elements are created first
    app.after(1000, app.setup_keyboard_shortcuts)

    # Start the app (window will be shown via _show_maximized)
    app.mainloop()


if __name__ == "__main__":
    main()
