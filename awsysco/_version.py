"""Single source of truth for the installed package version.

Kept separate from ``__init__.py`` so internal modules (e.g. the transports, for the
User-Agent header) can import it without triggering a circular import through the
package's public re-exports.
"""

__version__ = "1.4.0"
