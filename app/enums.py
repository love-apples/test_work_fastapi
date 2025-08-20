from enum import Enum


class TaskStatus(Enum):
    CREATED = 'created'
    ON_WORK = 'on_work'
    DONE = 'done'