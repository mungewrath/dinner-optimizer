import datetime
from pytest_mock import MockFixture
import pytest

from dinner_optimizer_shared import time_utils


def test_most_recent_monday__returns_yesterday_on_tuesday(mocker: MockFixture):
    mocked_datetime = mocker.patch(
        "dinner_optimizer_shared.time_utils.datetime.date",
    )
    oct_3_2023 = datetime.datetime(2023, 10, 3, 0, 0, 0)
    mocked_datetime.today.return_value = oct_3_2023

    assert time_utils.most_recent_monday() == "10-02-2023"


def test_most_recent_saturdaytest_most_recent_monday__returns_today_on_monday(
    mocker: MockFixture,
):
    mocked_datetime = mocker.patch(
        "dinner_optimizer_shared.time_utils.datetime.date",
    )
    oct_2_2023 = datetime.datetime(2023, 10, 2, 0, 0, 0)
    mocked_datetime.today.return_value = oct_2_2023

    assert time_utils.most_recent_monday() == "10-02-2023"


def test_most_recent_monday__returns_six_days_ago_on_sunday(mocker: MockFixture):
    mocked_datetime = mocker.patch(
        "dinner_optimizer_shared.time_utils.datetime.date",
    )
    oct_8_2023 = datetime.datetime(2023, 10, 8, 0, 0, 0)
    mocked_datetime.today.return_value = oct_8_2023

    assert time_utils.most_recent_monday() == "10-02-2023"


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


def test_nth_most_recent_weekday__returns_today_on_saturday_for_n_1(
    mocker: MockFixture,
):
    mocked_datetime = mocker.patch(
        "dinner_optimizer_shared.time_utils.datetime.date",
    )
    oct_7_2023 = datetime.datetime(2023, 10, 7, 0, 0, 0)
    mocked_datetime.today.return_value = oct_7_2023

    assert time_utils.nth_most_recent_weekday(1, 5) == "10-07-2023"


def test_nth_most_recent_weekday__returns_last_week_on_saturday_for_n_2(
    mocker: MockFixture,
):
    mocked_datetime = mocker.patch(
        "dinner_optimizer_shared.time_utils.datetime.date",
    )
    oct_7_2023 = datetime.datetime(2023, 10, 7, 0, 0, 0)
    mocked_datetime.today.return_value = oct_7_2023

    assert time_utils.nth_most_recent_weekday(2, 5) == "09-30-2023"


def test_nth_most_recent_weekday__when_sunday__returns_last_week_on_saturday_for_n_2(
    mocker: MockFixture,
):
    mocked_datetime = mocker.patch(
        "dinner_optimizer_shared.time_utils.datetime.date",
    )
    oct_8_2023 = datetime.datetime(2023, 10, 8, 0, 0, 0)
    mocked_datetime.today.return_value = oct_8_2023

    assert time_utils.nth_most_recent_weekday(2, 5) == "09-30-2023"


def test_nth_most_recent_weekday__throws_error_for_n_0():
    with pytest.raises(Exception):
        time_utils.nth_most_recent_weekday(0, 5)
