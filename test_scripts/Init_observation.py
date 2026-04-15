# dev_shell.py
from datetime import datetime
from nowcastingcli.models import Observation

obs = Observation(
    timestamp    = datetime.now(),
    pressure_raw = 1013.25,
    pressure_qnh = 1015.80,
    temperature  = 18.5,
    humidity     = 62.0,
    altitude     = 667.0
)

print(obs)