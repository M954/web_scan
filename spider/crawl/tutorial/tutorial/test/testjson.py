#encoding-utf8

import sys
import json

test = {'time':'[11:8]', 'test':'{}'}

if __name__ == "__main__":
    d = json.dumps(test)
    print d
    json.loads(d)

