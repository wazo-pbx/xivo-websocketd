# Copyright 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from .test_api.base import IntegrationTest, run_with_loop
from .test_api.constants import VALID_TOKEN_ID, INVALID_TOKEN_ID, UNAUTHORIZED_TOKEN_ID,\
    CLOSE_CODE_AUTH_FAILED, CLOSE_CODE_AUTH_EXPIRED, CLOSE_CODE_NO_TOKEN_ID


class TestAuthentication(IntegrationTest):

    asset = 'basic'

    @run_with_loop
    def test_no_token_closes_websocket(self):
        yield from self.websocketd_client.test_connect_failure(None,
                                                               CLOSE_CODE_NO_TOKEN_ID)

    @run_with_loop
    def test_valid_auth_gives_result(self):
        yield from self.websocketd_client.test_connect_success(VALID_TOKEN_ID)

    @run_with_loop
    def test_invalid_auth_closes_websocket(self):
        yield from self.websocketd_client.test_connect_failure(INVALID_TOKEN_ID,
                                                               CLOSE_CODE_AUTH_FAILED)

    @run_with_loop
    def test_unauthorized_auth_closes_websocket(self):
        yield from self.websocketd_client.test_connect_failure(UNAUTHORIZED_TOKEN_ID,
                                                               CLOSE_CODE_AUTH_FAILED)


class TestNoXivoAuth(IntegrationTest):

    asset = 'no_auth_server'

    @run_with_loop
    def test_no_auth_server_closes_websocket(self):
        yield from self.websocketd_client.test_connect_failure(VALID_TOKEN_ID)


class TestTokenExpiration(IntegrationTest):

    asset = 'token_expiration'

    _TIMEOUT = 15

    def setUp(self):
        super().setUp()
        self.token_id = 'dynamic-token'

    @run_with_loop
    def test_token_expire_closes_websocket(self):
        yield from self.auth_server.put_token(self.token_id)

        yield from self.websocketd_client.connect_and_wait_for_init(self.token_id)
        try:
            yield from self.auth_server.remove_token(self.token_id)
            yield from self.websocketd_client.wait_for_close(CLOSE_CODE_AUTH_EXPIRED,
                                                             timeout=self._TIMEOUT)
        finally:
            yield from self.websocketd_client.close()
