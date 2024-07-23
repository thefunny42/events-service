def test_metrics(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    metrics = response.text.splitlines()
    prefix = "# TYPE eventsservice"
    assert f"{prefix}_add_activity_created gauge" in metrics
    assert f"{prefix}_add_activity_failures_created gauge" in metrics
    assert f"{prefix}_list_activities_created gauge" in metrics
    assert f"{prefix}_list_activities_failures_created gauge" in metrics
    assert f"{prefix}_get_activity_created gauge" in metrics
    assert f"{prefix}_get_activity_failures_created gauge" in metrics
    assert f"{prefix}_delete_activity_created gauge" in metrics
    assert f"{prefix}_delete_activity_failures_created gauge" in metrics


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.content == b"{}"


def test_health_ready(client):
    response = client.get("/health?ready=true")
    assert response.status_code == 200
    assert response.json() == {}
