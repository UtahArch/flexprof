BINDIR = ../bin
OBJDIR = ../obj
OBJS = $(OBJDIR)/main.o $(OBJDIR)/memory_controller.o $(OBJDIR)/scheduler.o
CC = gcc
DEBUG = -g
CFLAGS = -std=c99 -Wall -c -fcommon $(DEBUG)
LFLAGS = -Wall $(DEBUG)
OUT = usimm

$(shell mkdir -p $(BINDIR) $(OBJDIR))

$(BINDIR)/$(OUT): $(OBJS)
	$(CC) $(LFLAGS) $(OBJS) -o $(BINDIR)/$(OUT)
	chmod 777 $(BINDIR)/$(OUT)

$(OBJDIR)/main.o: main.c processor.h configfile.h memory_controller.h scheduler.h params.h
	$(CC) $(CFLAGS) main.c -o $(OBJDIR)/main.o
	chmod 777 $(OBJDIR)/main.o

$(OBJDIR)/memory_controller.o: memory_controller.c utlist.h utils.h params.h memory_controller.h scheduler.h processor.h
	$(CC) $(CFLAGS) memory_controller.c -o $(OBJDIR)/memory_controller.o
	chmod 777 $(OBJDIR)/memory_controller.o

$(OBJDIR)/scheduler.o: scheduler.c scheduler.h utlist.h utils.h memory_controller.h params.h
	$(CC) $(CFLAGS) scheduler.c -o $(OBJDIR)/scheduler.o
	chmod 777 $(OBJDIR)/scheduler.o

close: OUT = usimm-close
close: $(OBJDIR)/main.o $(OBJDIR)/memory_controller.o
	$(CC) $(CFLAGS) scheduler-close.c -o $(OBJDIR)/scheduler-close.o
	chmod 777 $(OBJDIR)/scheduler-close.o
	@echo "Building $(BINDIR)/$(OUT)"
	$(CC) $(LFLAGS) $(OBJDIR)/main.o $(OBJDIR)/memory_controller.o $(OBJDIR)/scheduler-close.o -o $(BINDIR)/$(OUT)
	chmod 777 $(BINDIR)/$(OUT)


fsbta: OUT = usimm-fsbta
fsbta: $(OBJDIR)/main.o $(OBJDIR)/memory_controller.o
	$(CC) $(CFLAGS) scheduler-fsbta.c -o $(OBJDIR)/scheduler-fsbta.o
	chmod 777 $(OBJDIR)/scheduler-fsbta.o
	@echo "Building $(BINDIR)/$(OUT)"
	$(CC) $(LFLAGS) $(OBJDIR)/main.o $(OBJDIR)/memory_controller.o $(OBJDIR)/scheduler-fsbta.o -o $(BINDIR)/$(OUT)
	chmod 777 $(BINDIR)/$(OUT)

fsbta-rwopt: OUT = usimm-fsbta-rwopt
fsbta-rwopt: $(OBJDIR)/main.o $(OBJDIR)/memory_controller.o
	$(CC) $(CFLAGS) scheduler-fsbta-rwopt.c -o $(OBJDIR)/scheduler-fsbta-rwopt.o
	chmod 777 $(OBJDIR)/scheduler-fsbta-rwopt.o
	@echo "Building $(BINDIR)/$(OUT)"
	$(CC) $(LFLAGS) $(OBJDIR)/main.o $(OBJDIR)/memory_controller.o $(OBJDIR)/scheduler-fsbta-rwopt.o -o $(BINDIR)/$(OUT)
	chmod 777 $(BINDIR)/$(OUT)

rta: OUT = usimm-rta
rta: $(OBJDIR)/main.o $(OBJDIR)/memory_controller.o
	$(CC) $(CFLAGS) scheduler-rta.c -o $(OBJDIR)/scheduler-rta.o
	chmod 777 $(OBJDIR)/scheduler-rta.o
	@echo "Building $(BINDIR)/$(OUT)"
	$(CC) $(LFLAGS) $(OBJDIR)/main.o $(OBJDIR)/memory_controller.o $(OBJDIR)/scheduler-rta.o -o $(BINDIR)/$(OUT)
	chmod 777 $(BINDIR)/$(OUT)

all: close fsbta fsbta-rwopt rta $(BINDIR)/$(OUT)


clean:
	rm -f $(BINDIR)/* $(OBJDIR)/*
