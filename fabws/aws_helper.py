import logging
from boto.ec2 import EC2Connection
import time
from boto.exception import EC2ResponseError

__author__ = 'gautam'


class AWSHelper:
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.ec2conn = EC2Connection(access_key, secret_key)

    def set_instance_names(self, instances, name):
        instance_ids = [instance.id for instance in instances]
        logging.info("Naming {} instances as {}".format(instances, name))
        self.ec2conn.create_tags(instance_ids, {"Name": name})

    def run_instances(self, ami_id, key_name, security_groups, name=None, count=1,
                      instance_type="t1.micro", placement="us-east-1d"):
        """
        Helper method with sane defaults for starting new ec2 instances
        :param ami_id:
        :param count:
        :param key_name:
        :param instance_type:
        :param security_groups:
        :param placement:
        :return: Reservation
        """
        logging.info("Starting {} instances of {}".format(count, ami_id))
        reservation = self.ec2conn.run_instances(ami_id, key_name=key_name, security_groups=security_groups,
                                                 instance_type=instance_type, placement=placement, min_count=count)

        if name:
            self.set_instance_names(reservation.instances, name)
        logging.info("Instances Launched reservation id {}".format(reservation.id))
        return reservation

    @staticmethod
    def wait_for_instance_state(instance, state="running", tick=10,
                                timeout=1800):
        """
        Wait for instance state to change
        :param instance: Instance object
        :param state: the state to wait for
        :param tick: time to wait before checking again
        :return: when instance state changes to the required value
        :raises: TimeOutError when timeout occurs
        """
        started_at = time.time()
        instance.update()
        while instance.state != state:
            logging.info("Instance {} {}, expecting {}, waiting {}s".format(instance.id, instance.state, state, tick))
            time.sleep(tick)
            instance.update()
            waiting_for = time.time() - started_at
            logging.info("Been waiting for {}s, timeout is {}".format(waiting_for, timeout))
            if instance.state != state and waiting_for >= timeout:
                raise Exception("Timeout Error")

    def terminate_instances(self, instances=None, instance_ids=None):
        """
        Terminate instances, call with either a list of instance objects or a list of instance_ids

        :param instances: a list of instance objects
        :param instance_ids: A list of strings of the Instance IDs to terminate
        :return: None
        :raises: ValueError when both instances and instance_ids are None or empty
        """
        if instances:
            for instance in instances:
                print "Terminating instance {}".format(instance.id)
                instance.terminate()
        elif instance_ids:
            print "Terminating instances {}".format(instance_ids)
            try:
                self.ec2conn.terminate_instances(instance_ids=instance_ids)
            except EC2ResponseError as e:
                logging.exception("Unable to terminate instances, trying one at a time")
                for instance_id in instance_ids:
                    try:
                        self.ec2conn.terminate_instances(instance_ids=[instance_id])
                    except EC2ResponseError:
                        logging.error("Unable to delete instance {}".format(instance_id))
                        continue
        else:
            raise ValueError("Both instances and instance_ids cannot be None")