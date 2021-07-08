import traceback


def get_trace_back():
    lines = traceback.format_exc().strip().split('\n')
    rl = [lines[-1]]
    lines = lines[1:-1]
    lines.reverse()
    for i in range(0, len(lines), 2):
        if i + 1 >= len(lines):
            rl.append('* \t%s' % (lines[i].strip()))
        else:
            rl.append('* \t%s at %s' % (lines[i].strip(), lines[i + 1].strip()))
    return '\n'.join(rl)
