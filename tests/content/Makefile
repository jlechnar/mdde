default:
	./run.sh

force:

%.odt.png: %.odt force
	libreoffice --headless --convert-to png $<
	cp -f $*.png $*.org.png
	convert $*.org.png -background white -flatten -alpha off $*.bg.png
	convert $*.bg.png -trim $@
	rm -rf $*.org.png $*.bg.png $*.png
        
%.odt.jpg: %.odt force
	libreoffice --headless --convert-to jpg $<
	cp -f $*.jpg $*.org.jpg
	convert $*.org.jpg -background white -flatten -alpha off $*.bg.jpg
	convert $*.bg.jpg -trim $@
	rm -rf $*.org.jpg $*.bg.jpg $*.jpg

clean:
	rm -rf *.odt.jpg *.odt.png


