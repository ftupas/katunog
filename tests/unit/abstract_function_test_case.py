from abc import ABC
import unittest
from unittest.mock import MagicMock, patch


class AbstractFunctionTestCase(unittest.IsolatedAsyncioTestCase, ABC):
    post = MagicMock()

    def setUp(self):
        super().setUp()
        self.patch_post = patch("src.katunog.api.requests.post", return_value=self.post)
        self.mock_post = self.patch_post.start()

    def tearDown(self):
        self.patch_post.stop()
        self.post.reset_mock()
        super().tearDown()
