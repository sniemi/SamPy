#
#MODULE spst_getopt
#
#******************************************************************************
"""
    **PURPOSE** --
    To provide a way to parse cli-type parameters/options and compare them
    against an 'allowed' list.  This routine is consistent with how the
    SPSS commands do parameter/option parsing, but is a little different
    than standard Unix (see the spst_getopt function description below).

    **DEVELOPER** --
    Merle Reinhart

"""
#******************************************************************************

import string, exceptions

class GetoptError(exceptions.Exception):
    """Raised when there is a commandline parser error"""
    pass
# end class GetoptError

def spst_getopt(arg_list, allowed_options=[]):
    """This function will parse the input list of cli-type parameters/options
       looking for allowed option/values as specified in the allowed_options
       list.  This is an adaptation of the Python 1.5.2 getopt.py library
       routine.

       Written by Merle Reinhart, 4-Dec-2000

       ARGUMENTS:
           arg_list  -- *(list)*  This is the input argument list to be
                                  parsed without the reference to the
                                  running program (ie. like sys.argv[1:]).
                                  Parameters and options can occur in any
                                  order.  Options must be contain a leading
                                  '-'.  Options which have values should have
                                  a trailing '=' followed by the value.

           allowed_options -- *(list)*
                                  This is a list that describes the allowed
                                  options that the function may find in the
                                  arg_list.  Each option should be completely
                                  specified without the leading '-'.  If the
                                  option allows a value, then it should
                                  contain a trailing '='.

       RETURNS:
           options -- *(dictionary)*
                                  This is a dictionary of all option/value
                                  combinations that were found in the input
                                  arg_list.  The key is the option and the
                                  value is the value of the option.

           parms -- *(list)*      This is a list of all the parameters that
                                  were found in the input arg_list in the
                                  order they occured.

       RAISES:
           GetoptError            If an option is found in arg_list that
                                    is not contained in allowed_options.
                                  If an option contains a value but
                                    allowed_options says no value is allowed.
                                  If an option does not have a value but
                                    allowed_options says it must have a value.
                                  If an option in arg_list cannot be uniquely
                                    mapped to an option in allowed_options.
    """

    options = {}
    parms   = []

    # If the inputs are not a list, then make it so
    if (type(arg_list) == type('')):
        arg_list = string.split(arg_list)
    else:
        arg_list = list(arg_list)
    # end if
    if (type(allowed_options) == type('')):
        allowed_options = string.split(allowed_options)
    else:
        allowed_options = list(allowed_options)
    # end if
    allowed_options.sort()

    # go through the list one-by-one
    for i in arg_list:
        if (i[0:1] == '-'):
            tempopt, tempval = check_options(i[1:], allowed_options)
            options['-' + tempopt] = tempval or ''
        else:
            parms.append(i)
        # end if
    # end for i

    return options, parms
# end def spst_getopt


def check_options(option, allowed_options):
    """Check the option to see if it is one of the allowed_options.
       If so, then see if it has a value.
    """

    # See if a value was passed for the option
    j = string.find(option, '=')
    if (j >= 0):
        optpar = option[:j]
        optval = option[j+1:]
    else:
        optpar = option
        optval = None
    # end if

    # See if this option is supposed to have an argument
    has_arg, found_opt = check_option_for_args(optpar, allowed_options)
    optpar = found_opt

    if (has_arg):
        if (optval is None):
            raise GetoptError('option -%s requires argument' % optpar)
        # end if
    elif (optval):
        raise GetoptError('option -%s must not have an argument' % optpar)
    # end if

    return optpar, optval
# end def check_options


def check_option_for_args(option, allowed_options):
    """Check to see if the option is supposed to have arguments.
    """

    optlen = len(option)
    # Only match with what was passed in...ie, minimum matching for legality
    for i in range(len(allowed_options)):
        x, y = allowed_options[i][:optlen], allowed_options[i][optlen:]
        if (option != x):
            continue
        # end if
        if ((y != '') and (y != '=') and ((i+1) < len(allowed_options))):
            if (option == allowed_options[i+1][:optlen]):
                raise GetoptError('option -%s not a unique prefix' % option)
            # end if
        # end if
        if (allowed_options[i][-1:] in ('=', )):
            return 1, allowed_options[i][:-1]
        # end if
        return 0, allowed_options[i]
    # end for i
    raise GetoptError('option -%s not recognized' % option)
# end def check_option_for_args


if __name__ == '__main__':
    import sys
    print spst_getopt(sys.argv[1:], ['alpha=','beta'])
