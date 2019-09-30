# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import collections
import json
import logging


from .exception import SessionProtocolError

logger = logging.getLogger(__name__)

_UNSET = object()


class SessionProtocolEncoder(object):

    _CODE_SUCCESS = 0
    _CODe_FAILURE = 1
    _MSG_OK = ''

    def encode_init(self):
        return self._encode('init')

    def encode_subscribe(self):
        return self._encode('subscribe')

    def encode_start(self):
        return self._encode('start')

    def encode_token(self, success=False):
        if success:
            return self._encode('token')
        else:
            return self._encode('token', code=self._CODE_FAILURE, msg="Invalid token")

    def encode_event(self, event):
        self._encode("event", msg=event)

    def _encode(self, operation, code=_CODE_SUCCESS, msg=_MSG_OK):
        return json.dumps({'op': operation, 'code': code, 'msg': msg})


class SessionProtocolDecoder(object):
    def decode(self, data):
        if not isinstance(data, str):
            raise SessionProtocolError(
                'expected text frame: got data with type {}'.format(type(data))
            )
        try:
            deserialized_data = json.loads(data)
        except ValueError:
            raise SessionProtocolError('not a valid json document')
        if not isinstance(deserialized_data, dict):
            raise SessionProtocolError('json document root is not an object')
        if 'op' not in deserialized_data:
            raise SessionProtocolError('object is missing required "op" key')
        operation = deserialized_data['op']
        if not isinstance(operation, str):
            raise SessionProtocolError('object "op" value is not a string')

        func_name = '_decode_{}'.format(operation)
        func = getattr(self, func_name, self._decode)
        return func(operation, deserialized_data)

    def _decode(self, operation, deserialized_data):
        return _Message(operation, None)

    def _decode_token(self, operation, deserialized_data):
        return self._get("token", operation, deserialized_data, str)

    def _decode_subscribe(self, operation, deserialized_data):
        return self._get("event_name", operation, deserialized_data, str)

    def _decode_start(self, operation, deserialized_data):
        msg = self._get("version", operation, deserialized_data, int, 1)
        if msg.value in [1, 2]:
            return msg
        else:
            raise SessionProtocolError('invalid protocal version: {}'.format(msg.value))

    @staticmethod
    def _get(attribute, operation, deserialized_data, _type, default=_UNSET):
        if 'data' not in deserialized_data:
            raise SessionProtocolError('object is missing required "data" key')
        if not isinstance(deserialized_data['data'], dict):
            raise SessionProtocolError('object "data" value is not an object')

        if attribute in deserialized_data['data']:
            value = deserialized_data['data'][attribute]
        elif default != _UNSET:
            value = default
        else:
            raise SessionProtocolError(
                'object "data" is missing required "{}" key'.format(attribute)
            )

        if not isinstance(value, _type):
            raise SessionProtocolError(
                'object data "{}" value is not a {}'.format(value, _type)
            )
        return _Message(operation, value)


_Message = collections.namedtuple('_Message', ['op', 'value'])
