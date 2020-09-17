from unittest.mock import patch

from roles.decorators import ROLES_KEY
from app.workflows.models import db, Workflow
from app.utils import to_iso8601
from app.workflows.queries import find_workflow


def test_create_workflow_bad_content_type(client, client_application):
    db.session.commit()
    result = client.post(
        "/v1/workflows",
        content_type="text/html",
        json={"name": "a workflow", "description": "desc"},
        headers={ROLES_KEY: client_application.api_key},
    )
    assert result.status_code == 400
    assert set(result.json.keys()) == set(["message"])


@patch("app.workflows.routes.create_workflow")
def test_create_workflow_failure(create_workflow_mock, client, client_application):
    create_workflow_mock.side_effect = ValueError("failure")
    db.session.commit()
    result = client.post(
        "/v1/workflows",
        content_type="application/json",
        json={"name": "a workflow", "description": "desc"},
        headers={ROLES_KEY: client_application.api_key},
    )
    assert result.status_code == 400
    assert set(result.json.keys()) == set(["message"])


def test_create_workflow_bad_input(client, client_application):
    db.session.commit()
    result = client.post(
        "/v1/workflows",
        content_type="application/json",
        json={},
        headers={ROLES_KEY: client_application.api_key},
    )
    assert result.status_code == 400
    assert set(result.json["errors"].keys()) == set(["description", "name"])


def test_create_workflow(client, client_application):
    db.session.commit()
    params = {"name": "a workflow", "description": "desc"}
    result = client.post(
        "/v1/workflows",
        content_type="application/json",
        json=params,
        headers={ROLES_KEY: client_application.api_key},
    )
    assert result.status_code == 200
    workflow = Workflow.query.filter(Workflow.name == params["name"]).one_or_none()
    assert result.json == {
        "uuid": workflow.uuid,
        "name": workflow.name,
        "description": workflow.description,
        "created_at": to_iso8601(workflow.created_at),
        "updated_at": to_iso8601(workflow.updated_at),
    }


def test_remove_workflow_no_uuid(client, client_application):
    db.session.commit()
    result = client.delete(
        f"/v1/workflows/nouuid",
        headers={ROLES_KEY: client_application.api_key},
    )
    assert result.status_code == 400


def test_remove_workflow(client, client_application, workflow):
    the_uuid = workflow.uuid
    db.session.commit()
    result = client.delete(
        f"/v1/workflows/{the_uuid}",
        headers={ROLES_KEY: client_application.api_key},
    )
    assert result.status_code == 200
    assert find_workflow(the_uuid) is None


def test_update_workflow_failure(client, client_application):
    db.session.commit()
    result = client.put(
        "/v1/workflows/no-id",
        content_type="application/json",
        json={"name": "a workflow", "description": "desc"},
        headers={ROLES_KEY: client_application.api_key},
    )
    assert result.status_code == 400
    assert set(result.json.keys()) == set(["message"])


def test_update_workflow_bad_input(client, client_application, workflow):
    db.session.commit()
    result = client.put(
        f"/v1/workflows/{workflow.uuid}",
        content_type="application/json",
        json={},
        headers={ROLES_KEY: client_application.api_key},
    )
    assert result.status_code == 400
    assert set(result.json["errors"].keys()) == set(["description", "name"])


def test_update_workflow(client, client_application, workflow):
    db.session.commit()
    params = {"name": "new workflow", "description": "new desc"}
    result = client.put(
        f"/v1/workflows/{workflow.uuid}",
        content_type="application/json",
        json=params,
        headers={ROLES_KEY: client_application.api_key},
    )
    assert result.status_code == 200
    workflow = Workflow.query.filter(Workflow.name == "new workflow").one_or_none()
    assert result.json == {
        "uuid": workflow.uuid,
        "name": "new workflow",
        "description": "new desc",
        "created_at": to_iso8601(workflow.created_at),
        "updated_at": to_iso8601(workflow.updated_at),
    }