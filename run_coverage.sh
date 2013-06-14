rm cover/ -rf
nosetests tests/test.py --with-coverage --cover-erase --cover-package=firelet --cover-html

