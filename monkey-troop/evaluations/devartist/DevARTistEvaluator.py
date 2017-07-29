from argparse import ArgumentParser
from multiprocessing import Queue

from analysis.ResultAnalyzer import ResultAnalyzer
from evaluations.Task import Task
from evaluations.common import read_apps
from evaluations.trace_logging.TraceLoggingWorker import TraceLoggingWorker
from model.IEvaluator import IEvaluator


class DevARTistEvaluator(IEvaluator):
    # id used to choose this evaluator
    EVAL_ID = 'dev_artist'

    # subtask ids
    # subtask ids
    SUBTASK_DOWNLOAD_APP = 'download_app'
    SUBTASK_INSTALL_APP_1 = 'install_app_1'
    SUBTASK_TEST_UNINSTRUMENTED = 'test_app_uninstrumented'
    SUBTASK_INSTALL_APP_2 = 'install_app_2'
    SUBTASK_INSTRUMENT = 'instrument_app'
    SUBTASK_TEST_INSTRUMENTED = 'test_app_instrumented'
    SUBTASK_CLEANUP = 'cleanup'

    # subtask to interpretation map
    SUBTASKS_INTERPRETATION = {
        # detect whether eligible for testing
        SUBTASK_DOWNLOAD_APP: IEvaluator.ASSUMPTION,
        SUBTASK_INSTALL_APP_1: IEvaluator.ASSUMPTION,
        SUBTASK_TEST_UNINSTRUMENTED: IEvaluator.ASSUMPTION,
        SUBTASK_INSTALL_APP_2: IEvaluator.ASSUMPTION,
        # do the actual testing
        SUBTASK_INSTRUMENT: IEvaluator.REQUIRED,
        SUBTASK_TEST_INSTRUMENTED: IEvaluator.REQUIRED,
        # try to clean up
        SUBTASK_CLEANUP: IEvaluator.DONTCARE
    }

    # identifiers for arguments
    ARG_PKG_LIST = 'package_list'
    ARG_APK_FOLDER = 'apk_folder'
    ARG_REVERSE = 'reverse'

    # parcel
    SEPARATOR = '::'

    def init(self):
        parser = self.create_parser()
        args = parser.parse_args()

        if args.evaluation != DevARTistEvaluator.EVAL_ID:
            print('Error! Wrong evaluation provided. Expected "' + DevARTistEvaluator.EVAL_ID + '"')
            exit(-1)

        self.package_list = args.package_list
        self.apk_folder = args.apk_folder
        self.reverse = args.reverse


    def create_parser(self):
        parser = ArgumentParser()

        parser.add_argument('evaluation',
                            metavar='<EVALUATION>',
                            action='store',
                            help='The evaluation that will be invoked. Should be "' + DevARTistEvaluator.EVAL_ID + '"')

        parser.add_argument(DevARTistEvaluator.ARG_PKG_LIST,
                            metavar='<PACKAGE_LIST>',
                            action='store',
                            help='Package File which contains a categorized package list.')

        parser.add_argument(DevARTistEvaluator.ARG_APK_FOLDER,
                            metavar='<APK_FOLDER>',
                            action='store',
                            help='Folder where APKs should get stored, if the apk exists, nothing is '
                                 'downloaded')
        parser.add_argument('-r', '--reverse',
                            action='store_true',
                            help='Activating this flag leads to a reverse processing of the package list')
        return parser

    # TODO code shared between at least 2 evaluations: refactor!
    def create_task_queue(self, skip=0):

        app_dict, num_apps = read_apps(self.package_list)
        queue = Queue(num_apps)

        for app,categories in app_dict.items():
            if app in skip:
                print('Skipping already processed app ' + app)
                continue
            queue.put(Task(app, categories))
        return queue

    def create_device_worker(self, control_channel, queue, device_id, report_queue, process_args=(), process_kwargs={}):
        process_name = 'device_' + device_id
        return TraceLoggingWorker(name=process_name, args=process_args, kwargs=process_kwargs,
                             control_channel=control_channel, queue=queue, device_id=device_id, report_queue=report_queue,
                             apk_folder=self.apk_folder)


    def get_eval_id(self):
        return DevARTistEvaluator.EVAL_ID

    def get_subtask_ids_ordered(self):
        # the ordering matters
        return [DevARTistEvaluator.SUBTASK_DOWNLOAD_APP,
                DevARTistEvaluator.SUBTASK_INSTALL_APP_1,
                DevARTistEvaluator.SUBTASK_TEST_UNINSTRUMENTED,
                DevARTistEvaluator.SUBTASK_INSTALL_APP_2,
                DevARTistEvaluator.SUBTASK_INSTRUMENT,
                DevARTistEvaluator.SUBTASK_TEST_INSTRUMENTED,
                DevARTistEvaluator.SUBTASK_CLEANUP]

    def get_subtask_interpretation(self):
        return DevARTistEvaluator.SUBTASKS_INTERPRETATION

    # no specialized analyzer needed currently: return default one
    def get_analyzer(self, out_dir, fixed_fields_front, fixed_fields_back):
        # no specific analyzer required
        return ResultAnalyzer(out_dir, self, fixed_fields_front, fixed_fields_back)
