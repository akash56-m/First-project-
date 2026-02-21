import io

import pytest

from app import create_app, db
from app.models import Complaint, Department, Service, User
from app.utils.security import hash_password
from config import TestConfig


@pytest.fixture()
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        dep = Department(name="Vigilance")
        db.session.add(dep)
        db.session.flush()
        service = Service(name="Bribery", department_id=dep.id)
        admin = User(username="admin", password_hash=hash_password("secret"), role="admin")
        officer = User(username="off1", password_hash=hash_password("secret"), role="officer", department_id=dep.id)
        db.session.add_all([service, admin, officer])
        db.session.commit()

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.drop_all()


def test_submit_and_track_complaint(client):
    response = client.post(
        "/complaints/submit",
        data={
            "department_id": 1,
            "service_id": 1,
            "description": "This is a detailed anonymous corruption complaint.",
            "evidence": (io.BytesIO(b"fakepdf"), "proof.pdf"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"tracking ID" in response.data


def test_unauthorized_admin_route_blocked(client):
    response = client.get("/admin/dashboard")
    assert response.status_code == 403


def test_login_and_assignment(client):
    login = client.post("/auth/login", data={"username": "admin", "password": "secret"}, follow_redirects=True)
    assert login.status_code == 200

    create = client.post(
        "/complaints/submit",
        data={"department_id": 1, "service_id": 1, "description": "A" * 40},
        follow_redirects=True,
    )
    assert create.status_code == 200

    with client.application.app_context():
        complaint = Complaint.query.first()
        cid = complaint.id

    assign = client.post(f"/admin/assign/{cid}", data={"officer_id": 2}, follow_redirects=True)
    assert assign.status_code == 200


def test_sql_injection_attempt_fails_login(client):
    response = client.post("/auth/login", data={"username": "admin' OR '1'='1", "password": "x"})
    assert b"Invalid credentials" in response.data
