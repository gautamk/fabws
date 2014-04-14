from fabric.context_managers import cd, settings
from fabric.operations import sudo, run

__author__ = 'gautam'


class FabricHelper:
    def __init__(self, host, user_name, ssh_key_path):
        self.host = host
        self.fabric_settings = settings(
            connection_attempts=10,  # Number of times to retry fabric connection
            timeout=20,
            key_filename=ssh_key_path,
            user=user_name,
            host_string=host
        )

    def execute(self, script, working_directory=None, super_user=False):
        method = sudo if super_user else run
        with self.fabric_settings:
            if working_directory:
                with cd(working_directory):
                    result = method(script)
            else:
                result = method(script)
        return result