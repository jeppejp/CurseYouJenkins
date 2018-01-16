
def generate_builds(cnt,nr):
    builds = []
    for i in range(0,cnt):
        status = 'SUCCESS'
        name = "build[%s]%s" % (nr, i)
        builds.append({
            'status': status,
            'name': name})
    return builds


def generate_jobs(cnt):
    jobs = []
    for i in range(0,cnt):
        name = "random_job%s" % (i)
        builds = generate_builds(60, i)
        weather = 'SUN'
        status = 'SUCCESS'
        last_build = ''
        jobs.append({
            'name': name,
            'builds': builds,
            'weather': weather,
            'status': status,
            'last_build': last_build})

    return jobs

jobs = generate_jobs(30)
import json
with open('test_data.json','w') as fp:
    fp.write(json.dumps(jobs))
