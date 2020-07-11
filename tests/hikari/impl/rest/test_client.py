# -*- coding: utf-8 -*-
# Copyright © Nekoka.tt 2019-2020
#
# This file is part of Hikari.
#
# Hikari is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hikari is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hikari. If not, see <https://www.gnu.org/licenses/>.
import aiohttp
import contextlib
import asyncio
import http

import mock
import pytest

from hikari import errors
from hikari import config
from hikari.models import channels
from hikari.models import permissions
from hikari.impl import rate_limits
from hikari.impl.rest import client
from hikari.api.rest import app
from hikari.utilities import routes
from hikari.utilities import snowflake
from hikari.utilities import undefined
from hikari.utilities import constants
from hikari.utilities import net
from tests.hikari import client_session_stub
from tests.hikari import hikari_test_helpers


@pytest.fixture
def stub_app():
    return mock.Mock(spec=app.IRESTApp, entity_factory=mock.Mock())


@pytest.fixture
def rest_client(stub_app):
    obj = hikari_test_helpers.unslot_class(client.RESTClientImpl)(
        app=stub_app,
        connector=mock.Mock(),
        connector_owner=True,
        debug=True,
        global_ratelimit=mock.Mock(spec=rate_limits.ManualRateLimiter),
        http_settings=mock.Mock(spec=config.HTTPSettings),
        proxy_settings=mock.Mock(spec=config.ProxySettings),
        token="some_token",
        token_type="tYpe",
        rest_url="https://some.where/api/v{0.version}",
        version=3,
    )
    obj.buckets = mock.Mock()
    obj.global_rate_limit = mock.Mock()
    return obj


@pytest.fixture
def stub_model():
    class StubModel(snowflake.Unique):
        id = None

        def __init__(self, id):
            self.id = snowflake.Snowflake(id)

    return StubModel


class TestRESTClientImpl:
    def test__init__when_token_is_None_sets_token_to_None(self):
        obj = client.RESTClientImpl(
            app=mock.Mock(),
            connector=mock.Mock(),
            connector_owner=True,
            debug=True,
            global_ratelimit=mock.Mock(),
            http_settings=mock.Mock(),
            proxy_settings=mock.Mock(),
            token=None,
            token_type=None,
            rest_url=None,
            version=1,
        )
        assert obj._token is None

    def test__init__when_token_is_not_None_and_token_type_is_None_generates_token_with_default_type(self):
        obj = client.RESTClientImpl(
            app=mock.Mock(),
            connector=mock.Mock(),
            connector_owner=True,
            debug=True,
            global_ratelimit=mock.Mock(),
            http_settings=mock.Mock(),
            proxy_settings=mock.Mock(),
            token="some_token",
            token_type=None,
            rest_url=None,
            version=1,
        )
        assert obj._token == "Bot some_token"

    def test__init__when_token_and_token_type_is_not_None_generates_token_with_type(self):
        obj = client.RESTClientImpl(
            app=mock.Mock(),
            connector=mock.Mock(),
            connector_owner=True,
            debug=True,
            global_ratelimit=mock.Mock(),
            http_settings=mock.Mock(),
            proxy_settings=mock.Mock(),
            token="some_token",
            token_type="tYpe",
            rest_url=None,
            version=1,
        )
        assert obj._token == "Type some_token"

    def test__init__when_rest_url_is_None_generates_url_using_default_url(self):
        obj = client.RESTClientImpl(
            app=mock.Mock(),
            connector=mock.Mock(),
            connector_owner=True,
            debug=True,
            global_ratelimit=mock.Mock(),
            http_settings=mock.Mock(),
            proxy_settings=mock.Mock(),
            token=None,
            token_type=None,
            rest_url=None,
            version=1,
        )
        assert obj._rest_url == "https://discord.com/api/v1"

    def test__init__when_rest_url_is_not_None_generates_url_using_given_url(self):
        obj = client.RESTClientImpl(
            app=mock.Mock(),
            connector=mock.Mock(),
            connector_owner=True,
            debug=True,
            global_ratelimit=mock.Mock(),
            http_settings=mock.Mock(),
            proxy_settings=mock.Mock(),
            token=None,
            token_type=None,
            rest_url="https://some.where/api/v{0.version}",
            version=2,
        )
        assert obj._rest_url == "https://some.where/api/v2"

    def test_app_property(self, rest_client):
        app_mock = mock.Mock()
        rest_client._app = app_mock

        assert rest_client.app is app_mock

    def test__acquire_client_session_when_None(self, rest_client):
        client_session_mock = client_session_stub.ClientSessionStub()
        connector_mock = mock.Mock()
        rest_client._connector = connector_mock
        rest_client._http_settings.timeouts.total = 10
        rest_client._http_settings.timeouts.acquire_and_connect = 5
        rest_client._http_settings.timeouts.request_socket_read = 4
        rest_client._http_settings.timeouts.request_socket_connect = 1
        rest_client._proxy_settings.trust_env = False
        rest_client._client_session = None

        with mock.patch.object(aiohttp, "ClientSession", return_value=client_session_mock) as client_session:
            assert rest_client._acquire_client_session() is client_session_mock
            client_session.assert_called_once_with(
                connector=connector_mock,
                version=aiohttp.HttpVersion11,
                timeout=aiohttp.ClientTimeout(total=10, connect=5, sock_read=4, sock_connect=1),
                trust_env=False,
            )

    def test__acquire_client_session_when_not_None(self, rest_client):
        client_session_mock = mock.Mock()
        rest_client._client_session = client_session_mock

        assert rest_client._acquire_client_session() is client_session_mock

    @pytest.mark.parametrize(
        ["function_input", "expected_output"],
        [
            ((True, True, True), {"parse": ["everyone", "users", "roles"]}),
            ((False, False, False), {"parse": []}),
            ((undefined.UNDEFINED, undefined.UNDEFINED, undefined.UNDEFINED), {"parse": []}),
            ((False, [123], [456]), {"parse": [], "users": ["123"], "roles": ["456"]}),
            (
                (True, [123, "123", 987], ["213", "456", 456]),
                {"parse": ["everyone"], "users": ["123", "987"], "roles": ["213", "456"]},
            ),
        ],
    )
    def test__generate_allowed_mentions(self, rest_client, function_input, expected_output):
        returned = rest_client._generate_allowed_mentions(*function_input)
        if returned is not undefined.UNDEFINED:
            for k in returned.keys():
                returned[k] = sorted(returned[k])

        if expected_output is not undefined.UNDEFINED:
            for k in expected_output.keys():
                expected_output[k] = sorted(expected_output[k])

        assert returned == expected_output


@pytest.mark.asyncio
class TestRESTClientImplAsync:
    @pytest.fixture
    def exit_exception(self):
        class ExitException(Exception):
            ...

        return ExitException

    @hikari_test_helpers.timeout()
    async def test__request_when_buckets_not_started(self, rest_client, exit_exception):
        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        rest_client.buckets.is_started = False
        with mock.patch.object(asyncio, "gather", new=mock.AsyncMock(side_effect=exit_exception)):
            with pytest.raises(exit_exception):
                await rest_client._request(route)

            rest_client.buckets.start.assert_called_once()

    @hikari_test_helpers.timeout()
    async def test__request_when_buckets_started(self, rest_client, exit_exception):
        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        rest_client.buckets.is_started = True
        with mock.patch.object(asyncio, "gather", new=mock.AsyncMock(side_effect=exit_exception)):
            with pytest.raises(exit_exception):
                await rest_client._request(route)

            rest_client.buckets.start.assert_not_called()

    @hikari_test_helpers.timeout()
    async def test__request_when__token_is_None(self, rest_client, exit_exception):
        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        mock_session = mock.AsyncMock(request=mock.AsyncMock(side_effect=exit_exception))
        rest_client.buckets.is_started = True
        rest_client._token = None
        rest_client._acquire_client_session = mock.Mock(return_value=mock_session)
        with mock.patch.object(asyncio, "gather", new=mock.AsyncMock()):
            with pytest.raises(exit_exception):
                await rest_client._request(route)

            _, kwargs = mock_session.request.call_args_list[0]
            assert constants.AUTHORIZATION_HEADER not in kwargs["headers"]

    @hikari_test_helpers.timeout()
    async def test__request_when__token_is_not_None(self, rest_client, exit_exception):
        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        mock_session = mock.AsyncMock(request=mock.AsyncMock(side_effect=exit_exception))
        rest_client.buckets.is_started = True
        rest_client._token = "token"
        rest_client._acquire_client_session = mock.Mock(return_value=mock_session)
        with mock.patch.object(asyncio, "gather", new=mock.AsyncMock()):
            with pytest.raises(exit_exception):
                await rest_client._request(route)

            _, kwargs = mock_session.request.call_args_list[0]
            assert kwargs["headers"][constants.AUTHORIZATION_HEADER] == "token"

    @hikari_test_helpers.timeout()
    async def test__request_when_no_auth_passed(self, rest_client, exit_exception):
        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        mock_session = mock.AsyncMock(request=mock.AsyncMock(side_effect=exit_exception))
        rest_client.buckets.is_started = True
        rest_client._token = "token"
        rest_client._acquire_client_session = mock.Mock(return_value=mock_session)
        with mock.patch.object(asyncio, "gather", new=mock.AsyncMock()):
            with pytest.raises(exit_exception):
                await rest_client._request(route, no_auth=True)

            _, kwargs = mock_session.request.call_args_list[0]
            assert constants.AUTHORIZATION_HEADER not in kwargs["headers"]

    @hikari_test_helpers.timeout()
    async def test__request_when_response_is_NO_CONTENT(self, rest_client):
        class StubResponse:
            status = http.HTTPStatus.NO_CONTENT
            reason = "cause why not"

        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        mock_session = mock.AsyncMock(request=mock.AsyncMock(return_value=StubResponse()))
        rest_client.buckets.is_started = True
        rest_client._debug = False
        rest_client._parse_ratelimits = mock.AsyncMock()
        rest_client._acquire_client_session = mock.Mock(return_value=mock_session)
        with mock.patch.object(asyncio, "gather", new=mock.AsyncMock()):
            assert (await rest_client._request(route)) is None

    @hikari_test_helpers.timeout()
    async def test__request_when_response_is_APPLICATION_JSON(self, rest_client):
        class StubResponse:
            status = http.HTTPStatus.OK
            content_type = constants.APPLICATION_JSON
            reason = "cause why not"
            raw_headers = ((b"HEADER", b"value"), (b"HEADER", b"value"))

            async def read(self):
                return '{"something": null}'

        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        mock_session = mock.AsyncMock(request=mock.AsyncMock(return_value=StubResponse()))
        rest_client.buckets.is_started = True
        rest_client._debug = True
        rest_client._parse_ratelimits = mock.AsyncMock()
        rest_client._acquire_client_session = mock.Mock(return_value=mock_session)
        with mock.patch.object(asyncio, "gather", new=mock.AsyncMock()):
            assert (await rest_client._request(route)) == {"something": None}

    @hikari_test_helpers.timeout()
    async def test__request_when_response_is_not_JSON(self, rest_client):
        class StubResponse:
            status = http.HTTPStatus.IM_USED
            content_type = "text/html"
            reason = "cause why not"
            real_url = "https://some.url"

        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        mock_session = mock.AsyncMock(request=mock.AsyncMock(return_value=StubResponse()))
        rest_client.buckets.is_started = True
        rest_client._debug = False
        rest_client._parse_ratelimits = mock.AsyncMock()
        rest_client._acquire_client_session = mock.Mock(return_value=mock_session)
        with mock.patch.object(asyncio, "gather", new=mock.AsyncMock()):
            with pytest.raises(errors.HTTPError):
                await rest_client._request(route)

    @hikari_test_helpers.timeout()
    async def test__request_when_response_is_not_between_200_and_300(self, rest_client, exit_exception):
        class StubResponse:
            status = http.HTTPStatus.NOT_IMPLEMENTED
            content_type = "text/html"
            reason = "cause why not"

        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        mock_session = mock.AsyncMock(request=mock.AsyncMock(return_value=StubResponse()))
        rest_client.buckets.is_started = True
        rest_client._debug = False
        rest_client._parse_ratelimits = mock.AsyncMock()
        rest_client._handle_error_response = mock.AsyncMock(side_effect=exit_exception)
        rest_client._acquire_client_session = mock.Mock(return_value=mock_session)
        with mock.patch.object(asyncio, "gather", new=mock.AsyncMock()):
            with pytest.raises(exit_exception):
                await rest_client._request(route)

    @hikari_test_helpers.timeout()
    async def test__request_when_response__RetryRequest_gets_handled(self, rest_client, exit_exception):
        class StubResponse:
            status = http.HTTPStatus.USE_PROXY
            content_type = "text/html"
            reason = "cause why not"

        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        mock_session = mock.AsyncMock(request=mock.AsyncMock(side_effect=[rest_client._RetryRequest, exit_exception]))
        rest_client.buckets.is_started = True
        rest_client._debug = False
        rest_client._acquire_client_session = mock.Mock(return_value=mock_session)
        with mock.patch.object(asyncio, "gather", new=mock.AsyncMock()):
            with pytest.raises(exit_exception):
                await rest_client._request(route)

    async def test__handle_error_response(self, rest_client, exit_exception):
        mock_response = mock.Mock()
        with mock.patch.object(net, "generate_error_response", return_value=exit_exception) as generate_error_response:
            with pytest.raises(exit_exception):
                await rest_client._handle_error_response(mock_response)

            generate_error_response.assert_called_once_with(mock_response)

    async def test__parse_ratelimits_when_not_ratelimited(self, rest_client):
        class StubResponse:
            status = http.HTTPStatus.OK
            headers = {constants.DATE_HEADER: "Thu, 02 Jul 2020 20:55:08 GMT"}

            json = mock.AsyncMock()

        response = StubResponse()
        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        await rest_client._parse_ratelimits(route, response)
        response.json.assert_not_called()

    async def test__parse_ratelimits_when_ratelimited(self, rest_client, exit_exception):
        class StubResponse:
            status = http.HTTPStatus.TOO_MANY_REQUESTS
            content_type = constants.APPLICATION_JSON
            headers = {constants.DATE_HEADER: "Thu, 02 Jul 2020 20:55:08 GMT"}

            async def json(self):
                raise exit_exception

        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        with pytest.raises(exit_exception):
            await rest_client._parse_ratelimits(route, StubResponse())

    async def test__parse_ratelimits_when_unexpected_content_type(self, rest_client):
        class StubResponse:
            status = http.HTTPStatus.TOO_MANY_REQUESTS
            content_type = "text/html"
            headers = {constants.DATE_HEADER: "Thu, 02 Jul 2020 20:55:08 GMT"}
            real_url = "https://some.url"

            async def read(self):
                return "this is not json :)"

        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        with pytest.raises(errors.HTTPErrorResponse):
            await rest_client._parse_ratelimits(route, StubResponse())

    async def test__parse_ratelimits_when_global_ratelimit(self, rest_client):
        class StubResponse:
            status = http.HTTPStatus.TOO_MANY_REQUESTS
            content_type = constants.APPLICATION_JSON
            headers = {constants.DATE_HEADER: "Thu, 02 Jul 2020 20:55:08 GMT"}
            real_url = "https://some.url"

            async def json(self):
                return {"global": True, "retry_after": "2"}

        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        with pytest.raises(rest_client._RetryRequest):
            await rest_client._parse_ratelimits(route, StubResponse())

        rest_client.global_rate_limit.throttle.assert_called_once_with(0.002)

    async def test__parse_ratelimits_when_remaining_under_or_equal_to_0(self, rest_client):
        class StubResponse:
            status = http.HTTPStatus.TOO_MANY_REQUESTS
            content_type = constants.APPLICATION_JSON
            headers = {
                constants.DATE_HEADER: "Thu, 02 Jul 2020 20:55:08 GMT",
                constants.X_RATELIMIT_REMAINING_HEADER: "0",
            }
            real_url = "https://some.url"

            async def json(self):
                return {"retry_after": "2"}

        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        with pytest.raises(errors.RateLimited):
            await rest_client._parse_ratelimits(route, StubResponse())

    async def test__parse_ratelimits_when_retry_after_is_close_enough(self, rest_client):
        class StubResponse:
            status = http.HTTPStatus.TOO_MANY_REQUESTS
            content_type = constants.APPLICATION_JSON
            headers = {
                constants.DATE_HEADER: "Thu, 02 Jul 2020 20:55:08 GMT",
                constants.X_RATELIMIT_RESET_AFTER_HEADER: "0.002",
            }
            real_url = "https://some.url"

            async def json(self):
                return {"retry_after": "2"}

        route = routes.Route("GET", "/something/{channel}/somewhere").compile(channel=123)
        with pytest.raises(rest_client._RetryRequest):
            await rest_client._parse_ratelimits(route, StubResponse())

    async def test_close_when__client_session_is_None(self, rest_client):
        rest_client._client_session = None
        rest_client.buckets = mock.Mock()

        await rest_client.close()

        rest_client.buckets.close.assert_called_once()

    async def test_close_when__client_session_is_not_None(self, rest_client):
        rest_client._client_session = mock.AsyncMock()
        rest_client.buckets = mock.Mock()

        await rest_client.close()

        rest_client._client_session.close.assert_called_once()
        rest_client.buckets.close.assert_called_once()

    async def test_fetch_channel(self, rest_client, stub_model):
        expected_route = routes.GET_CHANNEL.compile(channel=123)
        mock_object = mock.Mock()
        rest_client._app.entity_factory.deserialize_channel = mock.Mock(return_value=mock_object)
        rest_client._request = mock.AsyncMock(return_value={"payload"})

        assert await rest_client.fetch_channel(stub_model(123)) == mock_object
        rest_client._request.assert_called_once_with(expected_route)
        rest_client._app.entity_factory.deserialize_channel.assert_called_once_with({"payload"})

    async def test_edit_channel(self, rest_client, stub_model):
        expected_route = routes.PATCH_CHANNEL.compile(channel=123)
        mock_object = mock.Mock()
        rest_client._app.entity_factory.deserialize_channel = mock.Mock(return_value=mock_object)
        rest_client._request = mock.AsyncMock(return_value={"payload"})
        rest_client._app.entity_factory.serialize_permission_overwrite = mock.Mock(
            return_value={"type": "member", "allow": 1024, "deny": 8192}
        )
        expected_json = {
            "name": "new name",
            "position": 1,
            "topic": "new topic",
            "nsfw": True,
            "bitrate": 10,
            "user_limit": 100,
            "rate_limit_per_user": 30,
            "parent_id": "1234",
            "permission_overwrites": [{"type": "member", "allow": 1024, "deny": 8192}],
        }

        assert (
            await rest_client.edit_channel(
                stub_model(123),
                name="new name",
                position=1,
                topic="new topic",
                nsfw=True,
                bitrate=10,
                user_limit=100,
                rate_limit_per_user=30,
                permission_overwrites=[
                    channels.PermissionOverwrite(
                        type=channels.PermissionOverwriteType.MEMBER,
                        allow=permissions.Permission.VIEW_CHANNEL,
                        deny=permissions.Permission.MANAGE_MESSAGES,
                    )
                ],
                parent_category=stub_model(1234),
                reason="some reason :)",
            )
            == mock_object
        )
        rest_client._request.assert_called_once_with(expected_route, json=expected_json, reason="some reason :)")
        rest_client._app.entity_factory.deserialize_channel.assert_called_once_with({"payload"})

    async def test_edit_channel_without_optionals(self, rest_client, stub_model):
        expected_route = routes.PATCH_CHANNEL.compile(channel=123)
        mock_object = mock.Mock()
        rest_client._app.entity_factory.deserialize_channel = mock.Mock(return_value=mock_object)
        rest_client._request = mock.AsyncMock(return_value={"payload"})

        assert await rest_client.edit_channel(stub_model(123)) == mock_object
        rest_client._request.assert_called_once_with(expected_route, json={}, reason=undefined.UNDEFINED)
        rest_client._app.entity_factory.deserialize_channel.assert_called_once_with({"payload"})

    async def test_delete_channel(self, rest_client, stub_model):
        expected_route = routes.DELETE_CHANNEL.compile(channel=123)
        rest_client._request = mock.AsyncMock()

        await rest_client.delete_channel(stub_model(123))
        rest_client._request.assert_called_once_with(expected_route)
