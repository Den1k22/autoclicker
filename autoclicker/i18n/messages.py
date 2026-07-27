"""Catalog-only markers for deferred and dynamically selected UI messages."""

from gettext import gettext, ngettext


if False:  # Babel extracts these calls; application code translates them later.
    gettext("About Autoclicker")
    gettext("Local automation for recorded screen points and exact-color CV actions.")
    gettext("Version")
    gettext("Close")
    gettext("Global hotkeys could not be registered: {error}")
    gettext("The default points file could not be loaded: {error}")
    ngettext("{count} point", "{count} points", 1)

    gettext("Language must be English or Russian.")
    gettext("Delay before a click cannot be negative.")
    gettext("Delay after a click cannot be negative.")
    gettext("Mesh width must be greater than 1.")
    gettext("Mesh height must be greater than 1.")
    gettext("CV region width must be greater than 0.")
    gettext("CV region height must be greater than 0.")
    gettext("RGB values must be between 0 and 255.")
    gettext("CV timing values cannot be negative.")
    gettext("Hotkeys cannot be empty.")
    gettext("Unsupported hotkey.")
    gettext("Hotkey duplicates another action.")
    gettext("CV actions cannot be empty.")
    gettext("Unsupported CV action.")
