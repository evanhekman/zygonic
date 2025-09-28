import requests
import logging
import json
import webhook
from action import Action
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# --- Main execution block ---
if __name__ == "__main__":

    if len(sys.argv) > 1:
        print(f"Script name: {sys.argv[0]}")
        print("Arguments provided:")
        for i, arg in enumerate(sys.argv[1:]):
            print(f"  Argument {i+1}: {arg}")
        arg = sys.argv[1]
    else:
        print("No arguments provided.")
        exit(1)

    if arg == "notion":
        url = "NOTION"

        # create a post
        test = Action(integration=arg, 
                        action="create",
                        args={
                            "page_name": "An Essay on Longtermism",
                            "page_content": "The vast majority of human beings who will ever live have not yet been born. \n\
                            This simple, yet profound, observation is the foundation of longtermism, an ethical framework \
                            that suggests our primary moral obligation is to ensure the long and flourishing future of humanity. "
                        },
                        webhook=url)
        result1 = test.call()
        print(json.dumps(result1, indent=2))

        # search for a string of words in all posts
        test = Action(integration=arg, 
                        action="search",
                        args={
                            "query": "essay"
                        },
                        webhook=url)
        print(json.dumps(test.call(), indent=2))

        # add onto a post (here we use a previous result but can search then do this?)
        test = Action(integration=arg, 
                        action="modify",
                        args={
                            "page_url": result1["url"],
                            "new_content": "Extra stuff!"
                        },
                        webhook=url)
        print(json.dumps(test.call(), indent=2))
    
    elif arg == "email":
        url = "EMAIL"

        # make a draft email
        test = Action(integration=arg, 
                        action="draft",
                        args={
                            "subject": "An Essay on Longtermism",
                            "message": " ougugughgh my epic emaillllllllllllll business!!!"
                        },
                        webhook=url)
        print(json.dumps(test.call(), indent=2))

        # search for emails, should return a lot but returns none
        testS = Action(integration=arg, 
                        action="search",
                        args={
                            "query": "terms"
                        },
                        webhook=url)
        print(json.dumps(testS.call(), indent=2))

        # reply to an email, maybe search for an email then have gemini read it then reply to them?
        test = Action(integration=arg, 
                        action="search",
                        args={
                            "query": "from: notifications@discord.com"
                        },
                        webhook=url)
        searchinfo = test.call()

        test = Action(integration=arg, 
                        action="reply",
                        args={
                            "subject": "An Essay on Longtermism",
                            "message": " ougugughgh my epic emaillllllllllllll business!!!",
                            "to": searchinfo[""]
                        },
                        webhook=url)
        print(json.dumps(test.call(), indent=2))

    elif arg == "gcal":
        url = "GCAL"

        # make an event
        test = Action(integration=arg, 
                        action="create",
                        args={
                            "message": "heres my first event wow",
                        },
                        webhook=url)
        print(json.dumps(test.call(), indent=2))

        # search for gcal events in next week, should return a lot but returns none
        testS = Action(integration=arg, 
                        action="search",
                        args={
                        },
                        webhook=url)
        print(json.dumps(testS.call(), indent=2))

    elif arg == "sheets":
        url = "SHEETS"

        # make a sheet
        test = Action(integration=arg, 
                        action="create",
                        args={
                            "title": "my health plan",
                            "sheet1name": "week 1",
                            "sheet2name": "week 2",
                            "sheet3name": "week 3",
                        },
                        webhook=url)
        print(json.dumps(test.call(), indent=2))

    elif arg == "vscode":
        url = "VSCODE"

        # make a draft email
        test = Action(integration=arg, 
                        action="draft",
                        args={
                            "subject": "An Essay on Longtermism",
                            "message": " ougugughgh my epic emaillllllllllllll business!!!",
                        },
                        webhook=url)
        print(json.dumps(test.call(), indent=2))

        # search for emails, should return a lot but returns none
        testS = Action(integration=arg, 
                        action="search",
                        args={
                            "query": "terms"
                        },
                        webhook=url)
        print(json.dumps(testS.call(), indent=2))

        # reply to an email, maybe search for an email then have gemini read it then reply to them?
        test = Action(integration=arg, 
                        action="search",
                        args={
                            "query": "from: notifications@discord.com"
                        },
                        webhook=url)
        searchinfo = test.call()

        test = Action(integration=arg, 
                        action="reply",
                        args={
                            "subject": "An Essay on Longtermism",
                            "message": " ougugughgh my epic emaillllllllllllll business!!!",
                            "to": searchinfo[""]
                        },
                        webhook=url)
        print(json.dumps(test.call(), indent=2))