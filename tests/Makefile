default:
	./run.sh

always:

%.log: %.py %.md always
	python3 $*.py | tee $@

clean:
	rm -rf *.log *.html *_mapped.txt

