from __future__ import annotations


APP_STYLESHEET = """
QMainWindow, QDialog { background: #20252b; color: #e7e5df; }
QWidget { color: #e7e5df; font-size: 13px; }
QTabWidget::pane { border: 1px solid #3c434b; background: #252b32; }
QTabBar::tab { background: #303740; padding: 10px 18px; }
QTabBar::tab:selected { background: #48515b; }
QComboBox, QSpinBox, QLineEdit { background: #303740; border: 1px solid #59636e; padding: 6px; }
QPushButton { background: #3b4651; border: 1px solid #65717d; border-radius: 4px; padding: 6px 10px; }
QPushButton:hover { background: #4a5865; }
QTreeWidget { background: #252b32; border: none; alternate-background-color: #2b323a; }
QHeaderView::section { background: #303740; padding: 7px; border: none; }
QScrollArea { border: none; background: transparent; }
QLabel#heading { font-size: 20px; font-weight: 600; color: #f0d49a; }
QLabel#section { font-size: 15px; font-weight: 600; color: #d5d9de; }
QLabel#muted { color: #a7afb7; }
QLabel#warning { color: #ffc66d; font-weight: 600; }
QFrame#card { background: #2d343c; border: 1px solid #48515b; border-radius: 6px; }
QFrame#preparationCard { background: #30363d; border: 1px solid #777f89; border-radius: 6px; }
QFrame#sidebar { background: #242a30; border: 1px solid #48515b; border-radius: 6px; }
"""


def domain_badge(domain_id: str, theme: dict[str, dict]) -> str:
    item = theme.get(domain_id, {})
    return f"{item.get('icon', '•')} {item.get('label', domain_id.replace('_', ' ').title())}"


def domain_color(domain_id: str, theme: dict[str, dict]) -> str:
    return str(theme.get(domain_id, {}).get("color", "#777f89"))


def domain_badges_html(domain_ids: tuple[str, ...], theme: dict[str, dict]) -> str:
    return " &nbsp; ".join(
        f'<span style="color:{domain_color(domain_id, theme)}; font-weight:600">'
        f'{domain_badge(domain_id, theme)}</span>'
        for domain_id in domain_ids
    )


def tinted_card_style(domain_id: str, theme: dict[str, dict]) -> str:
    color = domain_color(domain_id, theme)
    red, green, blue = _rgb(color)
    return (
        "QFrame#card {"
        f"background-color: rgba({red}, {green}, {blue}, 58);"
        f"border: 1px solid {color}; border-radius: 6px;"
        "}"
    )


def objective_row_style(domain_id: str, theme: dict[str, dict]) -> str:
    color = domain_color(domain_id, theme)
    red, green, blue = _rgb(color)
    return (
        "QFrame#objectiveRow {"
        f"background-color: rgba({red}, {green}, {blue}, 42);"
        f"border-left: 5px solid {color}; border-radius: 3px;"
        "}"
    )


def _rgb(color: str) -> tuple[int, int, int]:
    value = color.lstrip("#")
    if len(value) != 6:
        return (119, 127, 137)
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))
