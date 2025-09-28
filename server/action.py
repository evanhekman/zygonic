"""
Class representing the actions/integrations available. Needs to be cleanly serializable to JSON and understandable to an LLM.
Example:

{
    "integration": "notion",
    "action": "create_page",
    "args": {
        "page_name": "Name of New Page",
        "page_content": "Content for New Page",
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

import webhook
import json

class Action:
    def __init__(self = None, integration: str = None, action: str = None, args: dict = None, webhook: str = None, model_dump: str = None):
        if model_dump:
            assert(type(model_dump) == str)
            model_dump = json.loads(model_dump)
            self.integration = model_dump["integration"]
            self.action = model_dump["action"]
            self.args = model_dump["args"]
            self.webhook = model_dump["webhook"]
        else:
            assert(type(integration) == str)
            assert(type(action) == str)
            assert(type(args) == dict)
            assert(type(webhook) == str)
            self.integration = integration
            self.action = action
            self.args = args
            self.webhook = webhook

    def serialize(self) -> str:
        """
        Convert Action -> JSON string.
        """
        data = {
            "integration": self.integration,
            "action": self.action,
            "args": self.args,
            "webhook": self.webhook
        }
        return json.dumps(data, indent=2)
    
    def deserialize(cls, json_str: str) -> 'Action':
        """
        Convert JSON string -> Action.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")
        
        # Validate required keys
        required_keys = {"integration", "action", "args", "webhook"}
        if not all(key in data for key in required_keys):
            missing_keys = required_keys - set(data.keys())
            raise ValueError(f"Missing required keys: {missing_keys}")
        
        return cls(
            integration=data["integration"],
            action=data["action"],
            args=data["args"],
            webhook=data["webhook"]
        )

    def call(self):
        """
        Call the action webhook.
        """
        webhook.webhook(self.integration, self.action, self.args, self.webhook)

    def call_with_args(self, args: dict):
        """
        Call with specific arguments
        """
        assert(not self.__dict__.get("args"))
        webhook.webhook(self.integration, self.action, args, self.webhook)


    def __str__(self):
        return f"{self.integration}.{self.action} ({self.webhook})\nArgs: {self.args}"

class ActionTemplate(Action):
    """
    Action class for when you want to configure the action without providing args.
    """
    def __init__(self = None, integration: str = None, action: str = None, webhook: str = None, model_dump: str = None):
        if model_dump:
            assert(type(model_dump) == str)
            model_dump = json.loads(model_dump)
            self.integration = model_dump["integration"]
            self.action = model_dump["action"]
            self.webhook = model_dump["webhook"]
        else:
            assert(type(integration) == str)
            assert(type(action) == str)
            assert(type(webhook) == str)
            self.integration = integration
            self.action = action
            self.webhook = webhook

    def call(self):
        raise NotImplementedError
    