# make is smart, it knows how to make *.o from *.c

CFLAGS+=-O3
# CFLAGS+=-march=native
CFLAGS+=-fomit-frame-pointer
CFLAGS+=-g
CFLAGS+=-I .
CFLAGS+=-flto
CXXFLAGS+=-O3
CXXFLAGS+=-g
# CXXFLAGS+=-march=native
CXXFLAGS+=-fomit-frame-pointer
CXXFLAGS+=-I .
CXXFLAGS+=-flto
# CFLAGS+=--std c11

LDFLAGS:=-O3 -flto -lboost_thread -lboost_system

# CC=clang
# CXX=clang++

CC=cc
CXX=c++

# find_collisions: find_collisions.o sha2.o
find_collisions: find_collisions.o sha256_sse4.o sha256_avx1.o sha256.o
	$(CXX) $(LDFLAGS) $^ -o find_collisions 






sha256_sse4.o:
	yasm -f x64 -f elf64 -X gnu -g dwarf2 -D LINUX -o sha256_sse4.o sha256_sse4.asm

sha256_avx1.o:
	yasm -f x64 -f elf64 -X gnu -g dwarf2 -D LINUX -o sha256_avx1.o sha256_avx1.asm

clean:
	rm -f find_collisions.o sha256.o sha2.o sha256_sse4.o sha256_avx.o
