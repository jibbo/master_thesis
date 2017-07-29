from os import path

from DeviceWorker import DeviceWorker
from utils.apkdownload.download import ApkDownloader
from utils.shellutils import adb_install, adb_shell, adb_uninstall


class DevARTistWorker(DeviceWorker):

    def __init__(self, group=None, target=None, name="DeviceProcess", args=(), kwargs={}, control_channel=None,
                 queue=None, report_queue=None, device_id=None,
                 apk_folder='.', artist_package = 'saarland.cispa.artist.artistgui', artist_activity = 'ArtistMainActivity'):
        super(DevARTistWorker, self).__init__(group, target, name, args, kwargs, control_channel, queue, report_queue,
                                              device_id, apk_folder, artist_package, artist_activity)

        self.downloader = ApkDownloader()

    def process(self, task):
        # local import to avoid circular dependency
        from evaluations.trace_logging.TraceLoggingEvaluator import TraceLoggingEvaluator

        app = task.package
        seed = self.generate_monkey_seed()
        app_path = self.generate_app_path(app)
        self.start_task(task)

        try:
            # download app
            self.start_subtask(TraceLoggingEvaluator.SUBTASK_DOWNLOAD_APP)
            self.downloader.download_if_not_exist(app, self.apk_folder)
            # TODO let the download method directly return whether it worked or not
            download_succ = path.exists(app_path)
            self.conclude_subtask(download_succ)
            if not download_succ:
                self.log('App not downloaded. Abort.')
                return

            # install app for the first time
            self.start_subtask(TraceLoggingEvaluator.SUBTASK_INSTALL_APP_1)
            (success2, out2) = adb_install(app_path, device=self.device_id)
            self.log(out2)
            self.conclude_subtask(success2, include_logcat=True)
            if not success2:
                return

            # test uninstrumented app. We are interested in whether apps might be broken already BEFORE we instrument
            self.start_subtask(TraceLoggingEvaluator.SUBTASK_TEST_UNINSTRUMENTED)
            success3 = self.monkey_test(app, seed)
            self.conclude_subtask(success3, include_logcat=True)
            if not success3:
                return

            # clean (re)installation of app
            self.start_subtask(TraceLoggingEvaluator.SUBTASK_INSTALL_APP_2)
            (success4, out4) = adb_install(app_path, device=self.device_id)
            self.log(out4)
            self.conclude_subtask(success4, include_logcat=True)
            if not success4:
                return

            # instrument app
            self.start_subtask(TraceLoggingEvaluator.SUBTASK_INSTRUMENT)
            success5 = self.instrument(app)
            self.conclude_subtask(success5, include_logcat=True)
            if not success5:
                return

            # test instrumented app again with the same seed
            self.start_subtask(TraceLoggingEvaluator.SUBTASK_TEST_INSTRUMENTED)
            success6 = self.monkey_test(app, seed)
            self.conclude_subtask(success6, include_logcat=True)

        # always cleanup no matter where we finish
        finally:
            self.cleanup(task)

    # best effort cleanup since we do not know what apps and data are still on the device
    def cleanup(self, task):

        from evaluations.trace_logging.TraceLoggingEvaluator import TraceLoggingEvaluator
        self.start_subtask(TraceLoggingEvaluator.SUBTASK_CLEANUP)

        app_package = task.package
        self.log('Clean up for task ' + app_package)

        artist_succ, artist_out = adb_shell('am force-stop ' + self.artist_package, device=self.device_id)
        self.log(('un' if not artist_succ else '') + 'successfully stopped ARTistGUI')
        self.log(artist_out)

        app_succ, app_out = adb_uninstall(app_package, device=self.device_id)
        self.log(('un' if not app_succ else '') + 'successfully deinstalled ' + app_package + ': ')
        self.log(app_out)

        # delete all result files
        del_succ, del_out = adb_shell('rm ' + self.instrumentation_result_path() + '*', device=self.device_id)
        self.log(('un' if not del_succ else '') + 'successfully removed result files: ')
        self.log(del_out)

        # TODO in order to reliably report whether cleaning up worked,
        # we need to find out what needs to be cleaned up and then check if it worked.
        # Either we remember it during the processing or simply probe whether an app is installed or a file is present
        self.conclude_subtask(True, include_logcat=True)