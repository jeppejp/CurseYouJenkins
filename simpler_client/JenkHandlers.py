import requests
import json

COL_RED = '\x1b[31m'
COL_BLUE = '\x1b[34m'
COL_YELLOW = '\x1b[33m'
COL_GREEN = '\x1b[32m'
COL_STOP = '\x1b[0m'


def get_color(s):
    if s == 'blue' or s == 'SUCCESS':
        return COL_BLUE
    if s == 'green':
        return COL_GREEN
    if s == 'red' or s == 'FAILURE' or s == 'red_anime':
        return COL_RED
    if s == 'yellow' or s == 'UNSTABLE' or s == 'yellow_anime':
        return COL_YELLOW
    if s == 'aborted':
        return COL_YELLOW
    if s == 'notbuilt':
        return COL_YELLOW
    if s == 'disabled':
        return COL_YELLOW
    if s == 'ABORTED' or s is None or s == 'notbuilt_anime':
        return ''
    raise Exception("Unknown color %s" % s)


def print_builds(joburl, cnt, console_log):
    if cnt == 0:
        return
    req_job = requests.get(joburl + 'api/json?depth=1')
    data = json.loads(req_job.text)
    if 'builds' not in data.keys():
        return
    printed = 0
    for b in data['builds']:
        display = b['displayName']
        result = b['result']
        buildurl = b['url']
        print get_color(result) + "  %s  %s" % (display, result) + COL_STOP
        print_console(buildurl, console_log)
        printed += 1
        if printed >= cnt:
            return


def print_console(url, cnt):
    if cnt is None:
        return
    req = requests.get(url + 'consoleText')
    lines = req.text.split('\n')
    if cnt == 0:
        for line in lines:
            print line
    else:
        for line in lines[-cnt:]:
            print line


def job_is_match(jobname, matchlst):
    if len(matchlst) == 0:
        return True
    for m in matchlst:
        if m in jobname:
            return True
    return False

def handle(url, show_builds, match, console_log):
    req = requests.get(url + 'api/json')
    data = json.loads(req.text)

    for job in data['jobs']:
        jobname = job['name']
        joburl = job['url']
        jobcolor = job['color']
        if job_is_match(jobname, match):
            print get_color(jobcolor) + jobname + COL_STOP
            print_builds(joburl, show_builds, console_log)
