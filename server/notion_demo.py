from action import Action

# # create an action template
# create_page_template = ActionTemplate(
#     "notion",
#     "create_page",
#     "NOTION",
# )

# create a specific action
create_page = Action(
    integration="notion",
    action="create_page",
    args={
        "page_name": "Philosophical Ramblings 1.0",
        "page_content": "If doors have handles, why do windows have latches?",
    },
    webhook="NOTION",
)

# these are functionally the same
# create_page_template.call_with_args(
#     {
#         "page_name": "Philosophical Ramblings 2.0",
#         "page_content": "If doors have handles, why do windows have latches?",
#     }
# )
create_page.call()

# serialize
json = create_page.serialize()

# this is also how we interpret model output
create_page_2 = Action(model_dump=json)

for property, value in create_page.__dict__.items():
    assert(create_page_2.__dict__.get(property) == value)

