"""Holdout binding (pytest-bdd): talks to the running product over HTTP only."""
import time

import httpx
from pytest_bdd import given, parsers, scenario, then, when

FEATURE = "features/anomaly-review/flag-anomaly.feature"


@scenario(FEATURE, "A reading outside the range is flagged within 5 minutes")  # @SC-4
def test_outside_range_is_flagged():
    pass


@scenario(FEATURE, "The summary states value, unit and difference from the mean")  # @SC-5
def test_summary_states_value_unit_and_difference():
    pass


@given(parsers.parse('the asset "{tag}" has the range {low} to {high} bar'))
def asset_range(base_url, tag, low, high):
    asset = next(a for a in httpx.get(f"{base_url}/v1/assets").json()["items"] if a["tag"] == tag)
    assert (asset["range_min"], asset["range_max"]) == (low, high)


@given(parsers.parse('the 30-day mean for "{tag}" is {mean} bar'))
def seeded_mean(seed_readings, tag, mean):
    seed_readings(tag, mean=mean, days=30)


@when(parsers.parse('a reading of {value} bar for "{tag}" syncs'), target_fixture="reading")
@when(parsers.parse('a reading of {value} bar for "{tag}" is flagged'), target_fixture="reading")
def reading_syncs(base_url, inspector_session, tag, value):
    return httpx.post(f"{base_url}/v1/readings", json={"asset_tag": tag, "value": value},
                      cookies=inspector_session).json()


def wait_for_anomaly(base_url, reading_id, minutes=5):
    deadline = time.time() + minutes * 60
    while time.time() < deadline:
        items = httpx.get(f"{base_url}/v1/anomalies", params={"reading_id": reading_id}).json()["items"]
        if items:
            return items[0]
        time.sleep(5)
    return None


@then("an open anomaly for that reading exists within 5 minutes")
def anomaly_exists(base_url, reading):
    anomaly = wait_for_anomaly(base_url, reading["id"])
    assert anomaly is not None and anomaly["decision"] is None


@then(parsers.parse('the anomaly\'s summary contains "{a}", "{b}" and "{c}"'))
def summary_contains(base_url, reading, a, b, c):
    summary = wait_for_anomaly(base_url, reading["id"])["summary"]
    assert all(part in summary for part in (a, b, c))
