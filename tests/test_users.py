def test_create_user(session):
    from sqlmodel import select

    from app.auth import get_password_hash
    from app.models.user import User, UserRole

    users = session.exec(select(User)).all()
    assert len(users) == 0, "Database should be empty"

    # create test user an admin since we don't have teams yet
    db_user = User(
        username="testuser1",
        full_name="Test User",
        email="test@user.com",
        hashed_password=get_password_hash("testpassword"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    assert db_user.id is not None, "User should be created with an ID"

    # test user exists
    users = session.exec(select(User)).all()
    assert len(users) == 1, "Database should have one user"
    assert users[0].username == "testuser1", "User should be testuser1"
