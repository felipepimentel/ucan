import json
import logging
import os

import customtkinter as ctk

logger = logging.getLogger("UCAN")

# Definir algumas cores e estilos consistentes para a aplicação
COLORS = {
    "light": {
        "primary": "#2563EB",  # More accessible blue
        "primary_dark": "#1D4ED8",  # Darker blue for hover
        "primary_light": "#60A5FA",  # Light blue for highlights
        "surface": "#FFFFFF",  # White
        "surface_light": "#F5F7FA",  # Light gray with blue tint
        "surface_hover": "#EFF3F8",  # Hover state for surface
        "text": "#111827",  # Very dark gray for better contrast
        "text_light": "#FFFFFF",  # White for dark backgrounds
        "text_secondary": "#4B5563",  # Darker medium gray for better readability
        "border": "#D1D5DB",  # Medium gray
        "border_focus": "#2563EB",  # Blue for focus states
        "error": "#DC2626",  # More accessible red
        "warning": "#D97706",  # More accessible orange
        "success": "#059669",  # More accessible green
        "background": "#F9FAFB",  # Light background
        "disabled": "#E5E7EB",  # Disabled state
        "accent1": "#8B5CF6",  # Purple
        "accent2": "#EC4899",  # Pink
    },
    "dark": {
        "primary": "#3B82F6",  # Brighter blue for dark mode
        "primary_dark": "#2563EB",  # Slightly darker blue for hover
        "primary_light": "#60A5FA",  # Light blue for highlights
        "surface": "#1F2937",  # Dark gray
        "surface_light": "#374151",  # Lighter gray
        "surface_hover": "#4B5563",  # Hover state for surface
        "text": "#F9FAFB",  # Very light gray for better contrast
        "text_light": "#FFFFFF",  # White for dark backgrounds
        "text_secondary": "#D1D5DB",  # Light gray with better contrast
        "border": "#4B5563",  # Medium gray
        "border_focus": "#3B82F6",  # Blue for focus states
        "error": "#EF4444",  # Brighter red for dark mode
        "warning": "#F59E0B",  # Brighter orange for dark mode
        "success": "#10B981",  # Brighter green for dark mode
        "background": "#111827",  # Dark background
        "disabled": "#374151",  # Disabled state
        "accent1": "#A78BFA",  # Lighter purple for dark mode
        "accent2": "#F472B6",  # Lighter pink for dark mode
    },
}

# Accessibility colors (high contrast)
ACCESSIBILITY_COLORS = {
    "high_contrast_light": {
        "primary": "#0039A6",  # Darker blue with higher contrast
        "primary_dark": "#002D77",  # Even darker blue
        "primary_light": "#0052E0",  # Slightly lighter blue
        "surface": "#FFFFFF",  # White
        "surface_light": "#F0F0F0",  # Light gray
        "surface_hover": "#E0E0E0",  # Slightly darker for hover
        "text": "#000000",  # Black text for maximum contrast
        "text_light": "#FFFFFF",  # White text
        "text_secondary": "#333333",  # Very dark gray
        "border": "#666666",  # Medium gray border
        "border_focus": "#0039A6",  # Same as primary
        "error": "#C41E3A",  # Darker red
        "warning": "#B35A00",  # Darker orange
        "success": "#006400",  # Dark green
        "background": "#F8F8F8",  # Very light gray
        "disabled": "#CCCCCC",  # Light gray
        "accent1": "#6A0DAD",  # Dark purple
        "accent2": "#AD0D6A",  # Dark pink
    },
    "high_contrast_dark": {
        "primary": "#52A9FF",  # Brighter blue
        "primary_dark": "#3B94E8",  # Slightly darker blue
        "primary_light": "#73BCFF",  # Lighter blue
        "surface": "#121212",  # Very dark gray
        "surface_light": "#1F1F1F",  # Slightly lighter dark
        "surface_hover": "#2F2F2F",  # Hover state
        "text": "#FFFFFF",  # White text
        "text_light": "#FFFFFF",  # White text
        "text_secondary": "#E0E0E0",  # Very light gray
        "border": "#AAAAAA",  # Light gray border
        "border_focus": "#52A9FF",  # Same as primary
        "error": "#FF5252",  # Bright red
        "warning": "#FFAB40",  # Bright orange
        "success": "#60E550",  # Bright green
        "background": "#000000",  # Black
        "disabled": "#444444",  # Dark gray
        "accent1": "#B57EFF",  # Bright purple
        "accent2": "#FF7EC2",  # Bright pink
    },
}

# Constantes de estilo
TEXT_STYLES = {
    "h1": {"size": 32, "weight": "bold", "family": "Segoe UI"},
    "h2": {"size": 24, "weight": "bold", "family": "Segoe UI"},
    "subtitle": {"size": 18, "weight": "bold", "family": "Segoe UI"},
    "body": {"size": 16, "weight": "normal", "family": "Segoe UI"},
    "small": {"size": 14, "weight": "normal", "family": "Segoe UI"},
    "caption": {"size": 12, "weight": "normal", "family": "Segoe UI"},
}

LAYOUT = {
    "padding": {
        "xxs": 2,
        "xs": 4,
        "sm": 8,
        "md": 12,
        "lg": 16,
        "xl": 24,
        "xxl": 32,
    },
    "border_radius": {
        "xs": 4,
        "sm": 8,
        "md": 12,
        "lg": 16,
        "xl": 24,
        "circle": 9999,
    },
    "button": {
        "width": 36,
        "height": 36,
        "corner_radius": 8,
        "border_width": 1,
    },
    "input": {
        "height": 40,
        "corner_radius": 8,
        "border_width": 1,
    },
    "message": {
        "max_width": 600,
        "corner_radius": 8,
        "border_width": 1,
    },
    "card": {
        "corner_radius": 12,
        "border_width": 1,
        "padding": 16,
    },
    "avatar": {
        "sizes": {
            "sm": 32,
            "md": 40,
            "lg": 48,
        }
    },
}

BUTTON_STYLES = {
    "primary": {
        "font": ("Segoe UI", 16),
        "corner_radius": LAYOUT["border_radius"]["sm"],
        "fg_color": "#3B82F6",  # primary blue
        "text_color": "#FFFFFF",  # white
        "hover_color": "#2563EB",  # darker blue
    },
    "secondary": {
        "font": ("Segoe UI", 16),
        "corner_radius": LAYOUT["border_radius"]["sm"],
        "fg_color": "#F3F4F6",  # light gray
        "text_color": "#111827",  # dark gray
        "hover_color": "#E5E7EB",  # slightly darker gray
        "border_width": 1,
        "border_color": "#D1D5DB",  # medium gray
    },
    "danger": {
        "font": ("Segoe UI", 16),
        "corner_radius": LAYOUT["border_radius"]["sm"],
        "fg_color": "#EF4444",  # red
        "text_color": "#FFFFFF",  # white
        "hover_color": "#DC2626",  # darker red
    },
    "icon": {
        "font": ("Segoe UI", 20),
        "corner_radius": LAYOUT["border_radius"]["circle"],
        "fg_color": "transparent",  # transparent
        "text_color": "#6B7280",  # medium gray
        "hover_color": "#F3F4F6",  # light gray
        "width": 40,
        "height": 40,
    },
    "link": {
        "font": ("Segoe UI", 16),
        "corner_radius": 0,
        "fg_color": "transparent",  # transparent
        "text_color": "#3B82F6",  # primary blue
        "hover_color": "transparent",  # transparent
        "hover_text_color": "#2563EB",  # darker blue
    },
}


class ThemeManager:
    """Manages the application theme and colors"""

    def __init__(self):
        self.theme = "dark"
        self.high_contrast = False

        # Load theme from config file if it exists
        self.load_theme()

        # Set up colors based on theme and contrast mode
        self.colors = self._get_theme_colors()

        # Layout constants
        self.spacing = LAYOUT["padding"]
        self.border_radius = LAYOUT["border_radius"]

        self.animation = {
            "duration": {
                "fast": 100,
                "normal": 200,
                "slow": 300,
            },
            "easing": {
                "in": "cubic-bezier(0.4, 0, 1, 1)",
                "out": "cubic-bezier(0, 0, 0.2, 1)",
                "inOut": "cubic-bezier(0.4, 0, 0.2, 1)",
            },
        }

        # Apply the theme to the application
        self.apply_theme()

    def get_colors(self):
        """Get current theme colors based on theme and contrast settings"""
        return self._get_theme_colors()

    def _get_theme_colors(self):
        """Get theme colors based on theme and contrast mode"""
        if self.high_contrast:
            return ACCESSIBILITY_COLORS[f"high_contrast_{self.theme}"]
        else:
            return COLORS[self.theme]

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme = "light" if self.theme == "dark" else "dark"
        self.colors = self._get_theme_colors()
        self.save_theme()
        return self.colors

    def toggle_contrast(self):
        """Toggle between normal and high contrast mode"""
        self.high_contrast = not self.high_contrast
        self.colors = self._get_theme_colors()
        self.save_theme()
        return self.colors

    def get_spacing(self, size):
        """Get spacing value"""
        return self.spacing.get(size, self.spacing["md"])

    def get_border_radius(self, size):
        """Get border radius value"""
        return self.border_radius.get(size, self.border_radius["md"])

    def get_animation(self, duration="normal", easing="inOut"):
        """Get animation settings"""
        duration_value = self.animation["duration"].get(
            duration, self.animation["duration"]["normal"]
        )
        easing_value = self.animation["easing"].get(
            easing, self.animation["easing"]["inOut"]
        )
        return {"duration": duration_value, "easing": easing_value}

    def apply_theme(self):
        """Apply theme to CustomTkinter"""
        appearance_mode = "Dark" if self.theme == "dark" else "Light"
        ctk.set_appearance_mode(appearance_mode)

        # Use built-in CustomTkinter themes instead of our custom themes
        # CustomTkinter only accepts "blue", "dark-blue", or "green" as built-in themes
        if self.theme == "dark":
            builtin_theme = "dark-blue"
        else:
            builtin_theme = "blue"

        # Set default color theme using a built-in theme
        ctk.set_default_color_theme(builtin_theme)

    def load_theme(self):
        """Load theme settings from config file"""
        try:
            config_path = os.path.expanduser("~/.ucan/config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                    self.theme = config.get("theme", "dark")
                    self.high_contrast = config.get("high_contrast", False)
                    logger.info(
                        f"Loaded theme: {self.theme}, high contrast: {self.high_contrast}"
                    )
        except Exception as e:
            logger.error(f"Error loading theme: {e}")
            # Default to dark theme if there's an error
            self.theme = "dark"
            self.high_contrast = False

    def save_theme(self):
        """Save theme settings to config file"""
        try:
            config_path = os.path.expanduser("~/.ucan/config.json")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            # Load existing config if it exists
            config = {}
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)

            # Update theme settings
            config["theme"] = self.theme
            config["high_contrast"] = self.high_contrast

            # Save updated config
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(
                f"Saved theme: {self.theme}, high contrast: {self.high_contrast}"
            )
        except Exception as e:
            logger.error(f"Error saving theme: {e}")

    def get_theme(self):
        """Get current theme"""
        return {"theme": self.theme, "high_contrast": self.high_contrast}

    def set_theme(self, theme_name, high_contrast=None):
        """Set theme by name"""
        if theme_name in ["light", "dark"]:
            self.theme = theme_name

        if high_contrast is not None:
            self.high_contrast = bool(high_contrast)

        self.colors = self._get_theme_colors()
        self.save_theme()
        self.apply_theme()
        return self.colors

    def get_button_style(self, style_name="primary"):
        """Get button style by name"""
        return BUTTON_STYLES.get(style_name, BUTTON_STYLES["primary"])
