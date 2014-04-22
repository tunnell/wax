__author__ = 'tunnell'

from cliff.command import Command
from wax.core.Configuration import DEFAULT_FILENAME

class ProcessCommand(Command):


    def get_description(self):
        return self.__doc__

    def get_parser(self, prog_name):
        parser = super(ProcessCommand, self).get_parser(prog_name)

        parser.add_argument("--filename", help="filenmae",
                            type=str,
                            default='cito_file.pklz')


        return parser

    def take_action(self, parsed_args):
        self.log = logging.getLogger(self.__class__.__name__)

        self.log.debug('Command line arguments: %s', str(parsed_args))

        while True:
            try:
                p = ProcessTask(parsed_args.dataset, parsed_args.hostname)
            except Exception as e:
                self.log.exception(e)
                self.log.fatal("Exception resulted in fatal error; quiting.")
                raise

            if parsed_args.chunks != -1:
                p.delete_collection_when_done = False

            if not p.input.initialized:
                self.log.warning("No dataset available to process; waiting one second.")
                time.sleep(1)
            else:
                p.process_dataset(chunk_size=parsed_args.chunksize,
                                  chunks=parsed_args.chunks,
                                  padding=parsed_args.padding)

            # If only a single dataset was specified, break
            if parsed_args.dataset is not None or parsed_args.chunks != -1:
                break
