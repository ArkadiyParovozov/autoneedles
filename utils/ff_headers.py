"""
makes dict with headers from mozilla firefox developer tools

"""

import argparse
import json
from pprint import pprint

FF_HEADERS = {
    '': {
        'headers': [
        ]
    }
}


def main():
    """
    makes dict with headers from mozilla firefox developer tools

    """
    parser = argparse.ArgumentParser(
        description='makes dict with headers from mozilla firefox developer tools',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--path', type=str, default=None, help='path to file containing headers')

    args = parser.parse_args()

    if args.path:
        with open(args.path) as f:
            ff_headers = json.load(f)
    else:
        ff_headers = FF_HEADERS

    headers = {
        h['name']: h['value'] for h in [x for x in ff_headers.items()][0][1]['headers']
    }

    pprint(headers)


if __name__ == '__main__':
    main()
