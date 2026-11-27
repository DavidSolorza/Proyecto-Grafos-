"""Pager for lists that do not fit their panel: mouse wheel or the < > buttons."""
from tardo_ui import theme as t

WIDTH = 86


def paged(ui, store, key: str, items: list, per_page: int, area, top_right) -> list:
    """Return the items of the current page and draw the pager when there is more than one."""
    per_page = max(1, per_page)
    pages = max(1, -(-len(items) // per_page))
    page = store.pages.get(key, 0) - ui.scroll(area)
    if pages > 1:
        x, y = top_right[0] - WIDTH, top_right[1]
        if ui.button((x, y, 24, 20), "<", key=f"{key}:prev", tone="ghost", kind="small"):
            page -= 1
        if ui.button((x + WIDTH - 24, y, 24, 20), ">", key=f"{key}:next", tone="ghost", kind="small"):
            page += 1
    page = max(0, min(page, pages - 1))
    store.pages[key] = page
    if pages > 1:
        ui.text(f"{page + 1}/{pages}", (top_right[0] - WIDTH // 2, top_right[1] + 10), "small", t.INK, "center")
    return items[page * per_page:(page + 1) * per_page]
