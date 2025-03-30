import random

from models.waste import WasteLog, WasteType
from sqlmodel import Session, delete, select

from app.auth import get_password_hash
from app.config import settings
from app.db.session import engine
from app.models.team import Team
from app.models.user import User, UserRole


def wipe_existing_data(session: Session) -> None:
    # Wipe all existing data - won't reset row numbers though
    session.exec(delete(WasteLog))
    session.exec(delete(User))
    session.exec(delete(Team))
    session.commit()
    print("Wiped existing data.")


def create_admin_account(session: Session) -> None:
    # create admin account
    admin = User(
        username=settings.ADMIN_USERNAME,
        full_name="Admin User",
        email=settings.ADMIN_EMAIL,
        hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
        role=UserRole.ADMIN,
        is_active=True,
    )
    session.add(admin)
    print("Created new admin account.")
    session.commit()


def seed_teams(session: Session) -> None:
    # Create 3 default teams
    for i in range(3):
        team = Team(name=f"Team {i + 1}")
        session.add(team)
        print(f"Created default team: Team {i + 1}.")
    session.commit()
    print("Seeded default teams.")


def seed_managers(session: Session) -> None:
    # Create a manager for every team
    teams = session.exec(select(Team)).all()
    for team in teams:
        manager = User(
            username=f"{team.name.lower().replace(' ', '_')}_manager",
            email=f"{team.name.lower().replace(' ', '_')}_manager@example.com",
            full_name=f"{team.name} Manager",
            hashed_password=get_password_hash("manager"),
            role=UserRole.MANAGER,
            team_id=team.id,
            is_active=True,
        )
        session.add(manager)
        print(f"Created manager for {team.name}: {manager.username}.")
    session.commit()
    print("Seeded managers for all teams.")


def seed_employees(session: Session) -> None:
    # Create 5 employees for every team
    teams = session.exec(select(Team)).all()
    for team in teams:
        for i in range(5):
            employee = User(
                username=f"{team.name.lower().replace(' ', '_')}_employee_{i+1}",
                email=f"{team.name.lower().replace(' ', '_')}_employee_{i+1}@example.com",
                full_name=f"{team.name} Employee {i+1}",
                hashed_password=get_password_hash("employee"),
                role=UserRole.EMPLOYEE,
                team_id=team.id,
                is_active=True,
            )
            session.add(employee)
            print(f"Created employee for {team.name}: {employee.username}.")
    session.commit()
    print("Seeded employees for all teams.")


def seed_waste_logs(session: Session) -> None:
    # Create between 0 and 15 random waste logs for all employees
    employees = session.exec(select(User).where(User.role == UserRole.EMPLOYEE)).all()
    for employee in employees:
        for _ in range(random.randint(0, 15)):
            waste_log = WasteLog(
                created_by_id=employee.id,
                team_id=employee.team_id,
                waste_type=random.choice(list(WasteType)),
                weight_kg=random.randint(1, 100),
            )
            session.add(waste_log)
            print(f"Created waste log for {employee.username}: {waste_log}.")
    session.commit()
    print("Seeded waste logs for all employees.")


def run():
    with Session(engine) as session:
        wipe_existing_data(session)
        create_admin_account(session)
        seed_teams(session)
        seed_managers(session)
        seed_employees(session)
        seed_waste_logs(session)

        print("Completed: setup_service.py")


if __name__ == "__main__":
    run()
