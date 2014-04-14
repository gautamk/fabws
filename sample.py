__author__ = 'gautam'

from fabws.aws_helper import AWSHelper
from fabws.fabric_helper import FabricHelper
import logging

logging.getLogger().setLevel(logging.INFO)

ACCESS_KEY = ""
SECRET_KEY = ""

aws_helper = AWSHelper(ACCESS_KEY, SECRET_KEY)

reservation = aws_helper.run_instances("ami-acfsc22", "key_name1", "security-group-1", "Name of the instance")
instance = reservation.instances[0]
AWSHelper.wait_for_instance_state(instance)  # wait for the instance to startup
instance_host = instance.public_dns_name
fabric_helper = FabricHelper(instance_host, "ubuntu", "~/.ssh/keypath")

fabric_helper.execute("apt-get update", super_user=True)
fabric_helper.execute("python main.py", working_directory="/home/ubuntu")

aws_helper.terminate_instances([instance])




