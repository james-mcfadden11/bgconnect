import asyncio
import uuid
from datetime import datetime, timezone

from models.annotation import Annotation, AnnotationCreate

from .database import get_connection


def _create(data: AnnotationCreate, user_id: str) -> Annotation:
    annotation_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    conn = get_connection()
    conn.execute(
        """INSERT INTO annotations
           (id, user_id, timestamp, category, value, notes, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            annotation_id,
            user_id,
            data.timestamp.isoformat(),
            data.category,
            data.value,
            data.notes,
            now.isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    return Annotation(
        id=annotation_id,
        user_id=user_id,
        timestamp=data.timestamp,
        category=data.category,
        value=data.value,
        notes=data.notes,
        created_at=now,
    )


def _list(user_id: str, start: datetime, end: datetime) -> list[Annotation]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM annotations
           WHERE user_id = ? AND timestamp >= ? AND timestamp <= ?
           ORDER BY timestamp DESC""",
        (user_id, start.isoformat(), end.isoformat()),
    ).fetchall()
    conn.close()
    return [
        Annotation(
            id=row["id"],
            user_id=row["user_id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            category=row["category"],
            value=row["value"],
            notes=row["notes"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        for row in rows
    ]


async def create_annotation(data: AnnotationCreate, user_id: str) -> Annotation:
    return await asyncio.to_thread(_create, data, user_id)


async def list_annotations(
    user_id: str, start: datetime, end: datetime
) -> list[Annotation]:
    return await asyncio.to_thread(_list, user_id, start, end)
