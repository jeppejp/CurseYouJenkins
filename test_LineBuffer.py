import LineBuffer


def test_add_few():
    lb = LineBuffer.LineBuffer()
    lb.add_line("line1")
    lb.add_line("line2")

    lines = lb.get_lines()
    assert(lines[0] == ("line1", True))
    assert(lines[1] == ("line2", False))
def test_emtpty_list():
    lb = LineBuffer.LineBuffer()
    assert(lb.get_lines() == [])

def test_scroll():
    lb = LineBuffer.LineBuffer()
    for i in range(0,20):
        lb.add_line("line%s" % (i))


    for i in range(0,10):
        lb.increase()

    lines = lb.get_lines()
    # active should be 10
    assert(lines[0] == ("line1 ", False))

    for i in range(0,50):
        lb.decrease()

    lines = lb.get_lines()
    assert(lines[0] == ("line0 ", True))
