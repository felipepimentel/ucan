import logging
import sys

from .ui import ChatApp

logger = logging.getLogger("UCAN")


def main():
    """Main entry point"""
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Create and configure main app
        app = ChatApp()

        # Force update to get correct dimensions
        app.update_idletasks()

        # Center window
        width = app.winfo_width()
        height = app.winfo_height()
        x = (app.winfo_screenwidth() - width) // 2
        y = (app.winfo_screenheight() - height) // 2
        app.geometry(f"{width}x{height}+{x}+{y}")

        # Ensure window is visible and focused
        app.deiconify()
        app.focus_force()
        app.lift()

        # Start main loop
        app.mainloop()

    except Exception as e:
        logger.error(f"Erro ao iniciar aplicação: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
