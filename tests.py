from vkinder_bot import VKinderBot
import pytest

test_bot = VKinderBot()

class TestVKinderBot:

    def setup(self):
        print("method setup")

    def teardown(self):
        print("method teardown")

    @pytest.mark.parametrize('id, result', [(1, False), (777, False), (64176696, True), (11852056, True), (201431131, True)])
    def test_database_check(self, id, result):
        assert test_bot.database_check(id) == result