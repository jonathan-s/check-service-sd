import argparse
import json
import sys
import time
import urllib2


def parse():
    parser = argparse.ArgumentParser(description='Fetches Service data from Server Density')
    parser.add_argument('--id', help='The service ID in Server Density')
    parser.add_argument('--token', help='The api token for Server Density')
    parser.add_argument('--slow', help='The response threshold you want to give a warning')
    parser.add_argument('--locations', help='The number locations that has to be affected to elicit an error or warning')
    parser.add_argument('--allowed-status', nargs='+', help='The status codes that are allowed')
    parser.add_argument('--time', help='Time in epoch (use $timet$)')
    args = parser.parse_args()
    return args


def status(no_locations, request, slow, status_codes):

    if not request.code == 200:
        return (2, 'Critical: Unable to reach Server Density')

    locations = json.loads(request.read())

    above_threshold = []
    status_deviations = []
    for location in locations:
        if location['time'] > slow:
            above_threshold.append(location)
        if not location['code'] in status_codes:
            status_deviations.append(location)

    if status_deviations > no_locations:
        return (2, 'Critical: {} locations has deviated from the following status codes {}'.format(
                len(status_deviations),
                ', '.join(status_codes)
            ))
    elif above_threshold > no_locations:
        return (1, 'Warning: {} locations has deviated from the accepted threshold: {}'.format(
                len(above_threshold),
                slow
            ))
    else:
        return (0, 'OK: Service status nominal')



if __name__ == '__main__':
    args = parse()
    url = 'https://api.serverdensity.io/service-monitor/last/{}/?token={}'.format(
            args.id,
            args.token)

    elapsed_time = int(time.time()) - int(args.time)
    if elapsed_time < 5 * 60:
        print('OK: Service status nominal')
        sys.exit(0)

    no_locations = int(getattr(args, 'locations', 3))
    slow = float(getattr(args, 'slow', 0.5))
    status_codes = [int(s) for s in getattr(args, 'allowed_status', [200])]

    request = urllib2.urlopen(url)
    exit_code, status_statement = status(no_locations, request, slow, status_codes)
    print(status_statement)
    sys.exit(exit_code)
