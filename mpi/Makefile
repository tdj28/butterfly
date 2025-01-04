###############################################################################
# Makefile for "coparam" MPI program
# - Puts all .c in src/ into OBJ, plus one "globals.c" that defines the globals.
# - Generates dependencies automatically in .depend.
# - Standard targets: "all" (build), "clean", etc.
###############################################################################

# If "GNU Make" is not used, this ifneq check triggers a warning. 
ifneq (,)
    This makefile requires GNU Make.
endif

###############################################################################
# Directories & Build Settings
###############################################################################
SRC_DIR   = src
HDR_DIR   = hdrs
BIN_DIR   = bin
MPI_DIR   = /data/project/mpich-install/include

CC        = mpicc
CFLAGS    = -O2 -DDEBUG=1 -I$(HDR_DIR) -I$(MPI_DIR)
LDFLAGS   = -lm

PROGRAM   = coparam

###############################################################################
# Source & Object Lists
###############################################################################
# Gather all C source files under src/
C_FILES   := $(wildcard $(SRC_DIR)/*.c)
OBJS      := $(patsubst %.c, %.o, $(C_FILES))

###############################################################################
# Default Rule
###############################################################################
all: $(PROGRAM)

$(PROGRAM): .depend $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) $(LDFLAGS) -o $@

###############################################################################
# Dependency Generation
###############################################################################
depend: .depend

.depend: cmd = gcc -MM -MF depend $(var); cat depend >> .depend;
.depend:
	@echo "Generating dependencies..."
	@$(foreach var, $(C_FILES), $(cmd))
	@rm -f depend

-include .depend

###############################################################################
# Compile Rules
###############################################################################
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

###############################################################################
# Cleanup
###############################################################################
clean:
	rm -f .depend $(SRC_DIR)/*.o $(PROGRAM)

###############################################################################
# Phony Targets
###############################################################################
.PHONY: all clean depend

