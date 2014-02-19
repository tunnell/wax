__author__ = 'tunnell'

from cito.core.main import CitoContinousCommand

__author__ = 'tunnell'

from cito.EventBuilder import Tasks, Output


class ProcessToMongoCommand(CitoContinousCommand):
    """Process time blocks and save to MongoDB
    """

    def get_tasks(self, parsed_args=None):
        hostname = '127.0.0.1'
        if parsed_args:
            hostname = parsed_args.hostname
        tasks = [Tasks.ProcessTimeBlockTask(Output.MongoDBOutput(hostname))]

        return tasks
