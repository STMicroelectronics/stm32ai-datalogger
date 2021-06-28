
UI_DIR = uiFiles
ENTRY_POINT = main.py
OUT_FOLDER=out
APP_NAME = GenericUI

all: update build-exe

build-exe:
	rm -rf out/
	pyinstaller $(ENTRY_POINT) --clean --distpath out/ --specpath $(OUT_FOLDER) --workpath out/workpath --name $(APP_NAME) --onedir
	cp -R ./ai_logging $(OUT_FOLDER)/$(APP_NAME)

build-ui: $(UI_DIR)/*
	for file in $^ ; do \
		pyside2-uic $${file} -o $${file}.py  ; \
    done 

update:
	cp -R ../python_wrapper/ai_logging .
	pyside2-rcc.exe res.qrc -o res.py 
	
