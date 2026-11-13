"""Holdout binding (pytest-bdd): talks to the running product over HTTP and the browser only."""
import httpx
from pytest_bdd import given, parsers, scenario, then, when

FEATURE = "features/anomaly-review/review-queue.feature"


@scenario(FEATURE, "A decision by an inspector is refused")  # @SC-6
def test_inspector_decision_is_refused():
    pass


@scenario(FEATURE, "The planner sees the anomaly with the asset's range")  # @SC-7
def test_planner_sees_the_range():
    pass


@given(parsers.parse('an open anomaly for the asset "{tag}"'), target_fixture="anomaly_id")
def open_anomaly(seed_anomaly, tag):
    return seed_anomaly(tag)


@given("an inspector is signed in", target_fixture="session")
def inspector(inspector_session):
    return inspector_session


@given("a planner is signed in")
def planner(planner_page):
    return planner_page


@when("the inspector tries to confirm the anomaly", target_fixture="response")
def inspector_confirms(base_url, session, anomaly_id):
    return httpx.post(f"{base_url}/v1/anomalies/{anomaly_id}/decision", json={"decision": "confirmed"}, cookies=session)


@when("the planner opens Review Queue")
def planner_opens_queue(planner_page):
    planner_page.goto("/review")


@then("the decision is refused")
def refused(response):
    assert response.status_code == 403


@then("the anomaly is still open")
def still_open(base_url, planner_session, anomaly_id):
    assert httpx.get(f"{base_url}/v1/anomalies/{anomaly_id}", cookies=planner_session).json()["decision"] is None


@then(parsers.parse('the anomaly for "{tag}" is listed with the range {low} to {high} bar'))
def listed_with_range(planner_page, tag, low, high):
    text = planner_page.get_by_role("row", name=tag).inner_text()
    assert low in text and high in text
