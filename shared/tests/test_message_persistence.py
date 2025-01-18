import datetime
from pytest_mock import MockFixture
import pytest

from dinner_optimizer_shared import message_persistence


def test_retrieve_interactions_for_week__sorts_in_chronological_order(
    mocker: MockFixture,
):
    mock_boto3 = mocker.patch("dinner_optimizer_shared.message_persistence.boto3")
    mock_dynamodb = mock_boto3.client.return_value
    mock_dynamodb.get_item.return_value = {
        "Item": {
            "Week": {"S": "02-19-2024_C05JEBJHNQ4"},
            "Interactions": {
                "L": [
                    {
                        "M": {
                            "role": {"S": "assistant"},
                            "text": {
                                "S": "Here's your suggested menu for this week:\nKorean Turkey Lettuce Wraps - Savory and flavorful Korean-style turkey lettuce wraps, served with a tangy cucumber salad.\nBok Choy Stir-Fry with Lemongrass Tofu - A delicious and healthy stir-fry made with bok choy and marinated lemongrass tofu.\nRed Cabbage Slaw with Creamy Dressing - A refreshing and crunchy slaw made with red cabbage, carrots, and a creamy sour cream dressing.\nItalian Stuffed Zucchini - Zucchini stuffed with a mixture of ground turkey, tomatoes, and Italian herbs, topped with melted cheese.\n"
                            },
                            "time": {"S": "12-30-2023 21:00:33"},
                            "timestamp": {"S": "1703970033.7480774"},
                        }
                    },
                    {
                        "M": {
                            "role": {"S": "assistant"},
                            "text": {
                                "S": "Here's your suggested menu for this week:\nKorean Turkey Lettuce Wraps - Savory and flavorful Korean-style turkey lettuce wraps, served with a tangy cucumber salad.\nBok Choy Stir-Fry with Lemongrass Tofu - A delicious and healthy stir-fry made with bok choy and marinated lemongrass tofu.\nRed Cabbage Slaw with Creamy Dressing - A refreshing and crunchy slaw made with red cabbage, carrots, and a creamy sour cream dressing.\nItalian Stuffed Zucchini - Zucchini stuffed with a mixture of ground turkey, tomatoes, and Italian herbs, topped with melted cheese.\n"
                            },
                            "time": {"S": "12-30-2023 21:00:33"},
                            "timestamp": {"S": "1703970033.7480774"},
                        }
                    },
                    {
                        "M": {
                            "role": {"S": "assistant"},
                            "text": {
                                "S": "Here's your suggested menu for this week:\nKorean Turkey Lettuce Wraps - Savory and flavorful Korean-style turkey lettuce wraps, served with a tangy cucumber salad.\nBok Choy Stir-Fry with Lemongrass Tofu - A delicious and healthy stir-fry made with bok choy and marinated lemongrass tofu.\nRed Cabbage Slaw with Creamy Dressing - A refreshing and crunchy slaw made with red cabbage, carrots, and a creamy sour cream dressing.\nItalian Stuffed Zucchini - Zucchini stuffed with a mixture of ground turkey, tomatoes, and Italian herbs, topped with melted cheese.\n"
                            },
                            "time": {"S": "12-30-2023 21:00:33"},
                            "timestamp": {"S": "1703970033.7480774"},
                        }
                    },
                    {
                        "M": {
                            "role": {"S": "user"},
                            "text": {
                                "S": "foods we would like to use up:\n• shredded mozzarella\n• Tofu\n• Cherry tomatoes\nOne specific request this week, I have what feels like an ulcer. Appreciate food selections that will help minimize symptoms"
                            },
                            "time": {"S": "02-24-2024 17:23:16"},
                            "timestamp": {"S": "1708795395.325239"},
                        }
                    },
                    {
                        "M": {
                            "role": {"S": "assistant"},
                            "text": {
                                "S": "Here's your suggested menu for this week:\nMediterranean Tofu Skewers with Greek Salad - Grilled tofu skewers marinated in Mediterranean spices, served with a fresh Greek salad.\nCheesy Cherry Tomato Pasta - Pasta tossed with cherry tomatoes, garlic, and shredded mozzarella cheese for a simple and comforting meal.\nHealing Turmeric Tofu Stir-Fry - A soothing stir-fry with tofu, turmeric, ginger, and vegetables to help with ulcer symptoms.\nPortuguese Stuffed Bell Peppers - Bell peppers filled with a flavorful mixture of rice, beans, and Portuguese spices, topped with melted cheese.\n"
                            },
                            "time": {"S": "02-24-2024 21:00:31"},
                            "timestamp": {"S": "1708808431.0696373"},
                        }
                    },
                    {
                        "M": {
                            "role": {"S": "assistant"},
                            "text": {
                                "S": "Here's your suggested menu for this week:\nMozzarella Stuffed Tofu Meatballs - Tender tofu meatballs stuffed with gooey mozzarella cheese, served with a light marinara sauce.\nCherry Tomato and Basil Quinoa Salad - A refreshing quinoa salad with cherry tomatoes, fresh basil, and a tangy citrus dressing.\nTurmeric Ginger Carrot Soup - A soothing and anti-inflammatory soup made with turmeric, ginger, carrots, and coconut milk.\nHerb-Roasted Portobello Mushrooms - Large portobello mushrooms marinated in herbs and roasted to a tender, flavorful perfection.\n"
                            },
                            "time": {"S": "02-25-2024 02:08:35"},
                            "timestamp": {"S": "1708826915.3780475"},
                        }
                    },
                ]
            },
        }
    }

    messages = message_persistence.retrieve_interactions_for_week(
        "02-19-2024", "C05JEBJHNQ4"
    )
    assert len(messages) == 6
    assert messages[0].time == "12-30-2023 21:00:33"
    assert messages[1].time == "12-30-2023 21:00:33"
    assert messages[2].time == "12-30-2023 21:00:33"
    assert messages[3].time == "02-24-2024 17:23:16"
    assert messages[4].time == "02-24-2024 21:00:31"
    assert messages[5].time == "02-25-2024 02:08:35"


def test_retrieve_interactions_for_week__returns_empty_default_if_dynamo_had_no_entry(
    mocker: MockFixture,
):
    mock_boto3 = mocker.patch("dinner_optimizer_shared.message_persistence.boto3")
    mock_dynamodb = mock_boto3.client.return_value
    mock_dynamodb.get_item.return_value = {}

    messages = message_persistence.retrieve_interactions_for_week(
        "02-19-2024", "C05JEBJHNQ4"
    )

    assert len(messages) == 0
