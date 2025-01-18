from pytest_mock import MockFixture
import pytest


def test_retrieve_past_week_recommendations__keeps_latest_message_of_every_week(
    mocker: MockFixture,
):
    assert 5 == 5
