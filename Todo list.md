[X] Decide on overall flow - API gw vs step functions vs other
[ ] ~Figure out how to send initial message via pinpoint~
	[ ] Pricing - charged per message but sub-pennies
    [ ] Figure out return message
[ ] Slack messaging
    [X] Initial send
	[X] Account for receiving requests and follow-up
	[X] Need to have user_response_recorder respond to the hook, and post in channel
      [X] Prevent it from going into an infinite loop by checking user ID
	  [X] Tie API to SQS queue (which triggers Lambda) in order to consistently meet Slack's SLA
	  [ ] Consider reaction to message, instead of posting an explicit message reply
	  [X] No dupe handling currently, need to prevent multiple db messages / slack responses
	[X] Test (stub) menu_suggester with chat history
[ ] Scheduling/usability
	[ ] Change "start of week" to be Friday instead of Saturday
		[ ] Migrate Dynamo rows
		[ ] Change ScheduleV2 to fire on Friday (different time?)
		[ ] Update shared util tests
[ ] CodeBuild pipeline
	[ ] Figure out how to integrate with all/multiple branches
	[ ] Run tests
	[ ] Pre-built image so it doesn't need to install python stuff
[ ] Message spam reduction
	[X] Allow messaging to different channels rather than a single hard-coded
		[X] User response recorder
		[X] Menu suggester
		[X] Upcoming reminder
			[X] Modify cron schedule so it includes event details
		[X] Migrate to use a hash key of date + channel
		[X] Regression test
	[ ] Post multiple pictures at once, not individually
	[ ] Try to reduce recap/preamble into one message
[ ] Recommendation history
	[ ] Fix edge case where recipes are duped / continue to grow continuously, as they are carried week to week. Need to de-dupe, and filter down to only the last 3 week timestamps
	[ ] Debug why bibimbap keeps being suggested despite history >:(
	[ ] Use presence/frequency penalty to further reduce chance of common recipes. NLTK might be useful for avoiding penalizing prepositions
[ ] Lambda construction
	[X] Call OpenAI
	[X] Call Dall-E, chaining off prompts
	[ ] ~Send MMS to user~
[ ] Follow up requests
    [ ] If someone posts after the initial meal is generated, user_response_recorder should run; AND, a new meal should be scheduled in 5 min (currently lower priority since you can type "conjure" to trigger at any time)
	  [ ] Look at turning this into a slack button
[X] Shared code
	[X] Docker approach: is there a way to make a docker image / layer?
	[X] SAM approach: create a Lambda layer. <- This seems better, can use poetry venv for local testing (poetry dep export actually takes care of it without a lambda layer)
	  [X] How would local import be possible when debugging? PYPATH?
	  [X] Maybe easier to export some kind of shared lib. Ask GPT
	  [X] Use `poetry add --editable for the shared directory`
[X] Paprika - incorporate known/favorite recipes
	[X] Follow-up step in LLM flow - "compare the suggestions to this list of pre-defined recipes. Replace any meals with the pre-existing recipes if they are similar enough"