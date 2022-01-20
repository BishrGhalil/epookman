all: install

install:
	sudo python setup.py install --optimize=1 --record=install_log.log --prefix=/usr/local
	sudo chmod +x epookman.py
	sudo cp epookman.py /usr/bin/epookman

uninstall:
	sudo rm -rf /usr/bin/epookman

run:
	python3 epookman.py

clean:
	find epookman -depth -name __pycache__ -type d -exec rm -r -- {} \;
	find -depth -name "*.log" -type f -exec rm -rf -- {} \;
	rm -rf dist build epookman.egg-info

.PHONE: clean run
