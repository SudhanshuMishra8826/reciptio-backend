"""
Test Management Commands
"""

from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2OperationalError
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandsTests(SimpleTestCase):

    def test_wait_for_db_ready(self, mock_handle):

        """Test waiting for db when db is available"""
        mock_handle.return_value = True

        call_command('wait_for_db')

        mock_handle.assert_called_once_with(databases=['default'])

    @patch('time.sleep', return_value=True)
    def test_wait_for_db_delay(self, patched_sleep, mock_handle):

        """Test waiting for db"""
        mock_handle.side_effect = [Psycopg2OperationalError] * 2 + \
            [OperationalError] * 3 + [True]
        call_command('wait_for_db')

        self.assertEqual(mock_handle.call_count, 6)
