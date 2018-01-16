import requests
import time
import json
import unicodedata

"""
    .job
        color
        score
        name
    .build
        name
        duration  ( / 1000 to get secs)
        result
        timestamp ( / 1000 to get secs)
"""

MAX_AGE = 20

class CachedObject:
    def __init__(self, url):
        self._url = url
        self._data = ""
        self._ts = 0
        self._max_age = MAX_AGE

    def get_data(self):
        now = time.time()
        if (now - self._ts) > self._max_age:
            text = requests.get(self._url).text
            self._data = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
            self._ts = now
        return self._data

class JenkinsCache:
    def __init__(self, url):
        self.url = url
        self._cache = {}

    def _get_url(self, url):
        if url not in self._cache:
            self._cache[url] = CachedObject(url)
        return self._cache[url].get_data()

    def get_jobs(self):
        jobs_url = self.url + "/api/json?depth=1"
        json_blob = self._get_url(jobs_url)
        jobs = []
        job_data = json.loads(json_blob)
        score = -1
        for j in job_data['jobs']:
            if 'healthReport' in j.keys():
                if len(j['healthReport']) > 0:
                    score = j['healthReport'][0]['score']
            jobs.append({
                'color': j['color'],
                'score': score,
                'name': j['fullDisplayName']})
        return jobs

    def get_builds(self, job):
        build_url = self.url + '/job/' + job + '/api/json?depth=1'
        json_blob = self._get_url(build_url)
        builds = []
        build_data = json.loads(json_blob)

        for b in build_data['builds']:
            builds.append({
                'name': b['displayName'],
                'duration': float(b['duration'])/1000.0,
                'result': b['result'],
                'timestamp': int(float(b['timestamp'])/1000.0)
                })
        return builds

    def get_console(self, job, build):
        url = self.url + '/job/' + job + '/' + build.replace('#','') + '/consoleText'
        return self._get_url(url)

    def get_build_info(self, job, build):
        return {}

if __name__ == '__main__':
    jc = JenkinsCache('http://localhost:8080/')

    print jc.get_jobs()
    print jc.get_builds('hest')
