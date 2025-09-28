from db import TaskManager

tm = TaskManager()
tm.drop_tasks_table()  # This drops the table
tm.create_tasks_table()  # This recreates it with correct schema
tm.close()