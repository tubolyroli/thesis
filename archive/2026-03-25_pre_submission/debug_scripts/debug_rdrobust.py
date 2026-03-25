import pandas as pd
import numpy as np
from rdrobust import rdrobust

# Create dummy data
x = np.random.uniform(-1, 1, 100)
y = 0.5 * (x >= 0) + 0.2 * x + np.random.normal(0, 0.1, 100)

res = rdrobust(y, x, c=0)
print("Type of res:", type(res))
print("Attributes of res:", dir(res))
if hasattr(res, 'coef'):
    print("coef:\n", res.coef)
if hasattr(res, 'se'):
    print("se:\n", res.se)
if hasattr(res, 'pv'):
    print("pv:\n", res.pv)
