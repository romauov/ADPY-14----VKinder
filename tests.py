# from vkinder_bot import VKinderBot
import pytest
from dbutils import database_check


class TestVKinderBot:

    def setUp(self):
        # test_bot = VKinderBot()
        print("method setup")

    def tearDown(self):
        print("method teardown")

    @pytest.mark.parametrize('id, result', [(1, False), (777, False), (64176696, True), (11852056, True), (201431131, True)])
    def test_database_check(self, id, result):
        assert database_check(id) == result