###############################################################################
# Makefile for CUDA version of coparam program (with relocatable device code)
###############################################################################

# Directories
SRC_DIR       = src
HDR_DIR       = hdrs
BIN_DIR       = bin

# Compiler and flags
NVCC          = nvcc
# Enable relocatable device code (-rdc=true) for both compile & link.
# "-Xcompiler -fPIC" is often needed to ensure position-independent code for linking.
#NVCC_FLAGS    = -O3 -I$(HDR_DIR) -rdc=true -Xcompiler -fPIC
NVCC_FLAGS = -O3 -I$(HDR_DIR) -rdc=true -Xcompiler -fPIC --fmad=false --prec-div=true --prec-sqrt=true
NVCC_LINK_FLAGS = -O3 -rdc=true -Xcompiler -fPIC

# Source files (all .cu in src/)
CU_SOURCES    = $(wildcard $(SRC_DIR)/*.cu)
# Object files
CU_OBJECTS    = $(CU_SOURCES:.cu=.o)

# Output program name
PROGRAM       = cuda_coparam

###############################################################################
# Default Rule
###############################################################################
all: $(PROGRAM)

# Link rule - produce final executable from .o files
# Note: Add "-lcudadevrt" if device runtime resolution is needed.
$(PROGRAM): $(CU_OBJECTS)
	$(NVCC) $(NVCC_LINK_FLAGS) $(CU_OBJECTS) -o $@ -lcudadevrt

# Compilation rule for CUDA source files -> object files
# "-dc" is equivalent to "--device-c" (generates device code for separate compilation).
$(SRC_DIR)/%.o: $(SRC_DIR)/%.cu
	$(NVCC) $(NVCC_FLAGS) -dc $< -o $@

###############################################################################
# Cleanup
###############################################################################
clean:
	rm -f $(SRC_DIR)/*.o $(PROGRAM)

###############################################################################
# Phony Targets
###############################################################################
.PHONY: all clean

