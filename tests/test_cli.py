import sys
from mock import patch
from rancher_gen.cli import main
from rancher_gen.handler import RancherConnector
from StringIO import StringIO


class TestCLI:

    def test_fails_with_missing_host(self):
        mock_args = ['/tmp/rancher-gen/bin/rancher-gen',
                     '--port', '8080',
                     '--access-key', '1234567890',
                     '--secret-k', '1234567890abcd',
                     '--project-id', '1a5',
                     '/tmp/in.j2', '/tmp/out.txt']
        with patch.object(sys, 'argv', mock_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()

        assert mock_stdout.getvalue() == 'error: Missing host parameter\n'

    def test_fails_with_missing_access_key(self):
        mock_args = ['/tmp/rancher-gen/bin/rancher-gen',
                     '--host', '192.168.0.15',
                     '--port', '8080',
                     '--secret-k', '1234567890abcd',
                     '--project-id', '1a5',
                     '/tmp/in.j2', '/tmp/out.txt']
        with patch.object(sys, 'argv', mock_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()

        assert mock_stdout.getvalue() ==\
            'error: Missing Rancher access key parameter\n'

    def test_fails_with_missing_secret_key(self):
        mock_args = ['/tmp/rancher-gen/bin/rancher-gen',
                     '--host', '192.168.0.15',
                     '--port', '8080',
                     '--access-key', '1234567890',
                     '--project-id', '1a5',
                     '/tmp/in.j2', '/tmp/out.txt']
        with patch.object(sys, 'argv', mock_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()

        assert mock_stdout.getvalue() ==\
            'error: Missing Rancher secret key parameter\n'

    def test_fails_with_missing_project_id(self):
        mock_args = ['/tmp/rancher-gen/bin/rancher-gen',
                     '--host', '192.168.0.15',
                     '--port', '8080',
                     '--access-key', '1234567890',
                     '--secret-k', '1234567890abcd',
                     '/tmp/in.j2', '/tmp/out.txt']
        with patch.object(sys, 'argv', mock_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()

        assert mock_stdout.getvalue() ==\
            'error: Missing Rancher project id parameter\n'

    def test_succeeds_with_required_parameters(self):
        mock_args = ['/tmp/rancher-gen/bin/rancher-gen',
                     '--host', '192.168.0.15',
                     '--port', '8080',
                     '--access-key', '1234567890',
                     '--secret-k', '1234567890abcd',
                     '--project-id', '1a5',
                     '/tmp/in.j2', '/tmp/out.txt']
        with patch.object(sys, 'argv', mock_args):
            with patch.object(RancherConnector, '__call__') as mock:
                main()

        assert mock.called
