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
  int ind = 0;

  /* how to get random number */
  double rnd = openmc::prn(seed);
  /* check which theta will be used depending on the distribution*/
  for(int i = 1; i < 37; i++){
    if(rnd <= angleCdf[i] && rnd > angleCdf[i-1]){

      a = angleCdf[i-1]; b = angleCdf[i];

      scaledR = (rnd -  a)/(b - a);

      interplTheta = angleDist[i-1] + scaledR * (angleDist[i] - angleDist[i-1]);
      theta = std::acos(interplTheta);
      ind = i-1;
      break;
    }
  };  

  double phi = openmc::prn(seed)*2.*M_PI;

  double x = std::cos(theta);
  double y = std::sin(theta)*std::cos(phi);
  double z = std::sin(theta)*std::sin(phi);

  double angle = std::atan(VEC[1]/VEC[0]);  // Assumes the 3rd component is 0. Rotation about z

  // Should remain unit vector
  particle.u[0] = x * std::cos(angle) - y * std::sin(angle);
  particle.u[1] = x * std::sin(angle) + y * std::cos(angle);
  particle.u[2] = z;
  
  double En1 = openmc::prn(seed)*(energyDistHigh[ind]-energyDistLow[ind]) + energyDistLow[ind];

  particle.E = 1.e6 * En1;
  particle.particle = openmc::Particle::Type::neutron;
  particle.wgt = 1.0;
  particle.delayed_group = 0;
  
  return particle;
  }
};


extern "C" std::unique_ptr<Source> openmc_create_source(std::string parameters) {
  return std::unique_ptr<Source> (new Source());
}
