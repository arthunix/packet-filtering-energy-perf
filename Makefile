all: build-subdirs

SUBDIRS := test_1 test_2 test_3 test_4

.PHONY: build-subdirs
build-subdirs:
	for i in $(SUBDIRS); do $(MAKE) $(SUBMAKEOPTS) -C $$i all; done

.PHONY:
clean:
	for i in $(SUBDIRS); do $(MAKE) $(SUBMAKEOPTS) -C $$i clean; done