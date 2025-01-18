from pytest_mock import MockFixture
import pytest

from upcoming_reminder import app
from dinner_optimizer_shared import interaction


def test_retrieve_past_week_recommendations__keeps_latest_message_of_every_week(
    mocker: MockFixture,
):
    mock_persistence = mocker.patch("upcoming_reminder.app.persistence")
    mock_persistence.retrieve_interactions_for_week.return_value = [
        interaction.Interaction(
            role="assistant",
            time="02-19-2024 21:00:33",
            text="First turn",
            timestamp="1703970033.7480774",
        ),
        interaction.Interaction(
            role="assistant",
            time="02-20-2024 21:00:33",
            text="Second turn",
            timestamp="1704970033.7480774",
        ),
    ]

    recs = app.retrieve_past_week_recommendations("mockChannel")

    assert len(recs) == 3
    assert recs[0].text == "Second turn"
    assert recs[1].text == "Second turn"
    assert recs[2].text == "Second turn"
