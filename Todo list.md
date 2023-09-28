[X] Decide on overall flow - API gw vs step functions vs other
[ ] ~Figure out how to send initial message via pinpoint~
	[ ] Pricing - charged per message but sub-pennies
    [ ] Figure out return message
[ ] Slack messaging
    [X] Initial send
	[X] Account for receiving requests and follow-up
	[X] Need to have user_response_recorder respond to the hook, and post in channel
      [X] Prevent it from going into an infinite loop by checking user ID
	  [ ] Consider reaction to message, instead of posting an explicit message reply
	  [ ] No dupe handling currently, need to prevent multiple db messages / slack responses
	[X] Test (stub) menu_suggester with chat history
[ ] Lambda construction
	[X] Call OpenAI
	[X] Call Dall-E, chaining off prompts
	[ ] ~Send MMS to user~
[ ] Follow up requests
    [ ] If someone posts after the initial meal is generated, user_response_recorder should run; AND, a new meal should be scheduled in 5 min
	  [ ] Look at turning this into a slack button
[X] Shared code
	[X] Docker approach: is there a way to make a docker image / layer?
	[X] SAM approach: create a Lambda layer. <- This seems better, can use poetry venv for local testing (poetry dep export actually takes care of it without a lambda layer)
	  [X] How would local import be possible when debugging? PYPATH?
	  [X] Maybe easier to export some kind of shared lib. Ask GPT
	  [X] Use `poetry add --editable for the shared directory`
[ ] Paprika - incorporate known/favorite recipes
	[ ] Follow-up step in LLM flow - "compare the suggestions to this list of pre-defined recipes. Replace any meals with the pre-existing recipes if they are similar enough"