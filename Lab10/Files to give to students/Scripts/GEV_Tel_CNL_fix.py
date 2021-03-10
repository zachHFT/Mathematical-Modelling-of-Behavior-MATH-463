import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
from biogeme.models import logcnl_avail
from biogeme.expressions import Beta, DefineVariable, log

pandas = pd.read_table("telephone.dat")
database = db.Database("telephone",pandas)
pd.options.display.float_format = '{:.3g}'.format

globals().update(database.variables)

#Parameters to be estimated
# Arguments:
#   1  Name for report. Typically, the same as the variable
#   2  Starting value
#   3  Lower bound
#   4  Upper bound
#   5  0: estimate the parameter, 1: keep it fixed
ASC_BM	 = Beta('ASC_BM',0,None,None,0)
ASC_EF	 = Beta('ASC_EF',0,None,None,0)
ASC_LF	 = Beta('ASC_LF',0,None,None,0)
ASC_MF	 = Beta('ASC_MF',0,None,None,0)
ASC_SM	 = Beta('ASC_SM',0,None,None,1)
B_COST	 = Beta('B_COST',0,None,None,0)
#
# parameters relevant to the nests
N_FLAT = Beta('N_FLAT',2.16,None,None,1)
N_MEAS = Beta('N_MEAS',2.16,None,None,1)
#
a_FLAT_LF = Beta('a_FLAT_LF',0.5,0,1,1)
a_MEAS_LF = Beta('a_MEAS_LF',0.5,0,1,1)
a_FLAT_EF = Beta('a_FLAT_EF',1,0,1,1)
a_FLAT_MF = Beta('a_FLAT_MF',1,0,1,1)
a_MEAS_BM = Beta('a_MEAS_BM',1,0,1,1)
a_MEAS_SM = Beta('a_MEAS_SM',1,0,1,1)

# Define here arithmetic expressions for names that are not directly
# available from the data

logcostBM  = DefineVariable('logcostBM', log(cost1),database)
logcostSM  = DefineVariable('logcostSM', log(cost2),database)
logcostLF  = DefineVariable('logcostLF', log(cost3),database)
logcostEF  = DefineVariable('logcostEF', log(cost4),database)
logcostMF  = DefineVariable('logcostMF', log(cost5),database)

#Utilities
V_BM = ASC_BM + B_COST * logcostBM
V_SM = ASC_SM + B_COST * logcostSM
V_LF = ASC_LF + B_COST * logcostLF
V_EF = ASC_EF + B_COST * logcostEF
V_MF = ASC_MF + B_COST * logcostMF

V = {1: V_BM, 2: V_SM, 3: V_LF, 4: V_EF, 5: V_MF}
avail = {1: avail1, 2: avail2, 3: avail3, 4: avail4, 5: avail5}

#Definitions of nests
alpha_N_FLAT = {1: 0, 2: 0, 3: a_FLAT_LF, 4: a_FLAT_EF, 5: a_FLAT_MF}
alpha_N_MEAS = {1: a_MEAS_BM, 2: a_MEAS_SM, 3: a_MEAS_LF, 4: 0, 5: 0}

nest_N_FLAT = N_FLAT, alpha_N_FLAT
nest_N_MEAS = N_MEAS, alpha_N_MEAS

nests = nest_N_FLAT, nest_N_MEAS

# CNL with fixed alphas
logprob = logcnl_avail(V, avail, nests, choice)
biogeme  = bio.BIOGEME(database,logprob)
biogeme.modelName = "GEV_Tel_CNL_fix"
results = biogeme.estimate()

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
display(pandasResults)
print(f"Nbr of observations: {database.getNumberOfObservations()}")
print(f"LL(0) =    {results.data.initLogLike:.3f}")
print(f"LL(beta) = {results.data.logLike:.3f}")
print(f"rho bar square = {results.data.rhoBarSquare:.3g}")
print(f"Output file: {results.data.htmlFileName}")
