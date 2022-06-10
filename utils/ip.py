"""
get ip from url

"""

import argparse
import csv
import logging
import os
import socket
import urllib.parse

logging.getLogger().setLevel(logging.INFO)


def make_domain_ip(url):
    """
    gets tuple with domain and ip address from url string

    :param url: string containing url
    :return: domain and ip address
    """
    netloc, ip = None, None
    try:
        netloc = urllib.parse.urlparse(url).netloc
        if netloc:
            ip = socket.gethostbyname(netloc)
    except socket.gaierror:
        logging.error('url %s is not known', url)

    return netloc, ip


def main():
    """
    get ip from url

    """
    parser = argparse.ArgumentParser(
        description='get ip from url',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('url', type=str, help='string containing url or path to files with list of of urls')
    args = parser.parse_args()

    if os.path.exists(args.url):
        directory = os.path.dirname(args.url)

        with open(args.url) as inp:
            reader = csv.reader(inp)

            output = os.path.join(directory, 'output.csv')
            with open(output, 'w') as out:
                writer = csv.writer(out)
                writer.writerow(['domain', 'ip'])

                for url in reader:
                    row = make_domain_ip(url[0])

                    if row:
                        writer.writerow(row)

        logging.info('output file: %s', output)

    else:
        domain, ip = make_domain_ip(args.url)
        logging.info('domain: %s, ip: %s', domain, ip)


if __name__ == '__main__':
    main()
