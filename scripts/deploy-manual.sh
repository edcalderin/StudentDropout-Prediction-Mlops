variables="{
    PREDICTIONS_OUTPUT_STREAM=${PREDICTIONS_OUTPUT_STREAM},
    MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI},
    GRAFANA_DB_USER=${GRAFANA_DB_USER},
    GRAFANA_DB_PASSWORD=${GRAFANA_DB_PASSWORD},
    GRAFANA_DB_NAME=${GRAFANA_DB_NAME}}"

aws lambda update-function-configuration --function-name ${LAMBDA_FUNCTION} --environment "Variables=${variables}"
