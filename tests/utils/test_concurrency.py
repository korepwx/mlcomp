import time
import unittest

from mlcomp.utils import BackgroundWorker
from tests.helper import TestCase


class BackgroundWorkerTestCase(TestCase):

    def test_NoError(self):
        # test no error
        counter = [0]

        def action():
            counter[0] += 1

        worker = BackgroundWorker(action, sleep_seconds=0.5)
        worker.start()
        time.sleep(1)

        start_time = time.time()
        worker.stop()
        stop_time = time.time()

        # test the stop operation is immediate
        self.assertLess(stop_time - start_time, 0.1)
        # test the counter has been increased
        self.assertGreaterEqual(counter[0], 1)

    def test_NotStopOnError(self):
        def action():
            counter[0] += 1
            raise ValueError()

        counter = [0]
        worker = BackgroundWorker(
            action, sleep_seconds=0.1, stop_on_error=False)
        worker.start()
        time.sleep(0.5)
        worker.stop()
        self.assertGreaterEqual(counter[0], 4)

    def test_StopOnError(self):
        def action():
            counter[0] += 1
            raise ValueError()

        counter = [0]
        worker = BackgroundWorker(
            action, sleep_seconds=0.1, stop_on_error=True)
        worker.start()
        time.sleep(0.5)
        worker.stop()
        self.assertEqual(counter[0], 1)

    def test_WorkerNameInLog(self):
        def action():
            counter[0] += 1
            raise ValueError()

        counter = [0]
        worker = BackgroundWorker(
            action, sleep_seconds=0.1, name='worker_name',
            stop_on_error=True,
        )
        worker.start()
        time.sleep(0.5)
        worker.stop()
        self.assertEqual(counter[0], 1)


if __name__ == '__main__':
    unittest.main()
