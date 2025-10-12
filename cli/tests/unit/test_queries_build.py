"""Tests for build_events_query function."""

from datetime import timedelta

from sqlmodel import Session

from src.timeblock.utils.queries import build_events_query


class TestBuildEventsQuery:
    """Tests for build_events_query function."""

    def test_query_default_descending(self, test_db, sample_events):
        """Should order by scheduled_start descending by default."""
        with Session(test_db) as session:
            query = build_events_query(ascending=False)
            results = list(session.exec(query))

            assert len(results) == 5
            assert results[0].title == "Event 5"
            assert results[-1].title == "Event 1"

    def test_query_ascending(self, test_db, sample_events):
        """Should order by scheduled_start ascending when requested."""
        with Session(test_db) as session:
            query = build_events_query(ascending=True)
            results = list(session.exec(query))

            assert len(results) == 5
            assert results[0].title == "Event 1"
            assert results[-1].title == "Event 5"

    def test_query_with_start_date(self, test_db, sample_events, now_time):
        """Should filter events from start date."""
        with Session(test_db) as session:
            query = build_events_query(start=now_time, ascending=True)
            results = list(session.exec(query))

            assert len(results) == 3
            assert results[0].title == "Event 3"
            assert results[1].title == "Event 4"
            assert results[2].title == "Event 5"

    def test_query_with_end_date(self, test_db, sample_events, now_time):
        """Should filter events up to end date."""
        with Session(test_db) as session:
            query = build_events_query(end=now_time, ascending=True)
            results = list(session.exec(query))

            assert len(results) == 3
            assert results[0].title == "Event 1"
            assert results[1].title == "Event 2"
            assert results[2].title == "Event 3"

    def test_query_with_date_range(self, test_db, sample_events, now_time):
        """Should filter events within date range."""
        with Session(test_db) as session:
            start = now_time - timedelta(days=1)
            end = now_time + timedelta(days=1)
            query = build_events_query(start=start, end=end, ascending=True)
            results = list(session.exec(query))

            assert len(results) == 3
            assert results[0].title == "Event 2"
            assert results[1].title == "Event 3"
            assert results[2].title == "Event 4"

    def test_query_no_results(self, test_db, sample_events, now_time):
        """Should return empty list when no events match."""
        with Session(test_db) as session:
            start = now_time - timedelta(days=365)
            end = now_time - timedelta(days=300)
            query = build_events_query(start=start, end=end)
            results = list(session.exec(query))

            assert len(results) == 0
