XELATEX=xelatex -file-line-error -interaction=nonstopmode

.PHONY: all
all: AMazING.tex
	latexmk -pdf -pdflatex="$(XELATEX)" -use-make AMazING.tex

.PHONY: auto
auto: AMazING.tex
	latexmk -pdf -pdflatex="$(XELATEX)" -use-make -pvc AMazING.tex

.PHONY: clean
clean:
	rm -f AMazING.pdf *.aux *.bbl *bcf *.blg *.log *.out *.tdo *.toc *.xdv *.synctex.gz *.fdb_latexmk *.fls *.run.xml; \
	rm -f **/*.aux
