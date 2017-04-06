test:
	python -m unittest discover -s tests -v -p '*test*.py' 

testone:
	python -m unittest -q tests.test.TestMenu.test_building_structure
	#python -m tests.test.TestMenu.test_building_structure
