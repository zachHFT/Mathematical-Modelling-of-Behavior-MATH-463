# Translated to .py by Meritxell Pacheco
# 2017
# Adapted to PandasBiogeme by Michel Bierlaire
# Sun Oct 21 23:18:39 2018
# Revised by Nicola Ortelli
# Sept 2020

import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
from biogeme.expressions import Beta, DefineVariable
from biogeme.models import loglogit

pandas = pd.read_csv("airline.dat", sep = '\t')
database = db.Database("airline", pandas)
pd.options.display.float_format = '{:.3g}'.format

globals().update(database.variables)

# Exclude
exclude = (ArrivalTimeHours_1 == -1)
database.remove(exclude)
  
# Choice
chosenAlternative = (BestAlternative_1 * 1) + (BestAlternative_2 * 2) + (BestAlternative_3 * 3)

# Parameters to be estimated
# Arguments:
#   1  Name for report. Typically, the same as the variable
#   2  Starting value
#   3  Lower bound
#   4  Upper bound
#   5  0: estimate the parameter, 1: keep it fixed
Constant1 = Beta('Constant1', 0, None, None, 1)
Constant2 = Beta('Constant2', 0, None, None, 0)
Constant3 = Beta('Constant3', 0, None, None, 0)
Fare = Beta('Fare', 0, None, None, 0)
Legroom = Beta('Legroom', 0, None, None, 0)
SchedDE = Beta('SchedDE', 0, None, None, 0)
SchedDL = Beta('SchedDL', 0, None, None, 0)
Total_TT1 = Beta('Total_TT1', 0, None, None, 0)
Total_TT2 = Beta('Total_TT2', 0, None, None, 0)
Total_TT3 = Beta('Total_TT3', 0, None, None, 0)

# Define here arithmetic expressions for variables that are not directly available from the data
DepTimeSensitive  = DefineVariable('DepTimeSensitive', q11_DepartureOrArrivalIsImportant == 1, database)
ArrTimeSensitive  = DefineVariable('ArrTimeSensitive', q11_DepartureOrArrivalIsImportant == 2, database)
DesiredDepTime  = DefineVariable('DesiredDepTime', q12_IdealDepTime, database)
DesiredArrTime  = DefineVariable('DesiredArrTime', q13_IdealArrTime, database)
SchedDelay_1  = DefineVariable('SchedDelay_1', (DepTimeSensitive * (DepartureTimeMins_1 - DesiredDepTime)) + (ArrTimeSensitive * (ArrivalTimeMins_1 - DesiredArrTime)), database)
SchedDelay_2  = DefineVariable('SchedDelay_2', (DepTimeSensitive * (DepartureTimeMins_2 - DesiredDepTime)) + (ArrTimeSensitive * (ArrivalTimeMins_2 - DesiredArrTime)), database)
SchedDelay_3  = DefineVariable('SchedDelay_3', (DepTimeSensitive * (DepartureTimeMins_3 - DesiredDepTime)) + (ArrTimeSensitive * (ArrivalTimeMins_3 - DesiredArrTime)), database)
Opt1_SchedDelayEarly  = DefineVariable('Opt1_SchedDelayEarly', (-SchedDelay_1 * (SchedDelay_1 < 0)) / 60, database)
Opt2_SchedDelayEarly  = DefineVariable('Opt2_SchedDelayEarly', (-SchedDelay_2 * (SchedDelay_2 < 0)) / 60, database)
Opt3_SchedDelayEarly  = DefineVariable('Opt3_SchedDelayEarly', (-SchedDelay_3 * (SchedDelay_3 < 0)) / 60, database)
Opt1_SchedDelayLate  = DefineVariable('Opt1_SchedDelayLate', (SchedDelay_1 * (SchedDelay_1 > 0)) / 60, database)
Opt2_SchedDelayLate  = DefineVariable('Opt2_SchedDelayLate', (SchedDelay_2 * (SchedDelay_2 > 0)) / 60, database)
Opt3_SchedDelayLate  = DefineVariable('Opt3_SchedDelayLate', (SchedDelay_3 * (SchedDelay_3 > 0)) / 60, database)

# Utilities
Opt1 = Constant1 + Fare * Fare_1 + Legroom * Legroom_1 + SchedDE * Opt1_SchedDelayEarly + SchedDL * Opt1_SchedDelayLate + Total_TT1 * TripTimeHours_1
Opt2 = Constant2 + Fare * Fare_2 + Legroom * Legroom_2 + SchedDE * Opt2_SchedDelayEarly + SchedDL * Opt2_SchedDelayLate + Total_TT2 * TripTimeHours_2
Opt3 = Constant3 + Fare * Fare_3 + Legroom * Legroom_3 + SchedDE * Opt3_SchedDelayEarly + SchedDL * Opt3_SchedDelayLate + Total_TT3 * TripTimeHours_3
V = {1: Opt1, 2: Opt2, 3: Opt3}
av = {1: 1, 2: 1, 3: 1}

# The choice model is a logit, with availability conditions
logprob = loglogit(V, av, chosenAlternative)
biogeme = bio.BIOGEME(database, logprob)
biogeme.modelName = "logit_airline_specific"
results = biogeme.estimate()

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
print(pandasResults)
print(f"Nbr of observations: {database.getNumberOfObservations()}")
print(f"LL(0) = {results.data.initLogLike:.3f}")
print(f"LL(beta) = {results.data.logLike:.3f}")
print(f"rho bar square = {results.data.rhoBarSquare:.3g}")
print(f"Output file: {results.data.htmlFileName}")