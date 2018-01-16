import curses
import LineBuffer
import JenkinsCache

TOP_HEIGHT = 15
JOB = 1
BUILD = 2
CONSOLE = 3


class ConsoleText:
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def increase(self):
        self.offset += 1
    def decrease(self):
        self.offset -= 1
        if self.offset < 0:
            self.offset = 0

    def get(self, numlines, maxlen):
        # try to return as many lines as possible.
        # if offset is so big that we return fewer lines than allowed, adjust it down
        if len(self.data) > numlines:
            if len(self.data[self.offset:]) < numlines and self.offset > 0:
                max_offset = len(self.data)-numlines
                self.offset = min(self.offset, max_offset)
        retval = []
        for i in range(0, min(numlines, len(self.data[self.offset:]))):
            retval.append(self.data[i + self.offset])
        for i in range(0, len(retval)):
            if len(retval[i]) > maxlen:
                retval[i] = retval[i][:maxlen]
        return retval


class Layout:
    def __init__(self):
        self._cache = JenkinsCache.JenkinsCache('http://localhost:8080')
    def create_boxes(self):
        (max_y, max_x) = self._stdscr.getmaxyx()

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
        (max_y, max_x) = self._stdscr.getmaxyx()
        time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        self._stdscr.addstr(max_y-1, 0, "THIS IS STATUS LINE"*2)

        self._stdscr.addstr(max_y-1, max_x-len(time_str)-1, time_str)

    def _update_build_buffer(self):
        (max_y, max_x) = self._stdscr.getmaxyx()
        self._buildlinebuffer = LineBuffer.LineBuffer()
        self._buildlinebuffer.height = self._top_height - 2
        self._buildlinebuffer.max_length = (max_x/2)-2
        (active_job, _) = self._joblinebuffer.active

        builds = self._cache.get_builds(active_job)
        for build in builds:
            self._buildlinebuffer.add_line(build['name'], self._to_color(result=build['result']))

    def _update_job_buffer(self):
        (max_y, max_x) = self._stdscr.getmaxyx()
        self._joblinebuffer = LineBuffer.LineBuffer()
        self._joblinebuffer.height = self._top_height - 2
        self._joblinebuffer.max_length = (max_x/2)-2
        jobs = self._cache.get_jobs()
        for j in jobs:
            self._joblinebuffer.add_line(j['name'], self._to_color(color=j['color']))

    def add_jobs(self, reload=False):
        if reload:
            self._update_job_buffer()
        for idx, (line, active, color) in enumerate(self._joblinebuffer.get_lines()):
            if active:
                attr = curses.A_BOLD
            else:
                attr = 0
            self._jobs.addstr(idx + 1, 1, line, curses.color_pair(color)|attr)

    def add_builds(self, reload=False):
        if reload:
            self._update_build_buffer()
        for idx, (line, active, color) in enumerate(self._buildlinebuffer.get_lines()):
            if active:
                attr = curses.A_BOLD
            else:
                attr = 0
            self._builds.addstr(idx + 1, 1, line, curses.color_pair(color)|attr)

    def add_buildview(self, reload=False):
        if reload:
            (ajob, _) = self._joblinebuffer.active
            (abuild, _) = self._buildlinebuffer.active
            data = self._cache.get_console(ajob, abuild)
            self.console = ConsoleText(data.split('\n'))
        
        (y, x) = self._buildview.getmaxyx()
        max_lines = y - 2
        lines = self.console.get(max_lines, x - 2)

        if len(lines) < max_lines:
            lines += [' '] * (max_lines - len(lines))
        max_length = x - 2
        for idx, line in enumerate(lines):
            if len(line) > max_length:
                line = line[:max_length]
            else:
                line = line + (max_length - len(line)) * " "
            self._buildview.addstr(idx + 1, 1, str(line))

    def add_borders(self, screen, name):
        if self._active == name:
            screen.border(".", ".", ".", ".", ".", ".", ".", ".")
        else:
            screen.border()
    def _draw_windows(self):
        self._jobs = curses.newwin(self._top_height, self._maxx / 2, 0, 0)
        self._builds = curses.newwin(self._top_height, self._maxx / 2, 0, self._maxx / 2)
        self._buildview = curses.newwin(self._maxy - self._top_height - 1, self._maxx, self._top_height, 0)


    def main(self, stdscr):
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i,i,-1)
        self._active = JOB
        self._top_height = TOP_HEIGHT
        self._stdscr = stdscr
        (self._maxy, self._maxx) = self._stdscr.getmaxyx()
        curses.curs_set(0)
        self._stdscr.timeout(100)
        self._redraw = False
        self._draw_windows()
        self.add_jobs(reload=True)
        self.add_builds(reload=True)
        self.add_buildview(reload=True)


        while True:
            if self._redraw:
                self._draw_windows()
                self._redraw = False

            self.add_borders(self._jobs, JOB)
            self.add_borders(self._builds, BUILD)
            self.add_borders(self._buildview, CONSOLE)

            self.add_jobs()
            self.add_builds()

            self._jobs.refresh()
            self._builds.refresh()
            self._buildview.refresh()

            s = self._stdscr.getch()
            self._stdscr.addstr(self._maxy - 1, 0, str([s, self._joblinebuffer.active]))
            if s == 113:  # q
                break
            if s == 529:  # shift up
                self._top_height -= 1
                self._redraw = True
            if s == 513:  # shift down
                self._top_height += 1
                self._redraw = True
            if s == 258:  # arrow down
                if self._active == JOB:
                    self._joblinebuffer.increase()
                    self.add_builds(reload=True)
                if self._active == BUILD:
                    self._buildlinebuffer.increase()
                    self.add_buildview(reload=True)
                if self._active == CONSOLE:
                    self.console.increase()
                    self.add_buildview()
            if s == 259:  # arrow up
                if self._active == JOB:
                    self._joblinebuffer.decrease()
                    self.add_builds(reload=True)
                if self._active == BUILD:
                    self._buildlinebuffer.decrease()
                    self.add_buildview(reload=True)
                if self._active == CONSOLE:
                    self.console.decrease()
                    self.add_buildview()
            if s == 260:  # arrow left
                if self._active > JOB:
                    self._active -= 1
            if s == 261:  # arrow right
                if self._active < CONSOLE:
                    self._active += 1
            if s == 338:  # pgdn
                self.console.offset += 15
            if s == 339:  # pgup
                self.console.offset -= 15


lo = Layout()
curses.wrapper(lo.main)
