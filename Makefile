all: 

run:
	python3 epookman.py

clean:
	find epookman -depth -name __pycache__ -type d -exec rm -r -- {} \;
	find -depth -name "*.log" -type f -exec rm -r -- {} \;

.PHONE: clean run
