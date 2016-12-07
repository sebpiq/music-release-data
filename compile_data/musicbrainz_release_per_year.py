#
# url samples: 
#
# http://musicbrainz.org/ws/2/release/?fmt=json&query=date:2000-*-*&limit=1&inc=recordings
# http://musicbrainz.org/ws/2/release-group/709fb7c5-f8ff-3d45-b52c-f264f763ebff?inc=releases&fmt=json
# http://musicbrainz.org/ws/2/release/b87a2075-8b3a-4f01-bf93-46ae171fe2ca?inc=recordings&fmt=json
import os
import sys
import json
import re
import datetime

import common


def get_release_count(year):
    url = 'http://musicbrainz.org/ws/2/release/?fmt=json&query=date:%s-*-*&limit=1' % year
    result = common.safe_get(url)
    return result['count']


def iter_releases(year):
    def _iter(date_query):
        release_limit = 200
        offset = 0
        release_count_actual = 0
        release_count_expected = None

        while True:
            url = ('http://musicbrainz.org/ws/2/release/?fmt=json&query=date:%s&limit=%s&offset=%s' 
                % (year, release_limit, offset))
            result = common.safe_get(url)

            if release_count_expected is None: 
                release_count_expected = result['count']
                print('%s releases for year query %s' % (release_count_expected, date_query))

            if len(result['releases']) == 0: break
            for release in result['releases']:
                release_count_actual += 1
                yield release

            offset += len(result['releases'])

        assert(release_count_actual == release_count_expected)

    for release in _iter('%s-*-*' % year): yield release
    for release in _iter('%s-*' % year): yield release
    for release in _iter('%s' % year): yield release


def get_release_group(rg_id):
    url = 'http://musicbrainz.org/ws/2/release-group/%s?inc=releases&fmt=json' % rg_id
    return common.safe_get(url)


def get_release(r_id):
    url = 'http://musicbrainz.org/ws/2/release/%s?inc=recordings&fmt=json' % r_id
    return common.safe_get(url)


def _parse_date(date_str):
    if (re.match('^\d{4}$', date_str)):
        return datetime.datetime.strptime(date_str, '%Y')
    elif (re.match('^\d{4}-\d{2}$', date_str)):
        return datetime.datetime.strptime(date_str, '%Y-%m')
    elif (re.match('^\d{4}-\d{2}-\d{2}$', date_str)):
        return datetime.datetime.strptime(date_str, '%Y-%m-%d')
    else:
        raise ValueError(date_str)


if __name__ == '__main__':
    year_int = 2012
    while year_int < 2015:
        
        year = str(year_int)
        year_datetime = _parse_date(year)

        json_path = os.path.join(common.data_folder, '%s.json' % year)
        seen_releases = { 
            'total_tracks': 0,
            'total_seconds': 0,
            'tracks_unknown_duration': 0,
            'releases_ids': [] 
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

                # Once in a while, back-up our progress
                if i % 20 == 0: _backup_results()

                # Get the corresponding release group, so we can get the first release in the group
                # (in case the release is just a re-issue or something ...)
                release_group_id = current_release['release-group']['id']
                release_group = get_release_group(release_group_id)

                # Parse all dates to Python datetime
                try:
                    release_group['first-release-date'] = _parse_date(release_group['first-release-date'])
                except ValueError as err:
                    print('release rejected : %s' % err)
                    continue

                for release_from_gp in release_group['releases'][:]:
                    try:
                        release_from_gp['date'] = _parse_date(release_from_gp.get('date', ''))
                    except ValueError as err:
                        print('invalid date "%s"' % release_from_gp.get('date', ''))
                        release_group['releases'].remove(release_from_gp)

                    # Add all releases to the seen releases, so we ignore them if they come up
                    seen_releases['releases_ids'].append(release_from_gp['id'])

                # We only want releases that are the first release of their group
                if release_group['first-release-date'] < year_datetime: continue

                # Otherwise, we pick the first release in the group and count its tracks
                else:
                    release_group['releases'].sort(key=lambda r: r['date'])
                    first_release_id = release_group['releases'][0]['id']
                    first_release = get_release(first_release_id)
                    
                    for media in first_release['media']: 
                        seen_releases['total_tracks'] += media['track-count']
                        if not 'tracks' in media:
                            print('ERR : %s doesnt contain "tracks"' % media)
                            continue 
                        for track in media['tracks']:
                            if track.get('length', None):
                                seen_releases['total_seconds'] += round(track['length'] / 1000.0)
                            else: seen_releases['tracks_unknown_duration'] += 1

                    common.print_progress('year %s, %s seen, total tracks %s                ' 
                        % (year, len(seen_releases['releases_ids']), seen_releases['total_tracks']))

        # If AssertionError we do again the same year
        except AssertionError as err:
            print(err)
            continue

        # Otherwise we go on to next year
        else:
            year_int += 1


        _backup_results()