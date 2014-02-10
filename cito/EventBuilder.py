"""Plot waveform

Make a plot of the sum waveform for a time range.
"""

__author__ = 'tunnell'

from cito.CommandsBase import CitoContinousCommand
from cito.EventBuilder import Tasks, Output


class ProcessToMongoCommand(CitoContinousCommand):
    """Process time blocks and save to MongoDB
    """

    def get_tasks(self):
        tasks = [Tasks.ProcessTimeBlockTask(Output.MongoDBOutput())]
        return tasks
