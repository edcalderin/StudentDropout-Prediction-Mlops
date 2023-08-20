from typing import Any, Dict, List

from pydantic import BaseModel


class ArgsMLFlowExperiment(BaseModel):
    mlflow: Any
    hyperparams: Dict[str, Any]
    features: Dict[str, List[str]]
    log_artifacts: bool = False
