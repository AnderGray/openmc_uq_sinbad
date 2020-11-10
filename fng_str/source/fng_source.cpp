#include "fng_source.hpp"

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
  particle.r.x = 0.;
  particle.r.y = 0.001;
  particle.r.z = 0.;

  double theta = 0;
  int index = 0;
  double scaledR = 0;
  double interplTheta = 0;
  double a = 0;
  double b = 0;

  /* how to get random number */
  double rnd = openmc::prn(seed);
  /* check which theta will be used depending on the distribution*/
  for(int i = 1; i < 40; i++){
    if(rnd <= angleDistribution[i][1] && rnd > angleDistribution[i-1][1]){

      a = angleDistribution[i-1][1]; b = angleDistribution[i][1];
      scaledR = (rnd -  a)/(b - a);
      interplTheta = angleDistribution[i-1][0] + scaledR * (angleDistribution[i][0] - angleDistribution[i-1][0]);
      theta = std::acos(interplTheta);
      index = i;
      break;
    }
  }  

  double phi = openmc::prn(seed)*2.*M_PI;

  particle.u[0] = std::sin(theta)*std::cos(phi);
  particle.u[1] = std::cos(theta);
  particle.u[2] = std::sin(theta)*std::sin(phi);
    
  /* puting your position and direction so that program can use it - pointers in C - x,y,z on cylnder*/
  double angle = openmc::prn(seed)*2.*M_PI;
  double r = 0.7*std::sqrt(openmc::prn(seed));
  particle.r.x += r*std::cos(angle);
  particle.r.y += openmc::prn(seed)*0.001;
  particle.r.z += r*std::sin(angle);

  /*  Here you need to define the energy of particle depending on the sampled direction */
  /* new randon number for energy distribution*/
  rnd = openmc::prn(seed);
  for(int i = 1; i < 127; i++){
    if(rnd <= energyDistibution[i][index] && rnd > energyDistibution[i-1][index]){
      /* energy between the lower and upper value sampled randomly*/
      particle.E = 1.e6*openmc::prn(seed)*(energyDistibution[i][0]-energyDistibution[i-1][0])+energyDistibution[i-1][0] * 1.e6;
      break;
    }
  }

  particle.particle = openmc::Particle::Type::neutron;
  particle.wgt = 1.0;
  particle.delayed_group = 0;
  
  return particle;
  }
};

//
extern "C" std::unique_ptr<Source> openmc_create_source(std::string parameters) {
  return std::unique_ptr<Source> (new Source());
}
