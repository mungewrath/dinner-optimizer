import datetime
from pytest_mock import MockFixture
import pytest

from dinner_optimizer_shared import time_utils


def test_most_recent_saturday__returns_yesterday_on_sunday(mocker: MockFixture):
    mocked_datetime = mocker.patch(
        "dinner_optimizer_shared.time_utils.datetime.date",
    )
    oct_8_2023 = datetime.datetime(2023, 10, 8, 0, 0, 0)
    mocked_datetime.today.return_value = oct_8_2023

    assert time_utils.most_recent_saturday() == "10-07-2023"


def test_most_recent_saturday__returns_today_on_saturday(mocker: MockFixture):
    mocked_datetime = mocker.patch(
        "dinner_optimizer_shared.time_utils.datetime.date",
    )
    oct_7_2023 = datetime.datetime(2023, 10, 7, 0, 0, 0)
    mocked_datetime.today.return_value = oct_7_2023

    assert time_utils.most_recent_saturday() == "10-07-2023"


def test_nth_most_recent_saturday__returns_today_on_saturday_for_n_1(
    mocker: MockFixture,
):
    mocked_datetime = mocker.patch(
        "dinner_optimizer_shared.time_utils.datetime.date",
    )
    oct_7_2023 = datetime.datetime(2023, 10, 7, 0, 0, 0)
    mocked_datetime.today.return_value = oct_7_2023

    assert time_utils.nth_most_recent_saturday(1) == "10-07-2023"


def test_nth_most_recent_saturday__returns_last_week_on_saturday_for_n_2(
    mocker: MockFixture,
):
    mocked_datetime = mocker.patch(
        "dinner_optimizer_shared.time_utils.datetime.date",
    )
    oct_7_2023 = datetime.datetime(2023, 10, 7, 0, 0, 0)
    mocked_datetime.today.return_value = oct_7_2023

    assert time_utils.nth_most_recent_saturday(2) == "09-30-2023"


def test_nth_most_recent_saturday__when_sunday__returns_last_week_on_saturday_for_n_2(
    mocker: MockFixture,
):
    mocked_datetime = mocker.patch(
        "dinner_optimizer_shared.time_utils.datetime.date",
    )
    oct_8_2023 = datetime.datetime(2023, 10, 8, 0, 0, 0)
    mocked_datetime.today.return_value = oct_8_2023

    assert time_utils.nth_most_recent_saturday(2) == "09-30-2023"


def test_nth_most_recent_saturday__throws_error_for_n_0():
    with pytest.raises(Exception):
        time_utils.nth_most_recent_saturday(0)
