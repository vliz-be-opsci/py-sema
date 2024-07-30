#! /usr/bin/env python
from unittest import TestCase
from unittest.mock import Mock, patch

from sema.bench.dispatcher import TaskDispatcher
from sema.bench.handler import PyshaclHandler, PysubytHandler
from sema.bench.task import Task


class TestTaskDispatcher(TestCase):
    @patch("sema.bench.handler.PysubytHandler.handle")
    @patch("sema.bench.handler.PyshaclHandler.handle")
    def test_dispatch(self, patch1, patch2):
        patch1 = Mock()  # noqa F841
        patch2 = Mock()  # noqa F841
        task1 = Task(".", ".", ".", "my_pysubyt_task", "pysubyt", {})
        task2 = Task(".", ".", ".", "my_pyshacl_task", "pyshacl", {})
        self.assertEqual(TaskDispatcher().dispatch(task1), PysubytHandler)
        self.assertEqual(TaskDispatcher().dispatch(task2), PyshaclHandler)
