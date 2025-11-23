"""Testes para funções de construção de queries e fetch."""

from datetime import UTC, timedelta

from sqlmodel import Session

from src.timeblock.utils.queries import (
    build_events_query,
    fetch_events,
    fetch_events_in_range,
)


class TestBuildEventsQuery:
    """Testes para função build_events_query."""

    def test_query_default_descending(self, test_db, sample_events):
        """Deve ordenar por scheduled_start decrescente por padrão."""
        # test_db já é uma Session
        query = build_events_query(ascending=False)
        results = list(test_db.exec(query))
        assert len(results) == 5
        assert results[0].title == "Event 5"
        assert results[-1].title == "Event 1"

    def test_query_ascending(self, test_db, sample_events):
        """Deve ordenar por scheduled_start crescente quando solicitado."""
        # test_db já é uma Session
        query = build_events_query(ascending=True)
        results = list(test_db.exec(query))
        assert len(results) == 5
        assert results[0].title == "Event 1"
        assert results[-1].title == "Event 5"

    def test_query_with_start_date(self, test_db, sample_events, now_time):
        """Deve filtrar eventos a partir da data inicial."""
        # test_db já é uma Session
        query = build_events_query(start=now_time, ascending=True)
        results = list(test_db.exec(query))
        assert len(results) == 3
        assert results[0].title == "Event 3"
        assert results[1].title == "Event 4"
        assert results[2].title == "Event 5"

    def test_query_with_end_date(self, test_db, sample_events, now_time):
        """Deve filtrar eventos até a data final."""
        # test_db já é uma Session
        query = build_events_query(end=now_time, ascending=True)
        results = list(test_db.exec(query))
        assert len(results) == 3
        assert results[0].title == "Event 1"
        assert results[1].title == "Event 2"
        assert results[2].title == "Event 3"

    def test_query_with_date_range(self, test_db, sample_events, now_time):
        """Deve filtrar eventos dentro do intervalo de datas."""
        # test_db já é uma Session
        start = now_time - timedelta(days=1)
        end = now_time + timedelta(days=1)
        query = build_events_query(start=start, end=end, ascending=True)
        results = list(test_db.exec(query))
        assert len(results) == 3
        assert results[0].title == "Event 2"
        assert results[1].title == "Event 3"
        assert results[2].title == "Event 4"

    def test_query_no_results(self, test_db, sample_events, now_time):
        """Deve retornar lista vazia quando nenhum evento corresponde."""
        # test_db já é uma Session
        start = now_time - timedelta(days=365)
        end = now_time - timedelta(days=300)
        query = build_events_query(start=start, end=end)
        results = list(test_db.exec(query))
        assert len(results) == 0


class TestFetchEvents:
    """Testes para função fetch_events."""

    def test_fetch_all_events(self, test_db, sample_events):
        """Deve buscar todos os eventos quando sem filtros."""
        # test_db já é uma Session
        query = build_events_query()
        results = fetch_events(test_db, query)
        assert len(results) == 5

    def test_fetch_empty_database(self, test_db):
        """Deve retornar lista vazia quando banco está vazio."""
        # test_db já é uma Session
        query = build_events_query()
        results = fetch_events(test_db, query)
        assert len(results) == 0


class TestFetchEventsInRange:
    """Testes para função de conveniência fetch_events_in_range."""

    def test_fetch_with_start(self, test_db, sample_events, now_time):
        """Deve buscar eventos a partir da data inicial."""
        # test_db já é uma Session
        results = fetch_events_in_range(test_db, start=now_time)
        assert len(results) == 3
        assert all(e.scheduled_start.replace(tzinfo=UTC) >= now_time for e in results)

    def test_fetch_with_end(self, test_db, sample_events, now_time):
        """Deve buscar eventos até a data final."""
        # test_db já é uma Session
        results = fetch_events_in_range(test_db, end=now_time)
        assert len(results) == 3
        assert all(e.scheduled_start.replace(tzinfo=UTC) <= now_time for e in results)

    def test_fetch_with_range(self, test_db, sample_events, now_time):
        """Deve buscar eventos dentro do intervalo de datas."""
        # test_db já é uma Session
        start = now_time - timedelta(days=1)
        end = now_time + timedelta(days=1)
        results = fetch_events_in_range(test_db, start=start, end=end)
        assert len(results) == 3

    def test_fetch_with_ascending(self, test_db, sample_events):
        """Deve respeitar parâmetro ascending."""
        # test_db já é uma Session
        results = fetch_events_in_range(test_db, ascending=True)
        assert len(results) == 5
        assert results[0].title == "Event 1"
        assert results[-1].title == "Event 5"

    def test_fetch_empty_range(self, test_db, sample_events, now_time):
        """Deve retornar lista vazia quando nenhum evento no intervalo."""
        # test_db já é uma Session
        start = now_time + timedelta(days=100)
        end = now_time + timedelta(days=200)
        results = fetch_events_in_range(test_db, start=start, end=end)
        assert len(results) == 0

    def test_fetch_no_filters(self, test_db, sample_events):
        """Deve buscar todos os eventos quando nenhum filtro fornecido."""
        # test_db já é uma Session
        results = fetch_events_in_range(test_db)
        assert len(results) == 5
