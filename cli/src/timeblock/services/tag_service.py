"""Service para gerenciar tags."""

from sqlmodel import Session, select

from src.timeblock.database import get_engine_context
from src.timeblock.models import Tag


class TagService:
    """Gerencia operações de tags."""

    @staticmethod
    def create_tag(name: str | None = None, color: str = "#fbd75b") -> Tag:
        """Cria tag. Nome opcional, cor padrão amarelo."""
        tag = Tag(name=name, color=color)

        with get_engine_context() as engine:
            with Session(engine) as session:
                session.add(tag)
                session.commit()
                session.refresh(tag)
                return tag

    @staticmethod
    def get_tag(tag_id: int) -> Tag:
        """Busca tag por ID."""
        with get_engine_context() as engine:
            with Session(engine) as session:
                tag = session.get(Tag, tag_id)
                if not tag:
                    raise ValueError(f"Tag {tag_id} não encontrada")
                return tag

    @staticmethod
    def list_tags() -> list[Tag]:
        """Lista todas as tags."""
        with get_engine_context() as engine:
            with Session(engine) as session:
                statement = select(Tag).order_by(Tag.name)
                return list(session.exec(statement).all())

    @staticmethod
    def update_tag(tag_id: int, **kwargs) -> Tag:
        """Atualiza tag."""
        with get_engine_context() as engine:
            with Session(engine) as session:
                tag = session.get(Tag, tag_id)
                if not tag:
                    raise ValueError(f"Tag {tag_id} não encontrada")

                for key, value in kwargs.items():
                    setattr(tag, key, value)

                session.add(tag)
                session.commit()
                session.refresh(tag)
                return tag

    @staticmethod
    def delete_tag(tag_id: int) -> None:
        """Deleta tag."""
        with get_engine_context() as engine:
            with Session(engine) as session:
                tag = session.get(Tag, tag_id)
                if not tag:
                    raise ValueError(f"Tag {tag_id} não encontrada")

                session.delete(tag)
                session.commit()
