'''
Example script how to match rows with SQL.

:author: Sami-Matias Niemi
'''

if __name__ == '__main__':
    import sqlite3
    import numpy as N
    import pylab as P
    import astLib.astCoords as Coords
    from cosmocalc import cosmocalc
    import cosmology.distances as dist

    conversion = 0.000277777778 # degree to arcsecond

    data = N.array([[1849384, 1, 189.53117, 62.073025, 0.02513],
        [1852725, 1, 189.58427, 62.384327, 0.024573],
        [1852725, 2, 189.65951, 62.376747, 0.024573],
        [1851653, 3, 189.72211, 62.086521, 0.024767],
        [1851653, 5, 189.68188, 62.121794, 0.024767],
        [1851653, 6, 189.68566, 62.144206, 0.024767],
        [2185247, 1, 189.21627, 62.086777, 0.028581],
        [2185241, 1, 189.67465, 62.044975, 0.028573],
        [2185241, 7, 189.69131, 62.065615, 0.028573],
        [2176447, 1, 189.62968, 62.200272, 0.030789],
        [2180427, 1, 189.05091, 62.045602, 0.029864],
        [2178429, 1, 189.60425, 62.390785, 0.030206],
        [2178429, 11, 189.55878, 62.413759, 0.030206],
        [2178429, 12, 189.60903, 62.424642, 0.030206],
        [2178429, 13, 189.57792, 62.425876, 0.030206],
        [2184468, 1, 188.85568, 62.025154, 0.028962]])

    data2 = N.array([[1849384, 1, 1.11],
        [1852725, 1, 2.22],
        [1852725, 2, 3.33],
        [1851653, 3, 4.44],
        [1851653, 5, 5.55],
        [1851653, 6, 6.66],
        [2185247, 1, 7.77],
        [2185241, 1, 8.88],
        [2185241, 7, 9.99],
        [2176447, 1, 11.11],
        [2180427, 1, 22.22],
        [2178429, 1, 33.33],
        [2178429, 11, 44.44],
        [2178429, 12, 55.55],
        [2178429, 13, 66.66],
        [2184468, 1, 77.77]])
    #DB connection
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    #create a table
    cursor.execute('create table lightcone (halo_id, gal_id, ra, dec, redshift)')
    #insert data
    for line in data:
        cursor.execute('insert into lightcone values (?,?,?,?,?)', (line))
    conn.commit()

    #create a second table
    cursor.execute('create table galprop (halo_id, gal_id, foo)')
    for l in data2:
        cursor.execute('insert into galprop values (?,?,?)', (l))
    conn.commit()

    #query to pull out the data where halo_id matches but gal_id is different
    query = '''select l1.redshift, l1.ra, l1.dec, l1.halo_id, l1.gal_id, galprop.foo from lightcone l1
               inner join galprop using (halo_id, gal_id)
               inner join
               (
               select l2.halo_id, l2.gal_id from lightcone l2 where
               l2.halo_id in (select halo_id from lightcone group by halo_id having count(*) > 1)
               intersect
               select l3.halo_id, l3.gal_id from lightcone l3
               group by l3.halo_id, l3.gal_id having count(*) == 1
               )
               using (halo_id, gal_id)
               where l1.redshift > 0.03
               '''

    #get data back
    cursor.execute(query)
    matched = N.array(cursor.fetchall())

    fig = P.figure()
    ax = fig.add_subplot(111)

    #group them by halo_id
    for x in set(matched[:, 3]):
        tmp = matched[matched[:, 3] == x]

        #redshift
        z = tmp[0][0]

        RADeg1 = tmp[0][1]
        decDeg1 = tmp[0][2]

        RADeg2 = tmp[1:, 1]
        decDeg2 = tmp[1:, 2]

        prop = tmp[:, 5]

        sep = Coords.calcAngSepDeg(RADeg1, decDeg1, RADeg2, decDeg2)

        dd = cosmocalc(z, 71.0, 0.28)['PS_kpc'] #dist.getDiameterDistances(data)
        physical_distance = (sep / dd) / conversion

        print z, RADeg1, RADeg2, decDeg1, decDeg2, prop
        print sep, physical_distance
        print

        ax.plot([z for foo in range(len(physical_distance))], physical_distance, 'bo')

    #P.show()

    print
    print

    cursor.execute('CREATE TABLE newTable (h1, g1, h2, g2, foo)')
    newqu = '''INSERT INTO newTable
               SELECT l1.halo_id, l1.gal_id, galprop.halo_id, galprop.gal_id, galprop.foo
               FROM lightcone l1
               INNER JOIN galprop USING (halo_id, gal_id)
               '''
    cursor.execute(newqu)
    conn.commit()
    cursor.execute('select * from newTable')
    data = N.array(cursor.fetchall())
    print data