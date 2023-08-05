# Design notes

## Dynamo
- Partition Key: Week that it runs (this should be unique)
  - Date format MM-DD-YYYY
- Sort Key: Time
  - This would make it easy to retrieve multiple records chronologically
  - Does it even need this level of complexity? Shove it all in one message?

```json
{
    "Id": {
        "S": "07-22-2023"
    },
    "Interactions": [
        {
            "M": {
                "role": { "S": "assistant" },
                "time": { "S": "07-22-2023 08:00:00" },
                "text": { "S": "It's time to meal plan for the week! Do you have any special requests? I'll follow up at 3pm with suggestions, so let me know before then."}
            },
            "M": {
                "role": { "S": "user" },
                "time": { "S": "07-22-2023 08:09:00" },
                "text": { "S": "Try to make some meals using pork since it's on sale. Also avoid using the oven since the forecast is hot"}
            },
            "M": {
                "role": { "S": "assistant" },
                "time": { "S": "07-22-2023 08:09:15" },
                "text": { "S": "Got it!"}
            },
            "M": {
                "role": { "S": "assistant" },
                "time": { "S": "07-22-2023 15:06:02" },
                "text": { "S": "Here is your meal list for the week: <menu>"}
            },
            "M": {
                "role": { "S": "assistant" },
                "time": { "S": "07-22-2023 15:06:03" },
                "text": { "S": "Let me know if there are any customizations you want after looking, and I can re-think the list."}
            },
            "M": {
                "role": { "S": "user" },
                "time": { "S": "07-22-2023 15:30:10" },
                "text": { "S": "Replace the taco and quinoa meals"}
            },
            "M": {
                "role": { "S": "assistant" },
                "time": { "S": "07-22-2023 15:36:14" },
                "text": { "S": "Got it - Here is your new meal list for the week: <menu>"}
            },
        }
    ]
}
```