all: 

run:
	python3 epookman.py

clean:
	rm -rf __pycache__/

.PHONE: clean run
