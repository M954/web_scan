#encoding=utf8


if __name__ == "__main__":
    for i in open('domain_suffix').readlines():
        tmp = i.split()
        for t in tmp:
            if '.' in t:
                print t.split('.')[-1]
