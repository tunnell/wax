__author__ = 'tunnell'

from cito.core.main import CitoContinousCommand

__author__ = 'tunnell'

from cito.EventBuilder import Tasks, Output


class ProcessToMongoCommand(CitoContinousCommand):
    """Process time blocks and save to MongoDB
    """

    def get_tasks(self):
        tasks = [Tasks.ProcessTimeBlockTask(Output.MongoDBOutput())]
        return tasks
