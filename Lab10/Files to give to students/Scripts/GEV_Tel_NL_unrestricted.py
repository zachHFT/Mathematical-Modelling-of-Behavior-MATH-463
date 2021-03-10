import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
from biogeme.models import lognested
from biogeme.expressions import Beta, DefineVariable, log
from biogeme.models import loglogit

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

# parameters relevant to the nests
N_FLAT = Beta('N_FLAT',1,1,None, 0)
N_MEAS = Beta('N_MEAS',1,1,None, 0)

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
N_FLAT = N_FLAT, [3, 4, 5]
N_MEAS = N_MEAS, [1, 2]

nests = N_FLAT, N_MEAS

# NL
logprob = lognested(V, avail, nests, choice)
biogeme  = bio.BIOGEME(database,logprob)
biogeme.modelName = "GEV_Tel_NL_unrestricted"
results = biogeme.estimate()

# Get the results in a pandas table
pandasResults = results.getEstimatedParameters()
display(pandasResults)
print(f"Nbr of observations: {database.getNumberOfObservations()}")
print(f"LL(0) =    {results.data.initLogLike:.3f}")
print(f"LL(beta) = {results.data.logLike:.3f}")
print(f"rho bar square = {results.data.rhoBarSquare:.3g}")
print(f"Output file: {results.data.htmlFileName}")

# Compare with the logit model
logprob_logit = loglogit(V,avail,choice)
biogeme_logit  = bio.BIOGEME(database,logprob_logit)
biogeme_logit.modelName = "GEV_Tel_NL_logit"
results_logit = biogeme_logit.estimate()

ll_logit = results_logit.data.logLike
rhobar_logit = results_logit.data.rhoBarSquare
ll_nested = results.data.logLike
rhobar_nested = results.data.rhoBarSquare

print(f"LL logit:  {ll_logit:.3f}  rhobar: {rhobar_logit:.3f}  Parameters: {results_logit.data.nparam}")
print(f"LL nested: {ll_nested:.3f}  rhobar: {rhobar_nested:.3f}  Parameters: {results.data.nparam}")
lr = -2 * (ll_logit - ll_nested)
print(f"Likelihood ratio: {lr:.3f}")
