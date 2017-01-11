import urllib
import os
import json

import common


for year in range(2000, 2017):
    print('starting year %s' % year)
    json_path = os.path.join(common.data_folder, '%s-soundcloud.json' % year)

    def _backup_results():
        with open(json_path, 'w') as fd:
            fd.write(json.dumps(seen_releases))

    if os.path.exists(json_path):
        with open(json_path, 'r') as fd:
            seen_releases = json.loads(fd.read())
    else:
        seen_releases = {
            'total_duration': 0,
            'total_tracks': 0,
            'next_href': None,
            'last_date': None
        }

    if not seen_releases['next_href']:
        query = {}
        query['client_id'] = ''
        query['created_at[from]'] = '%s-01-01 00:00:00' % year
        query['created_at[to]'] = '%s-12-31 23:59:59' % year
        query['linked_partitioning'] = 1
        seen_releases['next_href'] = ( 'https://api.soundcloud.com/tracks.json?%s' 
            % '&'.join(['%s=%s' % (k, v) for k, v in query.items()]) )

    while True:
        results = common.safe_get(seen_releases['next_href'])
        for track_dict in results['collection']:
            seen_releases['total_duration'] += track_dict['duration'] / 1000
            seen_releases['total_tracks'] += 1

        seen_releases['next_href'] = results.get('next_href', None)
        if results['collection']:
            seen_releases['last_date'] = results['collection'][-1]['created_at']
        _backup_results()

        if not results.get('next_href', None):
            break
        common.print_progress('year %s | duration %s \t\t\t | tracks %s                ' 
            % (year, seen_releases['total_duration'], seen_releases['total_tracks']))
