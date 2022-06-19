"""
gets ports

"""

import argparse
import concurrent.futures
import csv
import logging
import os
import socket

logging.getLogger().setLevel(logging.INFO)

PORTS_RANGE = range(1024)


def tcp_connect(ip, port):
    """
    checks tcp connect

    :param ip: string containing ip address
    :param port: int, port number
    :return: bool, whether port is listen

    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1.)

    try:
        logging.debug('checking %s:%s', ip, port)
        sock.connect((ip, port))
        logging.info('%s:%s is listen', ip, port)

        return True
    except socket.error:
        return False


def make_ports(ip):
    """
    makes list of port numbers

    :param ip: string containing ip address
    :return: string containing list of port numbers

    """
    ports = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(tcp_connect, ip, port): port for port in PORTS_RANGE
        }
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                ports.append(futures[future])

        return ':'.join(str(port) for port in ports)


def main():
    """
    gets ports

    """
    parser = argparse.ArgumentParser(
        description='gets ports',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('ip', type=str, help='string containing ip address or path to files with list of ip addresses')
    parser.add_argument('--ip_column', type=str, default='ip', help='column name containing ip addresses')
    args = parser.parse_args()

    if os.path.exists(args.ip):
        directory = os.path.dirname(args.ip)

        with open(args.ip) as inp:
            reader = csv.DictReader(inp)

            output = os.path.join(directory, 'output.csv')
            out_cols = list(reader.fieldnames) + ['ports']

            with open(output, 'w') as out:
                writer = csv.DictWriter(out, fieldnames=out_cols)
                writer.writeheader()

                for row in reader:
                    row.update(
                        {'ports': make_ports(row[args.ip_column])}
                    )
                    writer.writerow(row)

        logging.info('output file: %s', output)

    else:
        logging.info('ip: %s', args.ip)
        logging.info('ports: %s', make_ports(args.ip))


if __name__ == '__main__':
    main()
