def getData(sql):
    import MySQLdb as M

    db = M.Connect(host='eeva', user='select_user', passwd='select_pass', db = 'Pipeline',)
    cursor = M.cursors.Cursor(db)
    cursor.execute(sql)
    result  = cursor.fetchall()
    cursor.close()
    db.close()
    return result

if __name__ == '__main__':
    import pylab as P
    import numpy as N

    sql = """SELECT x_dist,
    y_dist
    FROM FocusALobj
    WHERE exptime > 5.
    AND N > 2
    AND medianOffset between -45 and 45
    AND stdevOffset < 20
    AND stdevOffset != 0.0
    AND ALFLTNM ='Open'
    AND FAFLTNM ='Open'
    AND FBFLTNM ='Open'
    AND ALFOCUS = 1810"""
    
    temp = getData(sql)
    data = N.array(temp)

    xdist = data[:,0]
    ratio = data[:,0] / data[:,1]
    
    P.scatter(xdist, ratio)
    P.savefig('dist')
    P.xlabel('x_dist')
    P.ylabel('x_dist / y_dist')
    P.show()

