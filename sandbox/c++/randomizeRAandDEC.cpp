#include <iostream>
#include <math.h>
#include <time.h>
using namespace std;

const double PI = atan(1.0) * 4.0;

double deg2rad(double deg)
{
  return (deg * PI / 180.0);
}

double rad2deg(double rad)
{
  return (rad * 180.0 / PI);
}

double* convertSphericalToCartesian(double r, double phi, double theta)
{
  double* out = new double[3];
  out[0] = r * sin(phi) * cos(theta);
  out[1] = r * sin(phi) * sin(theta);
  out[2] = r * cos(phi);
  return out;
}

double* randomUnitSphere()
{
  double* output = new double[2];

  //Random draw within range (0,1)
  double u = (rand()% 10000) / 10000.0;
  double v = (rand()% 10000) / 10000.0;
  //Randomize the spherical angles
  double theta = 2.0 * PI * u;
  double phi = acos(2.0 * v - 1);
  //Set the output to an array
  output[0] = theta;
  output[1] = phi;
  return output;
}

double* RAandDECfromStandardCoordinates(double ra0, double dec0, double X, double Y)
{
  double* res = new double[2];

  /*This CD matrix should be input, but I don't remember
    how to make a matrix in C++ so I just hard coded the
    values for my coordinate selection
   */
  int cd00 = -1;
  int cd01 = 0;
  int cd10 = 0;
  int cd11 = 1;

  double xi = (cd00 * X) + (cd01 * Y);
  double eta = (cd10 * X) + (cd11 * Y);
  double xirad = deg2rad(xi);
  double etarad = deg2rad(eta);
  double ra0rad = deg2rad(ra0);
  double dec0rad = deg2rad(dec0);

  //calculate RA
  double ra = atan2(xirad, cos(dec0rad) - etarad * sin(dec0rad)) + ra0rad;
  //calculate DEC
  double tmp = cos(dec0rad) - etarad * sin(dec0rad);
  double dec = atan2(etarad * cos(dec0rad) + sin(dec0rad), sqrt(pow(tmp, 2) + pow(xirad, 2)));

  //I think one should actually take the module 360
  //ra = rad2deg(ra);
  //ra = mod(ra, 360.0);
  res[0] = rad2deg(ra);
  res[1] = rad2deg(dec);
  return res;
}

int main()
{
  double z;
  double distance;
  double ra_main = 52.904892;
  double dec_main = 27.757082;
  double arcsecToDegree = 0.000277777778;

  /* initialize random seed: */
  srand(time(NULL));
  
  /* Randomize redshift and distace.
     In realworld example these come from the
     light cone. */
  z = (rand() % 10000) / 10000.0 * 5.0; // 4.790
  distance = (rand() % 10000) / 10.0; // 944.30

  /* Randomize the position on a unit sphere */
  double* rdpos = randomUnitSphere();

  /* Here one would calculate the angular diameter
     distance. One should obtain it in the form of
     scale such that we know how many kpc one arcsec
     corresponds to. This can then be converted to degrees */
  float add = 6.46673991039; // I now just fix it to a semi-reasonable value
  double dd = (distance / add) * arcsecToDegree;

  /* Now we use the the distance information as a radius
     when moving to Cartesian coordinates. */
  double* xyz = convertSphericalToCartesian(dd, rdpos[0], rdpos[1]);
  /*  These are now in degrees. */

  /* Poor man's solution would be to apply thse changes to RA and DEC
     directly as follows */
  double newRAbad = ra_main - (xyz[1]/cos(xyz[0]));
  double newDECbad = dec_main + xyz[2];
  /* Here we have made the assumption that x is towards the observer
     z is north and y is east (thus RA increases to "left"). 
     However, this would not give accurate results if we are close to
     the pole, even though we used the declination information when
     deriving the new RA. Thus, a more accurate method should be used. */

  /* Now if we assume that our z and y are Standard Coordinates, 
     i.e., the projection of the RA and DEC of an object onto the 
     tangent plane of the sky. We can now assume that the y coordinate
     is aligned with RA and the z coordinate is aligned with DEC.
     The origin of this system is at the tangent point in the dark
     matter halo. */
  double* radec = RAandDECfromStandardCoordinates(ra_main, dec_main, xyz[1], xyz[2]);
  
  std:cout << "Redshift z = " << z;
  cout << " and the physical distance to the subhalo galaxy = " << distance << " kpc\n";
  cout << "Coordinates of the main galaxy:\n";
  cout << ra_main << " " << dec_main << "\n";
  cout << "Coordinates of the subhalo galaxy with no so accurate technique:\n";
  cout << newRAbad << " " << newDECbad << "\n";
  cout << "Or with the accurate method:\n";
  cout << radec[0] << " " << radec[1] << "\n";
}
