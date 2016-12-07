import os
import json
import re

import common


class CompiledData(object):

    def __init__(self, regex):
        self.all_data = {'TOTAL': {}}
        self.regex = regex
        self.compile()

    def add_year_data(self, year, raw_data):
        duration_avg = raw_data['total_seconds'] / raw_data['total_tracks']
        duration_estimated = raw_data['total_seconds'] + raw_data['tracks_unknown_duration'] * duration_avg
        
        self.all_data[year] = {
            'duration_known': raw_data['total_seconds'],
            'duration_estimated': duration_estimated,
            'tracks_count': raw_data['total_tracks'],
            'tracks_unknown_duration_count': raw_data['tracks_unknown_duration'],
            'releases_count': len(set(raw_data['releases_ids']))
        }

    def compile(self):
        for filename in os.listdir(common.data_folder):
            matched = re.match(self.regex, filename)
            if matched:
                file_path = os.path.join(common.data_folder, filename)
                year = int(re.match(self.regex, filename).group(1))
                with open(file_path, 'r') as fd:
                    data = json.loads(fd.read())
                self.add_year_data(year, data)

        for year_data in self.all_data.values():
            for key, value in year_data.items():
                self.all_data['TOTAL'].setdefault(key, 0)
                self.all_data['TOTAL'][key] += value


if __name__ == '__main__':
    import sys
    import os
    discogs_data = CompiledData('^(\d{4})-discogs.json$')
    musicbrainz_data = CompiledData('^(\d{4}).json$')

    file_path = os.path.join(sys.argv[1], 'discogs.json')
    print('compiling discogs data under %s' % os.path.abspath(file_path))
    with open(file_path, 'w') as fd:
        fd.write(json.dumps(discogs_data.all_data, sort_keys=True, indent=4, separators=(',', ': ')))
    
    file_path = os.path.join(sys.argv[1], 'musicbrainz.json')
    print('compiling musicbrainz data under %s' % os.path.abspath(file_path))
    with open(file_path, 'w') as fd:
        fd.write(json.dumps(musicbrainz_data.all_data, sort_keys=True, indent=4, separators=(',', ': ')))
    

