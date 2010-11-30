#include <Python.h>

/* function to be wrapped */
void HelloWorld () {
  printf("Hello World\n");

}

/* Wrapper - returns a Python object representing a method */

PyObject *wrap_HelloWorld(PyObject *self, PyObject *args) { 
  HelloWorld(); 
  return Py_BuildValue("");
}




void HelloWorld2(char *name) {
  printf("Hello %s\n", name);
}


PyObject *wrap_Hello2(PyObject *self, PyObject *args) { 
  char *name;
  if (!PyArg_ParseTuple(args, "s", &name))
    return NULL;
  HelloWorld2(name); 
  return Py_BuildValue("");
}




int factorial(int x) {
  if (x == 1) {
    return x;
  } else {
    return x * factorial(x - 1);
  }
}


PyObject *wrap_fact(PyObject *self, PyObject *args) {
  int x, y;
  if (!PyArg_ParseTuple(args, "i", &x))
    return NULL;
  y = factorial(x);
  return Py_BuildValue("i", y);
}

int gcd(int x, int y) {
    int g = y;
    while (x > 0) {
        g = x;
        x = y % x;
        y = g;
    }
    return g;
}



PyObject *wrap_gcd(PyObject *self, PyObject *args) {
    int x,y,g;
    if(!PyArg_ParseTuple(args, "ii", &x, &y))
       return NULL;
    g = gcd(x, y);
    return Py_BuildValue("i", g);
}



PyObject *wrap_gcdmult(PyObject *self, PyObject *args) {
    int x,y,g;
    if(!PyArg_ParseTuple(args, "ii", &x, &y))
       return NULL;
    g = gcd(x, y);
    return Py_BuildValue("ii", g, y);
}



/* List of all functions in the module */
static PyMethodDef hellomethods[] = {
   {"HelloWorld", wrap_HelloWorld, METH_VARARGS },
   {"HelloWorld2", wrap_Hello2, METH_VARARGS },
   {"factorial", wrap_fact, METH_VARARGS },
   {"gcd", wrap_gcd, METH_VARARGS },
   {"gcdmult", wrap_gcdmult, METH_VARARGS },
   { NULL, NULL }
};

/* Module initialization function */
void inithello(void) {
  Py_InitModule("hello", hellomethods);
}
    
