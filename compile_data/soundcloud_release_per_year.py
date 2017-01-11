import urllib
import os
import json

import settings
import common

def _make_url(date_start, date_end):
    query = {}
    query['client_id'] = settings.soundcloud_client_id
    query['created_at[from]'] = date_start 
    query['created_at[to]'] = date_end
    query['limit'] = 51
    return ( 'https://api.soundcloud.com/tracks.json?%s' 
        % '&'.join(['%s=%s' % (k, v) for k, v in query.items()]) )


for year in range(2006, 2017):
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
            'last_date': None,
            'last_ids': []
        }

    while True:
        # Building url, starting from last date if there is one
        if seen_releases['last_date']:
            search_url = _make_url('%s-01-01 00:00:00' % year, seen_releases['last_date'])
        else:
            search_url = _make_url('%s-01-01 00:00:00' % year, '%s-12-31 23:59:59' % year)
        results = common.safe_get(search_url)

        # Removing duplicates
        if seen_releases['last_ids'] and results:
            cleaned = []
            for track_dict in results:
                if not track_dict['id'] in seen_releases['last_ids']:
                    cleaned.append(track_dict)
            results = cleaned
        if not results: break

        # Counting tracks
        for track_dict in results:
            seen_releases['total_duration'] += track_dict['duration'] / 1000
            seen_releases['total_tracks'] += 1
            seen_releases['last_ids'].append(track_dict['id'])

        seen_releases['last_date'] = results[-1]['created_at']
        if len(seen_releases['last_ids']) > 2000:
            seen_releases['last_ids'] = seen_releases['last_ids'][2000:]
        _backup_results()

        common.print_progress('year %s | duration %s \t\t\t | tracks %s                ' 
            % (year, seen_releases['total_duration'], seen_releases['total_tracks']))
