# Copyright 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import asyncio
import json

import requests

from requests.packages.urllib3 import disable_warnings


class AuthServer(object):

    def __init__(self, loop, port):
        self._loop = loop
        self._base_url = 'https://localhost:{port}/_control'.format(port=port)
        self._session = requests.Session()
        self._session.verify = False
        disable_warnings()

    @asyncio.coroutine
    def put_token(self, token_id, auth_id='123-456', acls=[]):
        token = {
            'token': token_id,
            'auth_id': auth_id,
            'acls': acls,
        }
        return (yield from self._loop.run_in_executor(None, self._sync_put_token, token))

    def _sync_put_token(self, token):
        url = '{}/token/{}'.format(self._base_url, token['token'])
        headers = {'Content-Type': 'application/json'}
        r = self._session.put(url, headers=headers, data=json.dumps(token))
        if r.status_code != 204:
            r.raise_for_status()

    @asyncio.coroutine
    def remove_token(self, token_id):
        return (yield from self._loop.run_in_executor(None, self._sync_remove_token, token_id))

    def _sync_remove_token(self, token_id):
        url = '{}/token/{}'.format(self._base_url, token_id)
        r = self._session.delete(url)
        if r.status_code != 204:
            r.raise_for_status()
