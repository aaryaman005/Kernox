def test_engine_exists():
    from app.db.session import engine

    assert engine is not None
