# -*- coding: utf-8 -*-

from __future__ import absolute_import

from ..job import DelayableRecordset
from ..exception import BaseQueueJobError
from contextlib import contextmanager

import mock


@contextmanager
def mock_job_delay_to_direct(raise_job_errors=False):

    def patched_getattr(self, name):
        if name in self.recordset:
            raise AttributeError(
                'only methods can be delayed (%s called on %s)' %
                (name, self.recordset)
            )
        recordset_method = getattr(self.recordset, name)
        if not getattr(recordset_method, 'delayable', None):
            raise AttributeError(
                'method %s on %s is not allowed to be delayed, '
                'it should be decorated with openerp.addons.queue_job.job.job' %
                (name, self.recordset)
            )

        def delay(*args, **kwargs):
            try:
                return recordset_method(*args, **kwargs)
            except BaseQueueJobError:
                if raise_job_errors:
                    raise

        return delay

    with mock.patch.object(DelayableRecordset, '__getattr__', new=patched_getattr) as patched:
        yield patched
