import pymc
import testmodel
import matplotlib.pyplot as plt

#load the testmodel
R = pymc.MCMC(testmodel, db='pickle', dbname='test.pickle')

# populate and run it
R.sample(iter=100000, burn=10000, thin=2)
print 'a:', R.a.stats()
print 'b:', R.b.stats()
print 'c:', R.c.stats()
print 'd:', R.d.stats()

#generate plots
pymc.Matplot.plot(R)

#close MCMC to write database
R.db.close()

#generate a comparison plot
fig = plt.figure()
plt.errorbar(testmodel.x, testmodel.f, yerr=testmodel.noise, label='data', ls='None', marker='D')
plt.plot(testmodel.x,
         R.a.stats()['quantiles'][50]*testmodel.x**2 \
         + R.b.stats()['quantiles'][50]*testmodel.x \
         + R.c.stats()['quantiles'][50] \
         + R.d.stats()['quantiles'][50],
         'g-',
         label='Bayesian model fitting')
plt.plot(testmodel.x,
         testmodel.z[0]*testmodel.x**2 + testmodel.z[1]*testmodel.x + testmodel.z[2],
         'r--',
         label=r'$\chi^{2}$ minimization')

plt.legend()
plt.savefig('test.pdf')