#include <math.h>
#include <stdint.h>
#include <Python.h>

uint8_t 
isprime(uint64_t n)
{
    uint64_t i;
    uint64_t maximum;

    if (n < 2)
    {
        return 0;
    }
    if (n == 2)
    {
        return 1;
    }
    if (n % 2 == 0)
    {
        return 0;
    }

    maximum = (uint64_t) sqrt((double) n);
    i = 3;
    while (i <= maximum)
    {
        if (n % i == 0) 
        {
            return 0;
        }
        i += 2;
    }
    return 1;
}

uint64_t
sum_primes(uint64_t n)
{
    uint64_t i;
    uint64_t sum;
    sum = 0;
    for (i = 2; i < n; i++)
    {
        if (isprime(i))
        {
            sum += i;
        }
    }
    return sum;
}

static PyObject *
py_sum_primes(PyObject *self, PyObject *args)
{
    uint64_t n;
    uint64_t sum;
    if (!PyArg_ParseTuple(args, "K", &n))
    {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    sum = sum_primes(n);
    Py_END_ALLOW_THREADS
    return Py_BuildValue("K", sum);
}

static PyMethodDef CPrimesMethods[] =
{
    {"sum_primes", py_sum_primes, METH_VARARGS, "Sum all primes less than n"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initcprimes(void)
{
    (void) Py_InitModule("cprimes", CPrimesMethods);
}
