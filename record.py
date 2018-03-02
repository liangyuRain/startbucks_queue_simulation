import time
import os.path
import sys

if __name__ == '__main__':
    version = sys.hexversion >= 0x03000000
    i = 1
    fname = 'record_{0}.txt'.format(i)
    while os.path.isfile(fname):
        i += 1
        fname = 'record_{0}.txt'.format(i)
    count = 0
    s = 'Record saved in {0}'.format(fname)
    print(s)
    with open(fname, 'w') as f:
        while True:
            if version:
                input()
            else:
                raw_input()
            count += 1
            t = time.asctime(time.localtime())
            s = '{0}\t{1}'.format(count, t)
            print(s)
            f.write(s + '\n')
            f.flush()
