from prefect.deployments.deployments import Deployment

from orchestration.train import train_flow
from orchestration.common import params

deployment = Deployment.build_from_flow(
    name=params['prefect_deployment_name'], flow=train_flow
)

if __name__ == '__main__':
    deployment.apply()
