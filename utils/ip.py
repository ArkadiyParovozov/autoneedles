"""
gets ip from url

"""

import argparse
import csv
import logging
import os
import random
import socket
import urllib.parse

import requests

logging.getLogger().setLevel(logging.INFO)


def make_domain_ip(url):
    """
    gets dict with domain and ip address from url string

    :param url: string containing url
    :return: dict with domain and ip address
    """
    netloc, ip = None, None
    try:
        netloc = urllib.parse.urlparse(url).netloc
        if netloc:
            ip = socket.gethostbyname(netloc)
    except socket.gaierror:
        logging.error('url %s is not known', url)

    info = {
        'domain': netloc,
        'ip': ip,
    }

    return info


def make_user_agent():
    """
    makes random user agent

    :return: user agent
    """
    user_agent = random.choice([
        'Mozilla/5.0 (X11; Linux ppc64le; rv:75.0) Gecko/20100101 Firefox/75.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/75.0',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:75.0) Gecko/20100101 Firefox/75.0',
    ])

    return user_agent


def make_country(ip):
    """
    makes country from ipapi.co

    :param ip: string with ip address
    :return: string with country name
    """
    url = f'https://ipapi.co/{ip}/json/'
    response = requests.get(url, headers={'User-Agent': make_user_agent()})
    country = response.json()['country_name']

    return country


def main():
    """
    gets ip from url

    """
    parser = argparse.ArgumentParser(
        description='get ip from url',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('url', type=str, help='string containing url or path to files with list of of urls')
    parser.add_argument('--url_column', type=str, default='website', help='column name containing url')
    parser.add_argument('--country', type=bool, default=False, help='adds ip address location')
    args = parser.parse_args()

    if os.path.exists(args.url):
        directory = os.path.dirname(args.url)

        with open(args.url) as inp:
            reader = csv.DictReader(inp)

            output = os.path.join(directory, 'output.csv')
            out_cols = list(reader.fieldnames) + ['domain', 'ip']
            if args.country:
                out_cols.append('country')

            with open(output, 'w') as out:
                writer = csv.DictWriter(out, fieldnames=out_cols)
                writer.writeheader()

                for row in reader:
                    info = make_domain_ip(row[args.url_column])
                    row.update(info)
                    if args.country and row['ip']:
                        row['country'] = make_country(row['ip'])
                    writer.writerow(row)

        logging.info('output file: %s', output)

    else:
        logging.info('url: %s', args.url)

        info = make_domain_ip(args.url)
        logging.info('domain: %s, ip: %s', *info.values())

        if args.country and info['ip']:
            country = make_country(info['ip'])
            logging.info('country: %s', country)


if __name__ == '__main__':
    main()
