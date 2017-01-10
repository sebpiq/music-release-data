# https://api.discogs.com/database/search?year=1992&type=master&token=wfNtFSIXxwIUpkEkDfwratkQjpcytnltTRXEHLjG
# 
import re
import os
import json

import common

token = 'wfNtFSIXxwIUpkEkDfwratkQjpcytnltTRXEHLjG'


def iter_releases(year):
    url = 'https://api.discogs.com/database/search?year=%s&type=master&token=%s' % (year, token)

    actual_result_count = 0
    expected_result_count = None
    while True:
        result = common.safe_get(url, { 'user-agent': '%s-%s' % ('sebpiq', token) })
        if expected_result_count is None: expected_result_count = result['pagination']['items']
        if len(result['results']) == 0: break

        for r in result['results']:
            yield r
            actual_result_count += 1

        url = result['pagination']['urls'].get('next', None)
        if url is None: break

    assert(expected_result_count == actual_result_count)


def _parse_duration(duration):
    matched = re.match('^(\d+)\:(\d+)$', duration)
    if matched:
        minutes = int(matched.group(1))
        seconds = int(matched.group(2))
        return minutes * 60 + seconds

    matched = re.match('^(\d+)\.(\d+)$', duration)
    if matched:
        minutes = int(matched.group(1))
        seconds = int(matched.group(2))
        return minutes * 60 + seconds

    raise ValueError('%s - %s' % (duration, type(duration)))


if __name__ == '__main__':
    year_int = 1900
    while year_int <= 2014:
        year = str(year_int)

        json_path = os.path.join(common.data_folder, '%s-discogs.json' % year)
        seen_releases = { 
            'total_tracks': 0, 
            'total_seconds': 0,
            'total_releases': 0,
            'tracks_unknown_duration': 0,
            'releases_ids': [], # This list is used for not counting same releases twice 
        }
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as fd:
                seen_releases = json.loads(fd.read())

        def _backup_results():
            with open(json_path, 'w') as fd:
                fd.write(json.dumps(seen_releases))

        try:
            for i, current_release in enumerate(iter_releases(year)):

                if current_release['id'] in seen_releases['releases_ids']: continue
                seen_releases['releases_ids'].append(current_release['id'])

                # Filter out compilations
                if 'Compilation' in current_release['format'] or 'compilation' in current_release['format']:
                    continue

                # Get the detailed info about the release
                current_release = common.safe_get(
                    current_release['resource_url'], { 'user-agent': '%s-%s' % ('sebpiq', token) })

                # Filter out "Various" artist
                if len(current_release['artists']) == 1 and current_release['artists'][0]['id'] == 194:
                    continue

                seen_releases['total_releases'] += 1
                seen_releases['total_tracks'] += len(current_release['tracklist'])
                for track in current_release['tracklist']:
                    if track.get('duration', None):
                        try:
                            seen_releases['total_seconds'] += _parse_duration(track['duration'])
                        except ValueError as err:
                            print(err)
                            seen_releases['tracks_unknown_duration'] += 1  
                    else: seen_releases['tracks_unknown_duration'] += 1

                common.print_progress('year %s, %s seen, total tracks %s                ' 
                    % (year, len(seen_releases['releases_ids']), seen_releases['total_tracks']))

                # backup results
                if i % 20 == 0: _backup_results()
        
        # If AssertionError do the same year again
        except AssertionError as err:
            print(err)

        # Otherwise move on to next year
        else:
            year_int += 1

        _backup_results()
