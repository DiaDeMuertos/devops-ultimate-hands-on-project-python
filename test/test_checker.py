import pytest
import requests
from pytest_mock import MockerFixture

from simple_http_checker.checker import check_url


def test_check_url_success(mocker: MockerFixture):
    mock_request_get = mocker.patch("simple_http_checker.checker.requests.get")

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_response.ok = True
    mock_request_get.return_value = mock_response

    urls = ["http://example.com"]
    results = check_url(urls)

    mock_request_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == "200 OK"


def test_check_url_client_error(mocker: MockerFixture):
    mock_request_get = mocker.patch("simple_http_checker.checker.requests.get")

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mock_response.ok = False
    mock_request_get.return_value = mock_response

    urls = ["http://example.com/notfound"]
    results = check_url(urls)

    mock_request_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == "404 Not Found"


@pytest.mark.parametrize(
    "error_exception, expected_status",
    [
        (requests.exceptions.Timeout, "TIMEOUT"),
        (requests.exceptions.ConnectionError, "CONNECTION_ERROR"),
        (requests.exceptions.RequestException, "REQUEST_ERROR: RequestException"),
    ],
)
def test_check_url_request_exceptions(
    mocker: MockerFixture,
    error_exception: type[requests.exceptions.RequestException],
    expected_status: str,
):
    mock_request_get = mocker.patch("simple_http_checker.checker.requests.get")

    mock_request_get.side_effect = error_exception(f"Simulated {expected_status}")

    urls = ["http://example.com"]
    results = check_url(urls)

    mock_request_get.assert_called_once_with(urls[0], timeout=5)
    assert results[urls[0]] == expected_status


def test_check_url_with_multiple_urls(mocker: MockerFixture):
    # First call: OK
    mock_response_ok = mocker.MagicMock(spec=requests.Response)
    mock_response_ok.status_code = 200
    mock_response_ok.reason = "OK"
    mock_response_ok.ok = True

    # Second call: 500 Server Error
    timeout_exception = requests.exceptions.Timeout("Simulated TIMEOUT")

    # Third call: ConnectionError
    mock_response_fail = mocker.MagicMock(spec=requests.Response)
    mock_response_fail.status_code = 500
    mock_response_fail.reason = "Server Error"
    mock_response_fail.ok = False

    # mock side effects for three calls
    mock_request_get = mocker.patch("simple_http_checker.checker.requests.get")
    mock_request_get.side_effect = [
        mock_response_ok,
        timeout_exception,
        mock_response_fail,
    ]

    urls = ["http://success.com", "http://timeout.com", "http://servererror.com"]
    results = check_url(urls)

    assert len(results) == 3
    assert mock_request_get.call_count == 3
    assert results["http://success.com"] == "200 OK"
    assert results["http://timeout.com"] == "TIMEOUT"
    assert results["http://servererror.com"] == "500 Server Error"


def test_check_url_empty_list():
    resukts = check_url([])

    assert resukts == {}


def test_check_url_custom_timeout(mocker: MockerFixture):
    mock_request_get = mocker.patch("simple_http_checker.checker.requests.get")

    mock_response = mocker.MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.reason = "OK"
    mock_response.ok = True
    mock_request_get.return_value = mock_response

    urls = ["http://example.com"]
    custom_timeout = 5
    results = check_url(urls, timeout=custom_timeout)

    mock_request_get.assert_called_once_with(urls[0], timeout=custom_timeout)
    assert results[urls[0]] == "200 OK"
