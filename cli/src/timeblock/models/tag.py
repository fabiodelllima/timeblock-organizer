"""Tag model para categorização visual."""

from sqlmodel import Field, SQLModel


class Tag(SQLModel, table=True):
    """Tag para categorização de hábitos e tarefas."""

    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(default=None, index=True)
    color: str = Field(default="#fbd75b")  # Amarelo padrão (Google Calendar ID 5)
    gcal_color_id: int = Field(default=5)  # Para sync futuro
