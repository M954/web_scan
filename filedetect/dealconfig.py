#encoding=utf8

if __name__ == "__main__":
	for i in open('config.txt').readlines():
		i = i.strip()
		print i[1:]
