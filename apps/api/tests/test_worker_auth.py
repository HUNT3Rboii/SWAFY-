from swafy_api.api.dependencies import verify_worker_token


def test_worker_token_is_separate_exact_secret():
    expected = "internal-worker-token-which-is-not-a-user-jwt"
    assert verify_worker_token(expected, expected)
    assert not verify_worker_token("wrong-token", expected)
    assert not verify_worker_token("", "")
