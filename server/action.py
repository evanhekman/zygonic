"""
Class representing the actions/integrations available. Needs to be cleanly serializable to JSON and understandable to an LLM.
Example:

{
    "integration": "notion",
    "action": "create_page",
    "args": {
        page_name: "Name of New Page",
        page_content: "Content for New Page",
    },
    "webhook": "NOTION_WEBHOOK",
}

This contains the configuration info for to create a Notion Page using the appropriate webhook, called with the correct arguments.
The function to make the n8n call will be `notion.create_page` from the integrations/notion.py file.
This format is standardized across all calls. All "Action" instances must include the following keys:
- "integration" for the module
- "action" for the function
- "args" for the args to supply the function (can be empty dict)
- "webhook" for the webhook environment variable that starts the n8n workflow

This allows us to trigger the action with a simple
n8n.webhook(webhook, action, args)

"""

class Action:
    def __init__():
        ...

    def json():
        ...

    