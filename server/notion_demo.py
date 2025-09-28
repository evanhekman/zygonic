from action import Action

# # create an action template
# create_template = ActionTemplate(
#     "notion",
#     "create",
#     "NOTION",
# )

# create a specific action
create = Action(
    integration="notion",
    action="create",
    args={
        "page_name": "Philosophical Ramblings 1.0",
        "page_content": "If doors have handles, why do windows have latches?",
    },
    webhook="NOTION",
)

# these are functionally the same
# create_template.call_with_args(
#     {
#         "page_name": "Philosophical Ramblings 2.0",
#         "page_content": "If doors have handles, why do windows have latches?",
#     }
# )
create.call()

# serialize
json = create.serialize()

# this is also how we interpret model output
create_2 = Action(model_dump=json)

for property, value in create.__dict__.items():
    assert(create_2.__dict__.get(property) == value)

