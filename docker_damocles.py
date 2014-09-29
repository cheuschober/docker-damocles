#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Provides docker_damocles, a daemon for killing docker instances."""


# Python Standard Libs
import logging
import time

# Third-Party Libs
import docker
from daemon import runner


class Damocles:
    """Class for providing time-based Docker monitoring.

    This class is primarily used in a CI context like Jenkins where CI cannot
    reliably kill the docker process. This often occurs in scenarios such as
    infinite loops.

    Attributes:
        sleep_interval: Integer controlling the length of time between wakeups.
        logger: An instance of logging.Logger()
        log_handler: Handler for the logfile
        docker_client: An instance of docker.Client()
        docker_timeout: The number of seconds that may pass until this daemon
            kills the docker container.
    """

    default_daemon_log = '/dev/tty'
    default_pidfile = '/var/run/docker_damocles.pid'
    default_log = '/var/log/docker-damocles.log'

    def __init__(self, logger=None, docker_client=None, **kwargs):
        self.stdin_path = kwargs.get('stdin_path', '/dev/null')
        self.stdout_path = kwargs.get('stdout_path', self.default_daemon_log)
        self.stderr_path = kwargs.get('stderr_path', self.default_daemon_log)
        self.pidfile_path = kwargs.get('pidfile_path', self.default_pidfile)
        self.pidfile_timeout = kwargs.get('pidfile_timeout', 5)
   
        self.sleep_interval = kwargs.get('sleep_interval', 5)
        
        if not logger:
            log_name = kwargs.get('log_name', 'DockerDamoclesLog')
            log_path = kwargs.get('log_path', self.default_log)
            log_level = kwargs.get('log_level', logging.INFO)
            log_format = kwargs.get('log_format',
                                    '%(asctime)s:%(levelname)s:%(message)s')
            log_datefmt = kwargs.get('log_datefmt', '%Y-%m-%d %H:%M:%S')

            logger = logging.getLogger(log_name)
            logger.setLevel(log_level)
            formatter = logging.Formatter(log_format, log_datefmt)
            self.log_handler = logging.FileHandler(log_path)
            self.log_handler.setFormatter(formatter)
            logger.addHandler(self.log_handler)
        self.logger = logger

        if not docker_client:
            default_docker_sock = 'unix://var/run/docker.sock'
            try:
                docker_client = docker.Client(base_url=default_docker_sock)
            except:
                self.logger.exception('Failed to connect to docker.')

        self.docker_client = docker_client
        self.docker_timeout = 600
 

    def swing(self, containers):
        """Kills a list of containers.

        Args:
            containers (mixed, iterable): An iterable object of container ids.

        Returns:
            None

        Examples:
        
            >>> swordsman = Damocles()
            >>> swordsman.swing(['xxxxxxxxxx', 'yyyyyyyyyyy'])
        """
        fail_msg = 'Failed to kill container: {0}'
        complete_msg = 'Killed {0} of {1} containers.'
        i = 0
        for container in containers:
            try:
                self.logger.debug('Killing container: {0}'.format(container))
                self.docker_client.kill(container)
                self.logger.debug('Killed container: {0}'.format(container))
                i += 1
            except:
                self.logger.exception(fail_msg.format(container))

        if i == len(containers):
            self.logger.info(complete_msg.format(i, len(containers)))
        else:
            self.logger.error(complete_msg.format(i, len(containers)))


    def cull(self):
        """Collects a selection of Docker containers who have exceeded timeout.

        Args:
            None

        Returns:
            list: A list of Docker container Id's.

        Examples:

            >>> swordsman = Damocles()
            >>> swordsman.cull()
            ['xxxxxxxxxxxxx', 'yyyyyyyyyyyyy']
        """
        min_ts = time.time() - self.docker_timeout
        try:
            herd = [x['Id']
                    for x in self.docker_client.containers()
                    if x['Created'] < min_ts]
        except:
            self.logger.exception('Docker Err: unable to list containers.')
        return herd


    def run(self):
        """Hangs the Sword of Damocles over Docker's throne.
        
        Args:
            None

        Returns:
            None

        Examples:

            >>> swordsman = Damocles()
            >>> swordsman.hang()

        """
        found_msg = 'Found {0} containers over time limit: {1}'

        self.logger.info('Daemon started.')
        while True:
            herd = self.cull()
            self.logger.debug('Wakeup: Found {0} containers'.format(len(herd)))
            if herd:
                herd_len = len(herd)
                self.logger.info(found_msg.format(herd_len, herd))
                self.swing(herd)
            time.sleep(self.sleep_interval)

            
if __name__ == '__main__':
    damocles = Damocles()
    damocles.log_handler.close()  # can't have open log descriptors

    daemon_runner = runner.DaemonRunner(damocles)
    daemon_runner.do_action()
