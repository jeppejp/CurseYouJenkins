import curses

TOP_HEIGHT = 15
JOB = 1
BUILD = 2
CONSOLE = 3


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


class Layout:

    def add_jobs(self):
        for i in range(0, self._top_height - 2):
            self._jobs.addstr(i + 1, 1, "job %s" % i)

    def add_builds(self):
        for i in range(0, self._top_height - 2):
            self._builds.addstr(i + 1, 1, "build %s" % i)

    def add_buildview(self):
        (y, x) = self._buildview.getmaxyx()
        max_lines = y - 2
        lines = self.console.get(max_lines, x - 2)
        for idx, line in enumerate(lines):
            if len(line) > (x - 2):
                line = line[:(x - 2)]
            try:
                self._buildview.addstr(idx + 1, 1, line)
            except Exception as e:
                raise Exception(str([idx, line]))

    def add_borders(self, screen, name):
        if self._active == name:
            screen.border(".", ".", ".", ".", ".", ".", ".", ".")
        else:
            screen.border()

    def main(self, stdscr):
        self._active = JOB
        self._top_height = TOP_HEIGHT
        self.console = ConsoleText()
        self._stdscr = stdscr
        (self._maxy, self._maxx) = self._stdscr.getmaxyx()
        curses.curs_set(0)
        self._stdscr.timeout(100)
        self._redraw = True

        while True:
            if self._redraw:
                self._jobs = curses.newwin(self._top_height, self._maxx / 2, 0, 0)
                self._builds = curses.newwin(self._top_height, self._maxx / 2, 0, self._maxx / 2)
                self._buildview = curses.newwin(self._maxy - self._top_height - 1, self._maxx, self._top_height, 0)
                self._redraw = False
            self.add_jobs()
            self.add_builds()
            self.add_buildview()

            self.add_borders(self._jobs, JOB)
            self.add_borders(self._builds, BUILD)
            self.add_borders(self._buildview, CONSOLE)

            self._jobs.refresh()
            self._builds.refresh()
            self._buildview.refresh()

            s = self._stdscr.getch()
            self._stdscr.addstr(self._maxy - 1, 0, str(s))
            if s == 113:  # q
                break
            if s == 529:  # shift up
                self._top_height -= 1
                self._redraw = True
            if s == 513:  # shift down
                self._top_height += 1
                self._redraw = True
            if s == 258:  # arrow down
                self.console.offset += 1
            if s == 259:  # arrow up
                self.console.offset -= 1
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
