.PHONY: all clean help


all:
	sudo su
	apt-get install software-properties-common
	apt-add-repository ppa:deadsnakes/ppa
	apt install python3.9
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	python3.9 get-pip.py
	