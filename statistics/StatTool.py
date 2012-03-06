"""
This is a simple statistics tool to calculate basic statistics from an input file.

:requires: Scipy
:requires: Numpy

:date: 2008
:author: Sami-Matias Niemi
"""
from optparse import OptionParser
from scipy.stats import *
import numpy as N
import sys


def process_args():
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="output",
        help="Writes data to file named filename. This is optional choice.", metavar="filename")
    parser.add_option("-i", "--input", dest="input",
        help="Reads data from input file called filename", metavar="filename")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
        help="Verbose mode on. This is optional choice.")
    parser.add_option("-s", "--separator", dest="delim",
        help="Sets the data separator/delimiter to given char. This is optional choice.", metavar="separator")
    parser.add_option("-c", "--column1", dest="column1",
        help="The column1 to be processed. Numbering begins from 0.", metavar="number")
    parser.add_option("-x", "--column2", dest="column2",
        help="The column2 to be processed. Numbering begins from 0. This is optional choice!", metavar="number")
    return parser.parse_args()


if __name__ == '__main__':

    (opts, args) = process_args()

    if (opts.input is None):
        print "\nYou did not give input file!\nWill exit now!\n"
        sys.exit()

    if (opts.column1 is None):
        print "You did not give the column!\nWill exit now!\n"
        sys.exit()

    if opts.delim is None: alldata = N.loadtxt(opts.input, delimiter=" ", skiprows=0)
    else: alldata = N.loadtxt(opts.input, delimiter="%s" % opts.delim, skiprows=0)

    if int(opts.column1) != 0: data1 = alldata[:, int(opts.column1)]
    else: data1 = alldata

    if (opts.column2 is None):
        #Only one column statistics here
        count1 = len(data1)
        mean1 = N.mean(data1)
        median1 = N.median(data1)
        mode1 = mode(data1)
        min1 = N.min(data1)
        max1 = N.max(data1)
        sum1 = N.sum(data1)
        gmean1 = gmean(data1)
        hmean1 = hmean(data1)
        kurtosis1 = kurtosis(data1)
        kurtosisp1 = kurtosis(data1, fisher=False)
        kurtosist1 = kurtosistest(data1)
        moment1 = moment(data1)
        normaltest1 = normaltest(data1)
        sem1 = sem(data1)
        skew1 = skew(data1)
        skewt1 = skewtest(data1)
        sos1 = square_of_sums(data1)
        ss1 = ss(data1)
        std1 = std(data1)
        stderr1 = stderr(data1)
        var1 = var(data1)
        moment11 = moment(data1, moment=1)
        moment12 = moment(data1, moment=2)
        moment13 = moment(data1, moment=3)
        per125 = scoreatpercentile(data1, 25)
        per175 = scoreatpercentile(data1, 75)
    else:
        #Two column statistics here
        data2 = alldata[:, int(opts.column2)]
        count1 = len(data1)
        mean1 = N.mean(data1)
        median1 = N.median(data1)
        mode1 = mode(data1)
        min1 = N.min(data1)
        max1 = N.max(data1)
        sum1 = N.sum(data1)
        gmean1 = gmean(data1)
        hmean1 = hmean(data1)
        kurtosis1 = kurtosis(data1)
        kurtosisp1 = kurtosis(data1, fisher=False)
        kurtosist1 = kurtosistest(data1)
        moment11 = moment(data1, moment=1)
        moment12 = moment(data1, moment=2)
        moment13 = moment(data1, moment=3)
        per125 = scoreatpercentile(data1, 25)
        per175 = scoreatpercentile(data1, 75)
        normaltest1 = normaltest(data1)
        sem1 = sem(data1)
        skew1 = skew(data1)
        skewt1 = skewtest(data1)
        sos1 = square_of_sums(data1)
        ss1 = ss(data1)
        std1 = N.std(data1)
        stderr1 = stderr(data1)
        var1 = N.var(data1)
        count2 = len(data2)
        mean2 = N.mean(data2)
        median2 = N.median(data2)
        mode2 = mode(data2)
        min2 = N.min(data2)
        max2 = N.max(data2)
        sum2 = N.sum(data2)
        gmean2 = gmean(data2)
        hmean2 = hmean(data2)
        kurtosis2 = kurtosis(data2)
        kurtosisp2 = kurtosis(data2, fisher=False)
        kurtosist2 = kurtosistest(data2)
        moment2 = moment(data2)
        normaltest2 = normaltest(data2)
        sem2 = sem(data2)
        skew2 = skew(data2)
        skewt2 = skewtest(data2)
        sos2 = square_of_sums(data2)
        ss2 = ss(data2)
        std2 = N.std(data2)
        stderr2 = stderr(data2)
        var2 = N.var(data2)
        moment21 = moment(data2, moment=1)
        moment22 = moment(data2, moment=2)
        moment23 = moment(data2, moment=3)
        per225 = scoreatpercentile(data2, 25)
        per275 = scoreatpercentile(data2, 75)

        #tests between the two datasets
        corrcoef = corrcoef(data1, data2)
        kendalltau = kendalltau(data1, data2)
        ks = ks_2samp(data1, data2)
        mannw = mannwhitneyu(data1, data2)
        pearsonr = pearsonr(data1, data2)
        spearmanr = spearmanr(data1, data2)


    #outputs
    if opts.verbose == True:
        print "The verbose output!"
        if (opts.column2 is None):
            print "Statistics of column %i" % int(opts.column1)
            print "Count: %i" % count1
            print "Mean: %f" % mean1
            print "Harmonic mean: %f" % hmean1
            print "Geometric mean: %f" % gmean1
            print "Median: %f" % median1
            print "Mode (modal value, counts): %f, %i" % (mode1[0], mode1[1])
            print "Min: %f" % min1
            print "Max: %f" % max1
            print "Standard deviation: %f" % std1
            print "Standard deviation error: %f" % stderr1
            print "Variance: %f" % var1
            print "Kurtosis (Fisher): %f" % kurtosis1
            print "Kurtosis (Pearson): %f" % kurtosisp1
            print "Kurtosis test (Z-score, 2-tail Z-probability): %f, %s" % (kurtosist1[0], kurtosist1[1])
            print "Skewness: %f " % skew1
            print "Skewness test (Z-score, 2-tail Z-probability): %f, %s" % (skewt1[0], skewt1[1])
            print "Normality test (Chi**2 score,2-tail probability): %f, %s" % (normaltest1[0], normaltest1[1])
            print "Standard error of mean: %f" % sem1
            print "Sum: %f" % sum1
            print "Square of Sums: %f" % sos1
            print "Sums of Squares: %f" % ss1
            print "1st moment: %f" % moment11
            print "2nd moment: %f" % moment12
            print "3rd moment: %f" % moment13
            print "25th (1st quartile) percentile: %f" % per125
            print "75th (3rd quartile) percentile: %f" % per175
        else:
            print "Statistics of column %i" % int(opts.column1)
            print "Count: %i" % count1
            print "Mean: %f" % mean1
            print "Harmonic mean: %f" % hmean1
            print "Geometric mean: %f" % gmean1
            print "Median: %f" % median1
            print "Mode (modal value, counts): %f, %i" % (mode1[0], mode1[1])
            print "Min: %f" % min1
            print "Max: %f" % max1
            print "Standard deviation: %f" % std1
            print "Standard deviation error: %f" % stderr1
            print "Variance: %f" % var1
            print "Kurtosis (Fisher): %f" % kurtosis1
            print "Kurtosis (Pearson): %f" % kurtosisp1
            print "Kurtosis test (Z-score, 2-tail Z-probability): %f, %s" % (kurtosist1[0], kurtosist1[1])
            print "Skewness: %f " % skew1
            print "Skewness test (Z-score, 2-tail Z-probability): %f, %s" % (skewt1[0], skewt1[1])
            print "Normality test (Chi**2 score,2-tail probability): %f, %s" % (normaltest1[0], normaltest1[1])
            print "Standard error of mean: %f" % sem1
            print "Sum: %f" % sum1
            print "Square of Sums: %f" % sos1
            print "Sums of Squares: %f" % ss1
            print "1st moment: %f" % moment11
            print "2nd moment: %f" % moment12
            print "3rd moment: %f" % moment13
            print "25th (1st quartile) percentile: %f" % per125
            print "75th (3rd quartile) percentile: %f" % per175
            print
            print "Statistics of column %i" % int(opts.column2)
            print "Count: %i" % count2
            print "Mean: %f" % mean2
            print "Harmonic mean: %f" % hmean2
            print "Geometric mean: %f" % gmean2
            print "Median: %f" % median2
            print "Mode (modal value, counts): %f, %i" % (mode2[0], mode2[1])
            print "Min: %f" % min2
            print "Max: %f" % max2
            print "Standard deviation: %f" % std2
            print "Standard deviation error: %f" % stderr2
            print "Variance: %f" % var2
            print "Kurtosis (Fisher): %f" % kurtosis2
            print "Kurtosis (Pearson): %f" % kurtosisp2
            print "Kurtosis test (Z-score, 2-tail Z-probability): %f, %s" % (kurtosist2[0], kurtosist2[1])
            print "Skewness: %f " % skew2
            print "Skewness test (Z-score, 2-tail Z-probability): %f, %s" % (skewt2[0], skewt1[1])
            print "Normality test (Chi**2 score,2-tail probability): %f, %s" % (normaltest2[0], normaltest2[1])
            print "Standard error of mean: %f" % sem2
            print "Sum: %f" % sum2
            print "Square of Sums: %f" % sos2
            print "Sum of Squares: %f" % ss2
            print "1st moment: %f" % moment21
            print "2nd moment: %f" % moment22
            print "3rd moment: %f" % moment23
            print "25th (1st quartile) percentile: %f" % per225
            print "75th (3rd quartile) percentile: %f" % per275
            print "Statistical tests between columns %i and %i" % (int(opts.column1), int(opts.column2))
            print "Correlation Coefficients:\n %f, %f, %f, %f" % (
            corrcoef[0, 0], corrcoef[0, 1], corrcoef[1, 0], corrcoef[1, 1])
            print "Kendall's tau (Kendall's tau, two-tailed p-value):\n %f, %s" % (kendalltau[0], kendalltau[1])
            print "Kolmogorov-Smirnov (KS D-value, p-value):\n %f, %s" % (ks[0], ks[1])
            print "Mann-Whitney U (u-statistic, one-tailed p-value (i.e., p(z(U)))):\n %f, %s" % (mannw[0], mannw[1])
            print "Pearson Correlation Coefficient (Pearson's correlation coefficient, 2-tailed p-value):\n %f, %s" % (
            pearsonr[0], pearsonr[1])
            print "Spearman rank-order Correlation Coefficient (Spearman correlation coefficient, 2-tailed p-value):\n %f, %s" % (
            spearmanr[0], spearmanr[1])

    if (opts.output is not None):
        file = open(opts.output, 'w')
        if (opts.column2 is None):
            file.write("Statistics of column %i \n" % int(opts.column1))
            file.write("Count: %i \n" % count1)
            file.write("Mean: %f \n" % mean1)
            file.write("Harmonic mean: %f \n" % hmean1)
            file.write("Geometric mean: %f \n" % gmean1)
            file.write("Median: %f \n" % median1)
            file.write("Mode (modal value, counts): %f, %i \n" % (mode1[0], mode1[1]))
            file.write("Min: %f \n" % min1)
            file.write("Max: %f \n" % max1)
            file.write("Standard deviation: %f \n" % std1)
            file.write("Standard deviation error: %f \n" % stderr1)
            file.write("Variance: %f \n" % var1)
            file.write("Kurtosis (Fisher): %f \n" % kurtosis1)
            file.write("Kurtosis (Pearson): %f \n" % kurtosisp1)
            file.write("Kurtosis test (Z-score, 2-tail Z-probability): %f, %s \n" % (kurtosist1[0], kurtosist1[1]))
            file.write("Skewness: %f \n" % skew1)
            file.write("Skewness test (Z-score, 2-tail Z-probability): %f, %s \n" % (skewt1[0], skewt1[1]))
            file.write("Normality test (Chi**2 score,2-tail probability): %f, %s \n" % (normaltest1[0], normaltest1[1]))
            file.write("Standard error of mean: %f \n" % sem1)
            file.write("Sum: %f \n" % sum1)
            file.write("Square of Sums: %f \n" % sos1)
            file.write("Sums of Squares: %f \n" % ss1)
            file.write("1st moment: %f \n" % moment11)
            file.write("2nd moment: %f \n" % moment12)
            file.write("3rd moment: %f \n" % moment13)
            file.write("25th (1st quartile) percentile: %f\n" % per125)
            file.write("75th (3rd quartile) percentile: %f\n" % per175)
        else:
            file.write("Statistics of column %i \n" % int(opts.column1))
            file.write("Count: %i \n" % count1)
            file.write("Mean: %f \n" % mean1)
            file.write("Harmonic mean: %f \n" % hmean1)
            file.write("Geometric mean: %f \n" % gmean1)
            file.write("Median: %f \n" % median1)
            file.write("Mode (modal value, counts): %f, %i \n" % (mode1[0], mode1[1]))
            file.write("Min: %f \n" % min1)
            file.write("Max: %f \n" % max1)
            file.write("Standard deviation: %f \n" % std1)
            file.write("Standard deviation error: %f \n" % stderr1)
            file.write("Variance: %f \n" % var1)
            file.write("Kurtosis (Fisher): %f \n" % kurtosis1)
            file.write("Kurtosis (Pearson): %f \n" % kurtosisp1)
            file.write("Kurtosis test (Z-score, 2-tail Z-probability): %f, %s \n" % (kurtosist1[0], kurtosist1[1]))
            file.write("Skewness: %f \n" % skew1)
            file.write("Skewness test (Z-score, 2-tail Z-probability): %f, %s \n" % (skewt1[0], skewt1[1]))
            file.write("Normality test (Chi**2 score,2-tail probability): %f, %s \n" % (normaltest1[0], normaltest1[1]))
            file.write("Standard error of mean: %f \n" % sem1)
            file.write("Sum: %f \n" % sum1)
            file.write("Square of Sums: %f \n" % sos1)
            file.write("Sums of Squares: %f \n" % ss1)
            file.write("1st moment: %f \n" % moment11)
            file.write("2nd moment: %f \n" % moment12)
            file.write("3rd moment: %f \n" % moment13)
            file.write("25th (1st quartile) percentile: %f\n" % per125)
            file.write("75th (3rd quartile) percentile: %f\n" % per175)
            file.write("\n")
            file.write("Statistics of column %i \n" % int(opts.column2))
            file.write("Count: %i \n" % count2)
            file.write("Mean: %f \n" % mean2)
            file.write("Harmonic mean: %f \n" % hmean2)
            file.write("Geometric mean: %f \n" % gmean2)
            file.write("Median: %f \n" % median2)
            file.write("Mode (modal value, counts): %f, %i \n" % (mode2[0], mode2[1]))
            file.write("Min: %f \n" % min2)
            file.write("Max: %f \n" % max2)
            file.write("Standard deviation: %f \n" % std2)
            file.write("Standard deviation error: %f \n" % stderr2)
            file.write("Variance: %f \n" % var2)
            file.write("Kurtosis (Fisher): %f \n" % kurtosis2)
            file.write("Kurtosis (Pearson): %f \n" % kurtosisp2)
            file.write("Kurtosis test (Z-score, 2-tail Z-probability): %f, %s \n" % (kurtosist2[0], kurtosist2[1]))
            file.write("Skewness: %f \n" % skew2)
            file.write("Skewness test (Z-score, 2-tail Z-probability): %f, %s \n" % (skewt2[0], skewt1[1]))
            file.write("Normality test (Chi**2 score,2-tail probability): %f, %s \n" % (normaltest2[0], normaltest2[1]))
            file.write("Standard error of mean: %f \n" % sem2)
            file.write("Sum: %f \n" % sum2)
            file.write("Square of Sums: %f \n" % sos2)
            file.write("Sum of Squares: %f \n" % ss2)
            file.write("1st moment: %f \n" % moment21)
            file.write("2nd moment: %f \n" % moment22)
            file.write("3rd moment: %f \n" % moment23)
            file.write("25th (1st quartile) percentile: %f\n" % per225)
            file.write("75th (3rd quartile) percentile: %f\n" % per275)
            file.write("Statistical tests between columns %i and %i \n" % (int(opts.column1), int(opts.column2)))
            file.write("Correlation Coefficients:\n %f, %f, %f, %f \n" % (
            corrcoef[0, 0], corrcoef[0, 1], corrcoef[1, 0], corrcoef[1, 1]))
            file.write(
                "Kendall's tau (Kendall's tau, two-tailed p-value):\n %f, %s \n" % (kendalltau[0], kendalltau[1]))
            file.write("Kolmogorov-Smirnov (KS D-value, p-value):\n %f, %s \n" % (ks[0], ks[1]))
            file.write(
                "Mann-Whitney U (u-statistic, one-tailed p-value (i.e., p(z(U)))):\n %f, %s \n" % (mannw[0], mannw[1]))
            file.write(
                "Pearson Correlation Coefficient (Pearson's correlation coefficient, 2-tailed p-value):\n %f, %s \n" % (
                pearsonr[0], pearsonr[1]))
            file.write(
                "Spearman rank-order Correlation Coefficient (Spearman correlation coefficient, 2-tailed p-value):\n %f, %s \n" % (
                spearmanr[0], spearmanr[1]))
        file.flush()
        file.close()
        #END