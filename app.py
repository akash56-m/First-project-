from app import create_app, db
from app.models import Department, Service, User
from app.utils.security import hash_password

app = create_app()


@app.cli.command("seed")
def seed():
    if Department.query.count() > 0:
        return

    vigilance = Department(name="Vigilance", description="Anti-corruption and integrity")
    sanitation = Department(name="Sanitation", description="Waste and cleanliness")
    db.session.add_all([vigilance, sanitation])
    db.session.flush()

    db.session.add_all(
        [
            Service(name="Bribery Complaint", department_id=vigilance.id),
            Service(name="Delayed Approval", department_id=vigilance.id),
            Service(name="Garbage Collection", department_id=sanitation.id),
        ]
    )

    admin = User(username="admin", password_hash=hash_password("Admin@123"), role="admin")
    db.session.add(admin)
    db.session.commit()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
