"""
A script to pull out information from ZEPPO for STIS MSM montly monitoring.

:date: Created on Mar 23, 2009

:author: Sami-Matias Niemi
"""

__author__ = 'Sami-Matias Niemi'
__version__ = '1.0'

def getMonth():
    """
    Returns a date 4 weeks ago from today.
    """
    import datetime

    date = datetime.date.today()
    delta = datetime.timedelta(weeks=-4)

    return (date + delta)


def saveDataToFile(filename, data):
    """
    Prints data to a file.
    """
    output = open(filename, 'w')

    hdr1 = """Axis1      Axis2    Aperture  Slit    Date        Configuration  Spec. Elem.  Wavel.  Data Set  Target     Prop\n"""
    hdr2 = (
           '-' * 9 + ' ') * 3 + '-' * 4 + '   ' + '-' * 11 + ' ' + '-' * 15 + ' ' + '-' * 22 + ' ' + '-' * 4 + ' ' + '-' * 11 + ' ' + '-' * 15 + '\n'

    output.write(hdr1)
    output.write(hdr2)

    for line in data:
        tmp = ''
        for cell in line:
            tmp += str(cell) + ' '
        tmp += '\n'
        output.write(tmp)

    output.close()


if __name__ == '__main__':
    """
    A script to pull out information from ZEPPO for STIS MSM monitor.
    """
    import DB
    import datetime

    #Change these accordingly
    server = 'ZEPPO'
    user = 'yourusername'
    passwd = 'yourpasswd'
    database = 'dadsops'
    outputfile = 'output.test'

    #Lets get the date 4 weeks ago from today...
    lastmonth = getMonth()

    #SQL statement, change this
    sql = """select 
    st.ssa_shifta1,
    st.ssa_shifta2,
    s.sci_aper_1234,
    sc.ssc_slitnum,
    st.ssa_expend,
    s.sci_instrument_config,
    s.sci_spec_1234,
    s.sci_central_wavelength,
    s.sci_data_set_name,
    s.sci_targname,
    s.sci_pep_id
    from science s, stis_a_data st, stis_c_data sc
    where s.sci_data_set_name = st.ssa_data_set_name
    and s.sci_data_set_name = sc.ssc_data_set_name
    and s.sci_operating_mode = 'ACCUM'
    and (st.ssa_shifta1 != 0 and st.ssa_shifta2 != 0)
    and (sc.ssc_pcn1lamp < 3 or sc.ssc_pcn2lamp < 3 or sc.ssc_pcn3lamp < 3)
    and sc.ssc_slitnum = 35
    and ((s.sci_spec_1234 = 'G430M' and s.sci_central_wavelength = 4961) or
    (s.sci_spec_1234 = 'G430L' and s.sci_central_wavelength = 4300) or
    (s.sci_spec_1234 = 'G750L' and s.sci_central_wavelength = 7751) or
    (s.sci_spec_1234 = 'G750M' and s.sci_central_wavelength = 5734) or
    (s.sci_spec_1234 = 'G750M' and s.sci_central_wavelength = 6252) or
    (s.sci_spec_1234 = 'G750M' and s.sci_central_wavelength = 6581) or
    (s.sci_spec_1234 = 'G750M' and s.sci_central_wavelength = 6768) or
    (s.sci_spec_1234 = 'G750M' and s.sci_central_wavelength = 8561) or
    (s.sci_spec_1234 = 'G230LB' and s.sci_central_wavelength = 2375) or
    (s.sci_spec_1234 = 'G230L' and s.sci_central_wavelength = 2375) or
    (s.sci_spec_1234 = 'G230M' and s.sci_central_wavelength = 2499) or
    (s.sci_spec_1234 = 'G140L' and s.sci_central_wavelength = 1425) or
    (s.sci_spec_1234 = 'G140M' and s.sci_central_wavelength = 1222) or
    (s.sci_spec_1234 = 'G140M' and s.sci_central_wavelength = 1272))
    order by st.ssa_expend"""
    #and s.sci_start_time > %s
    #order by st.ssa_expend''' % lastmonth
    
    print 'MSM Monitor - %s' % datetime.date.today()

    #pulls out the data
    data = DB.DBSMN(sql, user, passwd, database, server).fetchSybaseData()

    #saves the data to an output file
    saveDataToFile(outputfile, data)
