import curses
import LineBuffer
import json
import JenkinsCache
import time

class ConsoleText:
    def __init__(self):
        with open('console.txt') as fp:
            self.data = fp.readlines()
        self.offset = 0

    def get(self, numlines, maxlen):
        if self.offset < 0:
            self.offset = 0
        if (self.offset + numlines) > len(self.data):
            self.offset = len(self.data) - numlines
        return self.data[self.offset: self.offset + numlines]

class JenkinsViewer:
    def __init__(self):
        self._cache = JenkinsCache.JenkinsCache('http://localhost:8080')
    def create_boxes(self):
        (max_y, max_x) = self.stdscr.getmaxyx()

        main_window = curses.newwin(max_y-1, max_x/2, 0, 0)
        top_left = curses.newwin(max_y/2, max_x/2, 0, max_x/2)
        bottom_left = curses.newwin(max_y/2-1, max_x/2, max_y/2, max_x/2)
        return main_window, top_left, bottom_left

    def gen_border(self, window, active):
        if active:
            window.border()
        else:
            window.border(".",".",".",".",".",".",".",".")

    def _to_color(self, score=None, color=None, result=None):
        if score >= 80 or color == 'blue' or result == 'SUCCESS':
            return 83
        if score >= 20 or color == 'yellow':
            return 191
        if (score < 20 and score >= 0)  or color == 'red' or result == 'FAILURE':
            return 197
        if color == 'notbuilt':
            return 0
        self.bottom.addstr(1, 1, str([score, color, result]))
        return 10

    def update_status_line(self):
        (max_y, max_x) = self.stdscr.getmaxyx()
        time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        self.stdscr.addstr(max_y-1, 0, "THIS IS STATUS LINE"*2)

        self.stdscr.addstr(max_y-1, max_x-len(time_str)-1, time_str)

    def _update_build_buffer(self):
        (max_y, max_x) = self.stdscr.getmaxyx()
        self._buildlinebuffer = LineBuffer.LineBuffer()
        self._buildlinebuffer.height = (max_y/2)-2
        self._buildlinebuffer.max_length = (max_x/2)-2
        (active_job, _) = self._joblinebuffer.active

        builds = self._cache.get_builds(active_job)
        for build in builds:
            self._buildlinebuffer.add_line(build['name'], self._to_color(result=build['result']))

    def _update_job_buffer(self):
        (max_y, max_x) = self.stdscr.getmaxyx()
        self._joblinebuffer = LineBuffer.LineBuffer()
        self._joblinebuffer.height = (max_y)-3
        self._joblinebuffer.max_length = (max_x/2)-2
        jobs = self._cache.get_jobs()
        for j in jobs:
            self._joblinebuffer.add_line(j['name'], self._to_color(color=j['color']))

    def main(self, stdscr):
        self.stdscr = stdscr
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i,i,-1)

        self.main, self.top, self.bottom = self.create_boxes()
        self._update_job_buffer()
        self._update_build_buffer()

        s = ''
        curses.curs_set(0)
        self.stdscr.timeout(100)
        active_window = 'main'
        while True:
            self.gen_border(self.main, active_window=='main')
            self.gen_border(self.top, active_window=='top')
            self.gen_border(self.bottom, active_window=='bottom')
            self.update_status_line()


            lines = self._joblinebuffer.get_lines()
            for i in range(0, len(lines)):
                attr = curses.color_pair(lines[i][2])
                if lines[i][1]:
                    attr |= curses.A_BOLD
                self.main.addstr(i+1,1, str(lines[i][0]), attr)

            buildlines = self._buildlinebuffer.get_lines()
            for i in range(0, len(buildlines)):
                attr = curses.color_pair(buildlines[i][2])
                if buildlines[i][1]:
                    attr |= curses.A_BOLD
                self.top.addstr(i+1,1, str(buildlines[i][0]), attr)




            self.main.refresh()
            self.top.refresh()
            self.bottom.refresh()
            
            
            
            
            s = self.stdscr.getch()
            if s == 113:
                break
            if s == 258: # down
                if active_window == 'main':
                    self._joblinebuffer.increase()
                    self._update_build_buffer()
                if active_window == 'top':
                    self._buildlinebuffer.increase()
            if s == 259: # up
                if active_window == 'main':
                    self._joblinebuffer.decrease()
                    self._update_build_buffer()
                if active_window == 'top':
                    self._buildlinebuffer.decrease()
            if s == 261: # right
                if active_window == 'main':
                    active_window = 'top'
                elif active_window == 'top':
                    active_window = 'bottom'

            if s == 260: # left
                if active_window == 'bottom':
                    active_window = 'top'
                elif active_window == 'top':
                    active_window = 'main'
            if s == 338: # pgdn
                if active_window == 'main':
                    for i in range(0,10):
                        self._joblinebuffer.increase()
                    self._update_build_buffer()
            if s == 339: # pgup
                if active_window == 'main':
                    for i in range(0,10):
                        self._joblinebuffer.decrease()
                    self._update_build_buffer()

if __name__ == "__main__":
    jw = JenkinsViewer()
    curses.wrapper(jw.main)
