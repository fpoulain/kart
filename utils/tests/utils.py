import pytest

from django.test import Client
from django.urls import reverse
from rest_framework_jwt.settings import api_settings

from django.contrib.auth.models import User


def first(items):
    return items[0]


def obtain_jwt_token(user):
    c = Client()
    url = reverse('obtain-jwt-token')

    response = c.post(url, {'username': user.username, 'password': 'p4ssw0rd'})
    assert response.status_code == 200
    assert 'token' in response.json()

    return response.json()


def validate_jwt_token(token, user):
    jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
    infos = jwt_decode_handler(token)
    return infos and 'user_id' in infos and User.objects.filter(pk=infos['user_id']).exists()


class HelpTestForModelRessource:
    """
    Help to test interfaces to ModelResource
    """
    fixtures = []
    methods_behavior = {
        method: 200
        for method in ['list', 'get', 'patch', 'put', 'post', 'delete']
    }
    mutate_fields = []

    _user_roles = [None, 'user', 'jwt']

    def setup(self):
        self.base_url = "/v1/{}".format(self.model._meta.resource_name)

    def setup_fixtures(self, request):
        for fixture_name in self.fixtures:
            setattr(self, fixture_name, request.getfixturevalue(fixture_name))

    def target_uri(self):
        return getattr(self.target(), self.model._meta.detail_uri_name)

    def thats_all_folk(self, method, response):
        if method in self.methods_behavior:
            assert response.status_code == self.methods_behavior[method]

        return method not in self.methods_behavior or self.methods_behavior[method] != 200

    def prepare_request(self, client, user_role, data=None):
        if user_role == 'user':
            client.force_login(self.requestor())

        kwargs = {'content_type': 'application/json'}
        if data is not None:
            kwargs['data'] = data

        if user_role == 'jwt':
            jwt = obtain_jwt_token(self.requestor())
            kwargs['HTTP_AUTHORIZATION'] = 'Bearer {}'.format(jwt['token'])

        return kwargs

    @pytest.mark.parametrize('user_role', _user_roles)
    def test_list(self, client, user_role, request):
        self.setup_fixtures(request)

        kwargs = self.prepare_request(client, user_role)
        response = client.get(self.base_url, **kwargs)

        if self.thats_all_folk('list', response):
            return

        answer = response.json()

        assert "meta" in answer
        assert "objects" in answer
        assert len(answer["objects"]) == self.expected_list_size

        for ressource in answer["objects"]:
            for field in self.expected_fields:
                assert field in ressource

    @pytest.mark.parametrize('user_role', _user_roles)
    def test_get(self, client, user_role, request):
        self.setup_fixtures(request)

        kwargs = self.prepare_request(client, user_role)
        response = client.get('{}/{}'.format(self.base_url, self.target_uri()), **kwargs)

        if self.thats_all_folk('get', response):
            return

        answer = response.json()

        for field in self.expected_fields:
            assert field in answer

    @pytest.mark.parametrize('user_role', _user_roles)
    def test_post(self, client, user_role, request):
        self.setup_fixtures(request)

        data = {f: getattr(self.target(), f) for f in self.mutate_fields}
        kwargs = self.prepare_request(client, user_role, data)
        response = client.post('{}/{}'.format(self.base_url, self.target_uri()), **kwargs)

        if self.thats_all_folk('post', response):
            return

    @pytest.mark.parametrize('user_role', _user_roles)
    def test_put(self, client, user_role, request):
        self.setup_fixtures(request)

        data = {f: getattr(self.target(), f) for f in self.mutate_fields}
        kwargs = self.prepare_request(client, user_role, data)
        response = client.put('{}/{}'.format(self.base_url, self.target_uri()), **kwargs)

        if self.thats_all_folk('put', response):
            return

    @pytest.mark.parametrize('user_role', _user_roles)
    def test_patch(self, client, user_role, request):
        self.setup_fixtures(request)

        data = {f: getattr(self.target(), f) for f in self.mutate_fields}
        kwargs = self.prepare_request(client, user_role, data)
        response = client.patch('{}/{}'.format(self.base_url, self.target_uri()), **kwargs)

        if self.thats_all_folk('patch', response):
            return

    @pytest.mark.parametrize('user_role', _user_roles)
    def test_delete(self, client, user_role, request):
        self.setup_fixtures(request)

        kwargs = self.prepare_request(client, user_role)
        response = client.delete('{}/{}'.format(self.base_url, self.target_uri()), **kwargs)

        if self.thats_all_folk('delete', response):
            return


class HelpTestForReadOnlyModelRessource(HelpTestForModelRessource):
    _user_roles = [None]

    methods_behavior = {
        'list': 200,
        'get': 200,
        'patch': 401,
        'put': 401,
        'post': 501,
        'delete': 401,
    }
