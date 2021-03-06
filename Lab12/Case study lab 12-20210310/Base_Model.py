# Translated to .py by Meritxell Pacheco (December 2016)
# Adapted to PandasBiogeme by Nicola Ortelli (November 2019)
# Adapted to new biogeme interface by Tim Hillel (October 2020)

import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
from biogeme.optimization import newtonTrustRegionForBiogeme
from biogeme.expressions import Beta, DefineVariable
from biogeme.models import loglogit

df = pd.read_csv("swissmetro.dat", sep = '\t')
database = db.Database("swissmetro", df)

globals().update(database.variables)

# Exclude data
exclude = (( PURPOSE != 1 ) * ( PURPOSE != 3 ) + ( CHOICE == 0 )) > 0
database.remove(exclude)

# Parameters to be estimated
ASC_TRAIN = Beta('ASC_TRAIN', 0, None, None, 1)
ASC_SM    = Beta('ASC_SM',    0, None, None, 0)
ASC_CAR   = Beta('ASC_CAR',   0, None, None, 0)

B_TIME = Beta('B_TIME', 0, None, None, 0)
B_COST = Beta('B_COST', 0, None, None, 0)
B_HE   = Beta('B_HE',   0, None, None, 0)

# Definition of new variables
TRAIN_COST = DefineVariable('TRAIN_COST', TRAIN_CO * ( GA == 0 ), database)
SM_COST    = DefineVariable('SM_COST', SM_CO * ( GA == 0 ), database)

# Utilities
V_TRAIN = ASC_TRAIN + B_TIME * TRAIN_TT + B_COST * TRAIN_COST + B_HE * TRAIN_HE
V_SM    = ASC_SM    + B_TIME * SM_TT    + B_COST * SM_COST    + B_HE * SM_HE
V_CAR   = ASC_CAR   + B_TIME * CAR_TT   + B_COST * CAR_CO

V = {1: V_TRAIN, 2: V_SM, 3: V_CAR}
av = {1: TRAIN_AV, 2: SM_AV, 3: CAR_AV}

# Choice model estimation
logprob = loglogit(V, av, CHOICE)
biogeme = bio.BIOGEME(database, logprob)
biogeme.modelName = "Base Model"
results = biogeme.estimate(algorithm = newtonTrustRegionForBiogeme)

# Results
pandasResults = results.getEstimatedParameters()
print(pandasResults)
print(f"Nbr of observations: {database.getNumberOfObservations()}")
print(f"LL(0) = {results.data.initLogLike:.3f}")
print(f"LL(beta) = {results.data.logLike:.3f}")
print(f"rho bar square = {results.data.rhoBarSquare:.3g}")
print(f"Output file: {results.data.htmlFileName}")