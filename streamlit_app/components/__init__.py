"""Compatibility namespace for moved UI components.

Prefer importing from streamlit_app.ui.components in new code.
"""

from .cards import render_kpi_card, render_status_card
from .charts import style_figure
from .layout import apply_theme, render_page_header
from .sidebar import render_sidebar
from .tables import render_dataframe

__all__ = [
	"apply_theme",
	"render_dataframe",
	"render_kpi_card",
	"render_page_header",
	"render_sidebar",
	"render_status_card",
	"style_figure",
]
