def test_stats_on_empty_database_are_zero(client):
    stats = client.get("/api/stats").json()
    assert stats["total"] == 0
    assert stats["avg_mean"] == 0.0


def test_stats_count_each_group_and_average(client, make_payload):
    client.post("/api/feedback", json=make_payload())  # 5,4,5 -> promoter
    client.post(
        "/api/feedback",
        json=make_payload(email="b@x.com", product_rating=3, care_rating=3, happy_rating=3),
    )
    client.post(
        "/api/feedback",
        json=make_payload(email="c@x.com", product_rating=1, care_rating=1, happy_rating=1),
    )
    stats = client.get("/api/stats").json()
    assert (stats["total"], stats["promoters"], stats["passives"], stats["detractors"]) == (
        3,
        1,
        1,
        1,
    )
    assert stats["avg_product"] == 3.0  # (5 + 3 + 1) / 3
    assert stats["avg_care"] == 2.67  # (4 + 3 + 1) / 3


def test_trend_groups_by_day(client, make_payload):
    client.post("/api/feedback", json=make_payload())
    client.post("/api/feedback", json=make_payload(email="b@x.com"))
    trend = client.get("/api/trend").json()
    assert len(trend["points"]) == 1
    assert trend["points"][0]["count"] == 2
    assert trend["projection"] == []  # a projection needs two different days


def test_trend_rejects_bad_days(client):
    assert client.get("/api/trend?days=0").status_code == 422


def test_responses_newest_first_with_customer(client, make_payload):
    client.post("/api/feedback", json=make_payload(name="First Person"))
    client.post(
        "/api/feedback", json=make_payload(name="Second Person", email="b@x.com", phone=None)
    )
    items = client.get("/api/responses").json()
    assert [i["customer"]["name"] for i in items] == ["First Person", "Second Person"][::-1]


def test_responses_pagination(client, make_payload):
    for i in range(3):
        client.post("/api/feedback", json=make_payload(email=f"p{i}@x.com"))
    assert len(client.get("/api/responses?limit=2").json()) == 2
    assert len(client.get("/api/responses?limit=2&offset=2").json()) == 1
    assert client.get("/api/responses?limit=0").status_code == 422


def test_drill_down_and_404(client, make_payload):
    client.post("/api/feedback", json=make_payload())
    one = client.get("/api/responses/1").json()
    assert (one["product_rating"], one["care_rating"], one["happy_rating"]) == (5, 4, 5)
    assert client.get("/api/responses/99").status_code == 404
