from dataclasses import asdict, dataclass
from typing import Optional

VALID_STATUSES = ("TGE", "CLAIMED", "ONLINE")
VALID_LIST_TYPES = ("MAIN", "SECONDARY")


@dataclass
class Project:
    id: Optional[int]
    name: str
    web_link: str
    x_handle: str
    status: str
    note: str
    list_type: str
    event_date: str
    created_at: str
    updated_at: str

    @staticmethod
    def from_row(row) -> "Project":
        return Project(
            id=row["id"],
            name=row["name"],
            web_link=row["web_link"] or "",
            x_handle=row["x_handle"] or "",
            status=row["status"],
            note=row["note"] or "",
            list_type=row["list_type"],
            event_date=row["event_date"] or "",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return asdict(self)
