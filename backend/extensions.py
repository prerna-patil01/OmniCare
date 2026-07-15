"""
Shared extension instances.

Lives in its own module so models and app can both import it without a
circular dependency — the single most common Flask bootstrapping mistake.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
