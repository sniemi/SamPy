'''
Plotting COS grating efficiency data
'''
import matplotlib

matplotlib.rc('text', usetex=True)
matplotlib.rc('xtick', labelsize=9)
matplotlib.rc('ytick', labelsize=9)
matplotlib.rc('axes', linewidth=0.8)
matplotlib.rcParams['legend.fontsize'] = 7
import idlsave, time
import pylab as P
import numpy as N
import datetime as D

def fromJulian(j):
    '''
    Converts Julian Date to human readable format

    :return: human readable date and time
    '''
    days = j - 2440587.5
    sec = days * 86400.0
    return time.gmtime(sec)


if __name__ == '__main__':
    data = idlsave.read('nes_all.dat')

    exclude_first = True
    legend = True

    c = 1
    #ran = [4,5,6,7]
    ran = [4, 5, 6, 9]

    for i in ran:
        if exclude_first:
            start = 1
            print '\nAll below fits exclude the first point shown in the plots as it was measured under different conditions'
        else:
            start = 0

        #average and dates
        #avg_r = N.mean(data.f_irats[start:,i])
        avg_r = N.mean(data.f_irats[:, i])
        dat = data.f_irats[start:, i]

        all_mjd = data.jdates
        mjd = data.jdates[start:]

        #plot
        ax = P.subplot(2, 2, c)
        P.errorbar(all_mjd, data.f_irats[:, i] / avg_r, yerr=data.f_ierats[:, i] / avg_r, marker='o', ms=4)
        P.axhline(y=1, c='k', ls=':')

        #linear fit mjd data
        fit = N.polyfit(mjd, dat / avg_r, 1)
        p = N.poly1d(fit)
        #    P.plot(all_mjd, p(all_mjd), 'r--', label = 'Linear fit, no first point')
        #    print 'Plot %i, slope %f with all data.' % (c, fit[0])
        print 'Plot %i, change %f per cent per year, all data. (fit not plotted)' % (c, fit[0] * 356. * 100.)

        #linear fit, only on orbit data
        mask = mjd > 2454970.0
        fit2 = N.polyfit(mjd[mask], dat[mask] / avg_r, 1)
        p2 = N.poly1d(fit2)
        P.plot(all_mjd, p2(all_mjd), 'g:', label='Linear fit, on orbit data', lw=1.3)
        #    print 'Plot %i, slope %f with only the last two measurements.' % (c, fit2[0])
        print 'Plot %i, change %f per cent per year, only on orbit data. Green dotted line.' % (
        c, fit2[0] * 356. * 100.)

        #fit without the two outliers, nor the first point
        mask = (mjd < 2454679.0) | (mjd > 2454904.0)
        fit3 = N.polyfit(mjd[mask], dat[mask] / avg_r, 1)
        p3 = N.poly1d(fit3)
        P.plot(all_mjd, p3(all_mjd), 'm-.', label='Linear fit, no outliers', lw=1.3)
        #    P.plot(all_mjd[mask], p3(all_mjd[mask]), 'go')
        #    print 'Plot %i, slope %f when the two outliers have been excluded.' % (c, fit3[0])
        print 'Plot %i, change %f per cent per year, all data excluding the two outliers. Magenta dot-dashed' % (
        c, fit3[0] * 356. * 100.)

        #fit to ground data, excluding the two last ground measurements
        mask4 = mjd < 2454679.0
        fit4 = N.polyfit(mjd[mask4], dat[mask4] / avg_r, 1)
        p4 = N.poly1d(fit4)
        P.plot(all_mjd, p4(all_mjd), 'r--', label='Linear fit, ground data', lw=1.3)
        #    print 'Plot %i, slope %f, only ground data, two outliers have been excluded.' % (c, fit4[0])
        print 'Plot %i, change %f per cent per year, ground data excluding the two clear outliers. Red hatched line' % (
        c, fit4[0] * 356. * 100.)

        #    P.annotate(s = '%.2f per cent / yr (2 last pt)' % (fit2[0]*356.*100.),
        #               xy= (0.1, 0.14), xycoords='axes fraction',
        #               horizontalalignment='left', verticalalignment='center', size = 'x-small')
        #    P.annotate(s = '%.2f per cent / yr (all data)' % (fit[0]*356.*100.),
        #               xy= (0.1, 0.20), xycoords='axes fraction',
        #               horizontalalignment='left', verticalalignment='center', size = 'x-small')
        #    P.annotate(s = '%.2f per cent / yr (excl 2 outl)' % (fit3[0]*356.*100.),
        #               xy= (0.1, 0.08), xycoords='axes fraction',
        #               horizontalalignment='left', verticalalignment='center', size = 'x-small')

        #limit the y axis
        #P.ylim(N.min(data.f_irats[:,i]/avg_r)*0.98, N.max(data.f_irats[:,i]/avg_r)*1.02)
        P.ylim(0.69, 1.28)
        P.xlim(N.min(all_mjd) - 35, N.max(all_mjd) + 55)
        #legend
        if legend: P.legend(shadow=True, fancybox=True)

        #fix labels
        times = []
        for m in ax.get_xticks():
            x = D.datetime(*fromJulian(m)[0:6]).strftime('%d %b\n%Y')
            times.append(x)
        ax.set_xticklabels(times)
        #size
        for tl in ax.get_xticklabels(): tl.set_fontsize(8)

        c += 1

    #this is in a funny place
    P.suptitle('Normalized Relative Efficiency of COS NUV gratings', fontsize=14)

    #Info about gratings to each image:
    P.annotate(s='G185M/G230L @ 2130\AA',
               xy=(0.13, 0.88), xycoords='figure fraction',
               horizontalalignment='left', verticalalignment='center', size='x-small')
    P.annotate(s='G225M/G230L @ 2130\AA',
               xy=(0.551, 0.88), xycoords='figure fraction',
               horizontalalignment='left', verticalalignment='center', size='x-small')
    P.annotate(s='G285M/G230L @ 2490\AA',
               xy=(0.13, 0.447), xycoords='figure fraction',
               horizontalalignment='left', verticalalignment='center', size='x-small')

    if ran[-1] == 7:
        P.annotate(s='G285M/G230L @ 2510\AA',
                   xy=(0.551, 0.447), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='center', size='x-small')
    else:
        P.annotate(s='G285M/G230L @ 2750\AA',
                   xy=(0.551, 0.447), xycoords='figure fraction',
                   horizontalalignment='left', verticalalignment='center', size='x-small')

    P.savefig('NUVGET.ps')
