import uuid
from collections.abc import Generator
from unittest.mock import ANY

import pytest
from clickhouse_connect.driver import Client
from django.conf import settings

from users.use_cases import CreateUser, CreateUserRequest, UserCreated
from users.models import User
import json

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def f_use_case() -> CreateUser:
    return CreateUser()


@pytest.fixture(autouse=True)
def f_clean_up_event_log(f_ch_client: Client) -> Generator:
    f_ch_client.command(f"TRUNCATE TABLE event_log") # Buffer table doesn't support truncate/delete, ideally use env instead of hardcode
    yield

def test_user_created_in_postgres(f_use_case: CreateUser) -> None:
    request = CreateUserRequest(
        email="test@email.com", first_name="Test", last_name="Testovich"
    )
    response = f_use_case.execute(request)
    assert response.result.email == "test@email.com"
    assert response.error == ""

    user = User.objects.get(email="test@email.com")
    assert user.first_name == "Test"
    assert user.last_name == "Testovich"


def test_emails_are_unique_in_postgres(f_use_case: CreateUser) -> None:
    request = CreateUserRequest(
        email="test@email.com", first_name="Test", last_name="Testovich"
    )

    f_use_case.execute(request)

    response = f_use_case.execute(request)
    assert response.result is None
    assert response.error == "User with this email already exists"

    assert User.objects.filter(email="test@email.com").count() == 1


def test_event_log_entry_published(
    f_use_case: CreateUser,
    f_ch_client: Client,
) -> None:
    email = f"test_{uuid.uuid4()}@email.com"
    request = CreateUserRequest(
        email=email, first_name="Test", last_name="Testovich"
    )
    response = f_use_case.execute(request)
    assert response.result.email == email
    assert response.error == ""
    from users.tasks import process_event_logs_task
    process_event_logs_task()
    log = f_ch_client.query(
        f"SELECT * FROM {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME} WHERE event_type = 'user_created'"
    )
    assert len(log.result_rows) == 1
    actual_payload = json.loads(log.result_rows[0][3])
    expected_payload = {
        "email": email,
        "first_name": "Test",
        "last_name": "Testovich",
        "event_type": "UserCreated"
    }
    assert actual_payload == expected_payload