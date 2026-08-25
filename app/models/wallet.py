from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Wallet:
    id: Optional[int]
    name: str
    address: str
    note: str
    created_at: str
    updated_at: str

    @staticmethod
    def from_row(row) -> "Wallet":
        return Wallet(
            id=row["id"],
            name=row["name"],
            address=row["address"],
            note=row["note"] or "",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return asdict(self)
