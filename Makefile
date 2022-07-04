VERSION = 1.2.1
.PHONY: all clean daemon cli

PREFIX     ?= /usr
CONFDIR    ?= /etc
OUTPATH	    = ./bin
TPMPATH 	= $(DESTDIR)/tmp/KEENTUNE
BINDIR      = $(DESTDIR)$(PREFIX)/bin
LOCALBINDIR = $(DESTDIR)$(PREFIX)/local/bin
SYSCONFDIR  = $(DESTDIR)$(CONFDIR)/keentune/conf/
SYSTEMDDIR  = $(DESTDIR)$(PREFIX)/lib/systemd/system

all: target

target:
	pyinstaller --clean --onefile \
		--workpath $(TPMPATH) \
		--distpath $(OUTPATH) \
		--specpath $(TPMPATH) \
		--hidden-import agent.domain.sysctl \
		--hidden-import agent.domain.iperf \
		--hidden-import agent.domain.nginx \
		--hidden-import agent.domain.sysbench \
		--name keentune-target \
		agent/agent.py

clean:
	rm -rf $(TPMPATH)
	rm -rf $(OUTPATH)
	rm -rf $(BINDIR)/keentune-target
	rm -rf $(LOCALBINDIR)/keentune-target
	rm -rf keentune-target-$(VERSION).tar.gz

install: 
	@echo "Start installing KeenTune-target"
	mkdir -p $(SYSCONFDIR)
	mkdir -p $(SYSTEMDDIR)
	install -p -D -m 0644 agent/target.conf $(SYSCONFDIR)
	install -p -D -m 0644 keentune-target.service $(SYSTEMDDIR)
	mkdir -p $(BINDIR)
	mkdir -p $(LOCALBINDIR)
	cp $(OUTPATH)/* $(BINDIR)
	cp $(OUTPATH)/* $(LOCALBINDIR)
	@echo "Make install Done."

startup:
	systemctl daemon-reload
	systemctl restart keentune-target
	systemctl restart keentune-target

tar:
	mkdir -p keentune-target-$(VERSION)
	cp  --parents $(OUTPATH)/* \
		keentune-target.service \
		LICENSE \
		Makefile \
		agent/target.conf \
		keentune-target-$(VERSION)
	tar -czvf keentune-target-$(VERSION).tar.gz keentune-target-$(VERSION)
	rm -rf keentune-target-$(VERSION)

run: all install startup