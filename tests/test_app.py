from unittest import TestCase
from unittest.mock import create_autospec, patch

import ovh
import requests

from ovh_db_backup.__main__ import App


class TestApp(TestCase):
    def setUp(self) -> None:
        self.client = create_autospec(ovh.Client, spec_set=True)
        self.service_name = "service"
        self.database_name = "database"
        self.app = App(
            client=self.client,
            service_name=self.service_name,
            database_name=self.database_name,
        )

    def test_timeout(self):
        def get_mock(url):
            if (
                url
                == f"/hosting/privateDatabase/{self.service_name}/database/{self.database_name}/dump"
            ):
                return [1, 2]

        self.client.get = get_mock
        self.app.max_retries = 1
        self.app.sleep_time = 0.001
        self.assertRaises(Exception, self.app.trigger_backup)

    def test_unavailable_url(self):
        self.client.get.side_effect = [
            [1, 2],
            [1, 2, 3],
            {
                "url": "https://my.url.com",
                "creationDate": "2023-06-16T15:47:32+02:00",
                "databaseName": "database",
                "id": 3,
                "deletionDate": "2023-07-17T15:46:41+02:00",
            },
        ]
        with patch("ovh_db_backup.__main__.requests") as mock_requests:
            response = create_autospec(requests.Response)
            response.status_code = 401
            mock_requests.head.return_value = response
            self.assertRaises(Exception, self.app.trigger_backup)

    def test_success(self):
        self.client.get.side_effect = [
            [1, 2],
            [1, 2, 3],
            {
                "url": "https://my.url.com",
                "creationDate": "2023-06-16T15:47:32+02:00",
                "databaseName": "database",
                "id": 3,
                "deletionDate": "2023-07-17T15:46:41+02:00",
            },
        ]
        with patch("ovh_db_backup.__main__.requests") as mock_requests:
            response = create_autospec(requests.Response)
            response.status_code = 200
            mock_requests.head.return_value = response
            self.app.trigger_backup()
