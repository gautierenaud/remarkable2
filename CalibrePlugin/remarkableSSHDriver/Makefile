.PHONY: driver init all

init:
	git submodule update --init

driver:
	rm -f ./rmSSHDriver.zip
	zip ./rmSSHDriver.zip ./*.py *.txt

all: driver
	calibre-customize --add-plugin rmSSHDriver.zip