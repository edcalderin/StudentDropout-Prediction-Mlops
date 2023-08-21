from prefect.deployments.deployments import Deployment

from config.params import params
from orchestration.train import train_flow


def apply_deploy():
    deployment = Deployment.build_from_flow(
        name=params['prefect_deployment_name'], flow=train_flow
    )
    deployment.apply()


if __name__ == '__main__':
    apply_deploy()
