%module CaenBlockParsing

%{
    #define SWIG_FILE_WITH_INIT
    #include "CaenBlockParsing.h"
%}

%include "numpy.i"

%init %{
    import_array();
%}

%apply (unsigned int* INPLACE_ARRAY1, int DIM1) {(unsigned int* invec, int n)}
%apply (int* INPLACE_ARRAY1, int DIM1) {(int* chan_samples, int n0)}
%apply (unsigned int* INPLACE_ARRAY1, int DIM1) {(unsigned int* chan_indecies, int n1)}
%include "CaenBlockParsing.h"

