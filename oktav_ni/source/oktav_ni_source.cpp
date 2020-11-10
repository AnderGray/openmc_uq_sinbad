#include "oktav_ni_source.hpp"
#include <cmath>


/*
  Source distribution follows the SINBAD documentation. Cosine and energy sampled following
  angle and energy distribution. Energy is then shifted depending on cosine.

                                                  A. Gray, Uni of Liverpool
*/

class Source : public openmc::CustomSource
{
  openmc::Particle::Bank sample(uint64_t* seed) {

  /* Particle coordinates, direction, energy, weight and time are set  */
  /* in the following for monodirectional, monoenergetic point source. */
  /* The number of parameters entered after "si" is stored in variable */
  /* np, and the values in array params. Notice that in C the indexing */
  /* is zero-based, so the first given parameter is params[0], and the */
  /* last parameter is params[np - 1]. Other variables defined in the  */
  /* source card are:                                                  */
  /*                                                                   */
  /* x0, y0, z0  -- Point source coordinates (values following "sp")   */
  /* xmin, xmax  -- Boundaries on the x-axis (values following "sx")   */
  /* ymin, ymax  -- Boundaries on the y-axis (values following "sy")   */
  /* zmin, zmax  -- Boundaries on the z-axis (values following "sz")   */
  /* u0, v0, w0  -- Direction cosines (values following "sd")          */
  /* E0          -- Source energy (value following "se")               */
  /*                                                                   */
  /* The values of x, y, z, u, v, w, E wgt and t, passed as function   */
  /* arguments are initially set based on the other entries in the     */
  /* source card. This subroutine is called after all other routines.  */
  /*                                                                   */
  /* Notice that altough these values can be used in the subroutine,   */
  /* they are not automatically assigned to the corresponding          */
  /* variables of the source particle.                                 */
  
  openmc::Particle::Bank particle;
  
  /* you will put your position as a parameter when you will call the source*/
  particle.r.x = POS[0];
  particle.r.y = POS[1];
  particle.r.z = POS[2];

  double theta = 0;
  double scaledR = 0;
  double interplTheta = 0;
  double a = 0;
  double b = 0;

  /* how to get random number */
  double rnd = openmc::prn(seed);
  /* check which theta will be used depending on the distribution*/
  for(int i = 1; i < 8; i++){
    if(rnd <= angleDistribution[i][1] && rnd > angleDistribution[i-1][1]){

      a = angleDistribution[i-1][1]; b = angleDistribution[i][1];

      scaledR = (rnd -  a)/(b - a);

      interplTheta = angleDistribution[i-1][0] + scaledR * (angleDistribution[i][0] - angleDistribution[i-1][0]);
      theta = std::acos(interplTheta);
      break;
    }
  };  

  double phi = openmc::prn(seed)*2.*M_PI;

  particle.u[0] = std::sin(theta)*std::cos(phi);
  particle.u[1] = std::cos(theta);
  particle.u[2] = std::sin(theta)*std::sin(phi);
    
  rnd = openmc::prn(seed);
  for(int i = 1; i < 83; i++){
    if(rnd <= energyCdf[0][i] && rnd > energyCdf[0][i-1]){
      /* energy between the lower and upper value sampled randomly*/
      double En1 = openmc::prn(seed)*(energyDistributionHigh[0][i-1]-energyDistributionLow[0][i-1]) + energyDistributionLow[0][i-1];
      particle.E = 1.e6 * En1 * (14.1 + 0.7 * interplTheta )/14.8;      // Angle-energy shifting. Found in Documentation 3.a
      break;
    }
  }

  particle.particle = openmc::Particle::Type::neutron;
  particle.wgt = 1.0;
  particle.delayed_group = 0;
  
  return particle;
  }
};


extern "C" std::unique_ptr<Source> openmc_create_source(std::string parameters) {
  return std::unique_ptr<Source> (new Source());
}
