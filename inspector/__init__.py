# Inspector package
from inspector.collector import collect_all
from inspector.reporter import generate_html, save_html_report

__all__ = ["collect_all", "generate_html", "save_html_report"]
