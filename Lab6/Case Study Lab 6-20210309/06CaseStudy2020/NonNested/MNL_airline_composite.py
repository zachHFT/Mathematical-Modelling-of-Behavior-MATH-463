# Translated to .py by Meritxell Pacheco
# 2017
# Adapted to PandasBiogeme by Tim Hillel
# Oct 7 2019

import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio

pandas = pd.read_table("airline.dat")
database = db.Database("airline",pandas)
pd.options.display.float_format = '{:.3g}'.format

from headers import *
  
# Choice
chosenAlternative = ( (  BestAlternative_1   *  1  ) + (  BestAlternative_2   *  2  ) ) + (  BestAlternative_3   *  3  )

#Parameters to be estimated
# Arguments:
#   1  Name for report. Typically, the same as the variable
#   2  Starting value
#   3  Lower bound
#   4  Upper bound
#   5  0: estimate the parameter, 1: keep it fixed
Constant1	 = Beta('Constant1',0,None,None,1)
Constant2	 = Beta('Constant2',0,None,None,0)
Constant3	 = Beta('Constant3',0,None,None,0)
Fare	 = Beta('Fare',0,None,None,0)
LogFare	 = Beta('LogFare',0,None,None,0)
Legroom	 = Beta('Legroom',0,None,None,0)
SchedDE	 = Beta('SchedDE',0,None,None,0)
SchedDL	 = Beta('SchedDL',0,None,None,0)
Total_TT1	 = Beta('Total_TT1',0,None,None,0)
Total_TT2	 = Beta('Total_TT2',0,None,None,0)
Total_TT3	 = Beta('Total_TT3',0,None,None,0)

# Define here arithmetic expressions for name that are not directly available from the data
DepartureTimeSensitive  = DefineVariable('DepartureTimeSensitive', q11_DepartureOrArrivalIsImportant   ==  1 , database)
ArrivalTimeSensitive  = DefineVariable('ArrivalTimeSensitive', q11_DepartureOrArrivalIsImportant   ==  2 , database)
Missing  = DefineVariable('Missing',(  q11_DepartureOrArrivalIsImportant   !=  1  ) * (  q11_DepartureOrArrivalIsImportant   !=  2  ), database)
DesiredDepartureTime  = DefineVariable('DesiredDepartureTime',q12_IdealDepTime , database)
DesiredArrivalTime  = DefineVariable('DesiredArrivalTime',q13_IdealArrTime , database)
ScheduledDelay_1  = DefineVariable('ScheduledDelay_1',(  DepartureTimeSensitive   * (  DepartureTimeMins_1   -  DesiredDepartureTime   ) ) + (  ArrivalTimeSensitive   * (  ArrivalTimeMins_1   -  DesiredArrivalTime   ) ), database)
ScheduledDelay_2  = DefineVariable('ScheduledDelay_2',(  DepartureTimeSensitive   * (  DepartureTimeMins_2   -  DesiredDepartureTime   ) ) + (  ArrivalTimeSensitive   * (  ArrivalTimeMins_2   -  DesiredArrivalTime   ) ), database)
ScheduledDelay_3  = DefineVariable('ScheduledDelay_3',(  DepartureTimeSensitive   * (  DepartureTimeMins_3   -  DesiredDepartureTime   ) ) + (  ArrivalTimeSensitive   * (  ArrivalTimeMins_3   -  DesiredArrivalTime   ) ), database)
Opt1_SchedDelayEarly  = DefineVariable('Opt1_SchedDelayEarly',(  -(ScheduledDelay_1 )  * (  ScheduledDelay_1   <  0  ) ) /  60 , database)
Opt2_SchedDelayEarly  = DefineVariable('Opt2_SchedDelayEarly',(  -(ScheduledDelay_2 )  * (  ScheduledDelay_2   <  0  ) ) /  60 , database)
Opt3_SchedDelayEarly  = DefineVariable('Opt3_SchedDelayEarly',(  -(ScheduledDelay_3 )  * (  ScheduledDelay_3   <  0  ) ) /  60 , database)
Opt1_SchedDelayLate  = DefineVariable('Opt1_SchedDelayLate',(  ScheduledDelay_1   * (  ScheduledDelay_1   >  0  ) ) /  60 , database)
Opt2_SchedDelayLate  = DefineVariable('Opt2_SchedDelayLate',(  ScheduledDelay_2   * (  ScheduledDelay_2   >  0  ) ) /  60 , database)
Opt3_SchedDelayLate  = DefineVariable('Opt3_SchedDelayLate',(  ScheduledDelay_3   * (  ScheduledDelay_3   >  0  ) ) /  60 , database)
LogFare_1  = DefineVariable('LogFare_1',log(Fare_1 ), database)
LogFare_2  = DefineVariable('LogFare_2',log(Fare_2 ), database)
LogFare_3  = DefineVariable('LogFare_3',log(Fare_3 ), database)

# Utilities
Opt1 = Constant1 + Fare * Fare_1 + LogFare * LogFare_1 + Legroom * Legroom_1 + SchedDE * Opt1_SchedDelayEarly + SchedDL * Opt1_SchedDelayLate + Total_TT1 * TripTimeHours_1
Opt2 = Constant2 + Fare * Fare_2 + LogFare * LogFare_2 + Legroom * Legroom_2 + SchedDE * Opt2_SchedDelayEarly + SchedDL * Opt2_SchedDelayLate + Total_TT2 * TripTimeHours_2
Opt3 = Constant3 + Fare * Fare_3 + LogFare * LogFare_3 + Legroom * Legroom_3 + SchedDE * Opt3_SchedDelayEarly + SchedDL * Opt3_SchedDelayLate + Total_TT3 * TripTimeHours_3
V = {1: Opt1,2: Opt2,3: Opt3}
av = {1: 1,2: 1,3: 1}

# MNL (Multinomial Logit model), with availability conditions
logprob = bioLogLogit(V,av,chosenAlternative)
biogeme  = bio.BIOGEME(database,logprob)
biogeme.modelName = "MNL_airline_composite"
results = biogeme.estimate()
# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)
print(f"Nbr of observations: {database.getNumberOfObservations()}")
print(f"LL(0) =    {results.data.initLogLike:.3f}")
print(f"LL(beta) = {results.data.logLike:.3f}")
print(f"rho bar square = {results.data.rhoBarSquare:.3g}")
print(f"Output file: {results.data.htmlFileName}")