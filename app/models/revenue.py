from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Revenue:
    id: Optional[int]
    project_id: Optional[int]
    project_name: str
    amount: float
    date: str
    created_at: str
    updated_at: str

    @staticmethod
    def from_row(row) -> "Revenue":
        return Revenue(
            id=row["id"],
            project_id=row["project_id"],
            project_name=row["project_name"],
            amount=row["amount"] or 0,
            date=row["date"] or "",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return asdict(self)
