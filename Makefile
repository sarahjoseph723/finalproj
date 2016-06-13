file = final.mdl

final: lex.py main.py matrix.py mdl.py script.py yacc.py 
	mkdir -p anim
	python main.py $(file)


make: $(file) lex.py main.py matrix.py mdl.py script.py yacc.py
	mkdir -p anim
	python main.py $(file)

clean:
	rm anim/* *pyc *out parsetab.py

clear:
	rm anim/* *pyc *out parsetab.py *ppm
