"""
Check News prompt generation (APP_SPEC section 4.2).

IMPORTANT (scope): this module only builds a text prompt for the user to
copy and run elsewhere (e.g. paste into an AI assistant). It does NOT
perform any web scraping or call any News/X API -- that is explicitly out
of scope per APP_SPEC section 22.
"""

from app.services import project_service

EVENTS_OF_INTEREST = ["TGE", "Snapshot", "Mint", "Claim", "End", "Deadline"]

# Check scope: how far back to look, and whether pinned posts are included.
CHECK_SCOPE_DAYS = {"NEWS": 2, "DEEP": 10}


def _collect_projects(scope: str) -> list:
    scope = (scope or "").upper()
    projects = []
    if scope in ("MAIN", "BOTH"):
        projects += project_service.list_projects("MAIN")
    if scope in ("SECONDARY", "BOTH"):
        projects += project_service.list_projects("SECONDARY")
    return projects


def generate_prompt(scope: str, check_scope: str = "NEWS") -> dict:
    """scope: 'MAIN' | 'SECONDARY' | 'BOTH'
    check_scope: 'NEWS' (2 day) | 'DEEP' (10 day + pinned)
    -> {"prompt": str, "handles": [str]}"""
    projects = _collect_projects(scope)
    handles = sorted({p["x_handle"].strip() for p in projects if p.get("x_handle")})

    if not handles:
        return {"prompt": "", "handles": []}

    check_scope = (check_scope or "NEWS").upper()
    days = CHECK_SCOPE_DAYS.get(check_scope, CHECK_SCOPE_DAYS["NEWS"])
    pinned_clause = " và cả bài viết được ghim" if check_scope == "DEEP" else ""

    handle_list = "\n".join(f"@{h.lstrip('@')}" for h in handles)
    events = ", ".join(EVENTS_OF_INTEREST)

    prompt = (
        f"Kiểm tra các bài viết mới nhất của các tài khoản X sau trong {days} ngày gần đây"
        f"{pinned_clause}, sau đó thông báo kết quả:\n\n"
        f"{handle_list}\n\n"
        f"Chỉ tập trung vào các sự kiện quan trọng liên quan đến Airdrop: {events} "
        "hoặc các thông tin quan trọng khác ảnh hưởng trực tiếp đến dự án."
    )

    return {"prompt": prompt, "handles": handles}
