"""Mocked provider tests: these never provision or contact a Runpod host."""

from __future__ import annotations

import io
import json
import urllib.error
import urllib.parse

import pytest

from scripts import runpodctl


def launch_args(max_hourly: float = 0.30):
    args = runpodctl.parser().parse_args(
        ["launch", "--name", "test-owned-worker", "--gpu", "test-gpu", "--max-hourly", "0.30"]
    )
    args.max_hourly = max_hourly
    return args


@pytest.fixture(autouse=True)
def prohibit_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_request(*args, **kwargs):
        pytest.fail("tests must never access the network")

    monkeypatch.setattr(runpodctl.urllib.request, "urlopen", unexpected_request)


@pytest.mark.parametrize("ceiling", [float("nan"), float("inf"), -float("inf"), 0.0, -0.1])
@pytest.mark.parametrize("command", ["launch", "catalog"])
def test_invalid_ceiling_is_rejected_before_any_provider_call(
    monkeypatch: pytest.MonkeyPatch, ceiling: float, command: str
) -> None:
    def unexpected_request(*args, **kwargs):
        pytest.fail("invalid ceiling must be rejected before requesting provider data")

    monkeypatch.setattr(runpodctl, "request_json", unexpected_request)
    monkeypatch.setattr(runpodctl, "graphql", unexpected_request)
    with pytest.raises(SystemExit, match="finite and positive"):
        getattr(runpodctl, command)(launch_args(ceiling))


def mock_launch_response(monkeypatch: pytest.MonkeyPatch, response, deletion_error=None):
    calls = []

    def request(method, url, *, payload=None):
        calls.append((method, url, payload))
        if method == "GET":
            return []
        if method == "POST":
            return response
        if method == "DELETE":
            if deletion_error is not None:
                raise deletion_error
            return None
        pytest.fail(f"unexpected request method {method}")

    monkeypatch.setattr(runpodctl, "request_json", request)
    return calls


@pytest.mark.parametrize("cost", [None, "not a price", float("nan"), float("inf"), -float("inf"), -0.1, {}, True])
def test_invalid_returned_cost_cleans_up_only_the_new_pod(
    monkeypatch: pytest.MonkeyPatch, cost
) -> None:
    calls = mock_launch_response(
        monkeypatch, {"id": "created-pod", "adjustedCostPerHr": cost}
    )
    with pytest.raises(SystemExit, match="termination request succeeded"):
        runpodctl.launch(launch_args())
    assert [method for method, _, _ in calls] == ["GET", "POST", "DELETE"]
    assert calls[-1][1] == f"{runpodctl.REST_BASE}/pods/created-pod"


def test_missing_cost_cleans_up_the_new_pod(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = mock_launch_response(monkeypatch, {"id": "created-pod"})
    with pytest.raises(SystemExit, match="missing or malformed hourly cost"):
        runpodctl.launch(launch_args())
    assert calls[-1][:2] == ("DELETE", f"{runpodctl.REST_BASE}/pods/created-pod")


def test_invalid_adjusted_cost_does_not_fall_back_to_affordable_base_cost(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = mock_launch_response(
        monkeypatch,
        {"id": "created-pod", "adjustedCostPerHr": None, "costPerHr": 0.1},
    )
    with pytest.raises(SystemExit, match="missing or malformed hourly cost"):
        runpodctl.launch(launch_args())
    assert calls[-1][0] == "DELETE"


def test_above_ceiling_cost_cleans_up_the_new_pod(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = mock_launch_response(monkeypatch, {"id": "created-pod", "costPerHr": 0.31})
    with pytest.raises(SystemExit, match="above.*ceiling.*termination request succeeded"):
        runpodctl.launch(launch_args())
    assert calls[-1][0] == "DELETE"


@pytest.mark.parametrize("response", [{"costPerHr": 0.9}, {"id": None, "costPerHr": 0.2}, None])
def test_missing_pod_id_does_not_claim_termination(
    monkeypatch: pytest.MonkeyPatch, response
) -> None:
    calls = mock_launch_response(monkeypatch, response)
    with pytest.raises(SystemExit, match="no usable pod ID.*termination is unconfirmed") as error:
        runpodctl.launch(launch_args())
    assert "termination request succeeded" not in str(error.value)
    assert [method for method, _, _ in calls] == ["GET", "POST"]


@pytest.mark.parametrize("deletion_error", [SystemExit("HTTP 503"), OSError("connection reset")])
def test_cleanup_failure_does_not_claim_termination(
    monkeypatch: pytest.MonkeyPatch, deletion_error
) -> None:
    calls = mock_launch_response(
        monkeypatch, {"id": "created-pod", "costPerHr": 1.0}, deletion_error
    )
    with pytest.raises(SystemExit, match="cleanup request failed.*termination is unconfirmed") as error:
        runpodctl.launch(launch_args())
    assert "termination request succeeded" not in str(error.value)
    assert calls[-1][0] == "DELETE"


@pytest.mark.parametrize("cost", [0.0, 0.2, 0.3, "0.2"])
def test_finite_affordable_cost_is_reported_without_cleanup(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], cost
) -> None:
    calls = mock_launch_response(
        monkeypatch, {"id": "created-pod", "name": "test-owned-worker", "costPerHr": cost}
    )
    runpodctl.launch(launch_args())
    result = json.loads(capsys.readouterr().out)
    assert result["id"] == "created-pod"
    assert result["cost_per_hour"] == float(cost)
    assert [method for method, _, _ in calls] == ["GET", "POST"]


def test_http_error_redacts_raw_and_query_encoded_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    key = "test/key+with spaces"
    encoded = urllib.parse.quote_plus(key, safe="")
    monkeypatch.setattr(runpodctl, "api_key", lambda: key)

    def fail_request(*args, **kwargs):
        raise urllib.error.HTTPError(
            "https://example.invalid", 403, "Forbidden", {},
            io.BytesIO(f"Bearer {key}; api_key={encoded}".encode()),
        )

    monkeypatch.setattr(runpodctl.urllib.request, "urlopen", fail_request)
    with pytest.raises(SystemExit) as error:
        runpodctl.request_json("GET", "https://example.invalid")
    assert key not in str(error.value)
    assert encoded not in str(error.value)
    assert str(error.value).count("[REDACTED]") == 2
    assert isinstance(error.value, runpodctl.RunpodHTTPError)
    assert error.value.status_code == 403
    assert set(vars(error.value)) == {"status_code"}


def test_graphql_error_redacts_json_escaped_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    key = 'test-key-with-"quote'
    monkeypatch.setattr(runpodctl, "api_key", lambda: key)
    monkeypatch.setattr(
        runpodctl, "request_json", lambda *args, **kwargs: {"errors": [{"message": f"Invalid key: {key}"}]}
    )
    with pytest.raises(SystemExit) as error:
        runpodctl.graphql("query { gpuTypes { id } }")
    assert key not in str(error.value)
    assert json.dumps(key)[1:-1] not in str(error.value)
    assert "[REDACTED]" in str(error.value)


def test_url_error_redacts_query_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    key = "test/key+with spaces"
    encoded = urllib.parse.quote_plus(key, safe="")
    monkeypatch.setattr(runpodctl, "api_key", lambda: key)

    def fail_request(*args, **kwargs):
        raise urllib.error.URLError(f"connection failed at https://example.invalid?api_key={encoded}")

    monkeypatch.setattr(runpodctl.urllib.request, "urlopen", fail_request)
    with pytest.raises(SystemExit) as error:
        runpodctl.request_json("GET", "https://example.invalid")
    assert encoded not in str(error.value)
    assert "[REDACTED]" in str(error.value)
    assert not isinstance(error.value, runpodctl.RunpodHTTPError)
