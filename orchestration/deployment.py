from prefect.deployments.deployments import Deployment

from orchestration.train import train_flow
from orchestration.common import params

deployment = Deployment.build_from_flow(
    name=params['PREFECT_DEPLOYMENT_NAME'], flow=train_flow
)

if __name__ == '__main__':
    deployment.apply()
