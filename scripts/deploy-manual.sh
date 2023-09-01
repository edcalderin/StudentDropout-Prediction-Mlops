variables="{
    PREDICTIONS_OUTPUT_STREAM=${PREDICTIONS_OUTPUT_STREAM},
    MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI},
    POSTGRES_USER=${POSTGRES_USER},
    POSTGRES_PASSWORD=${POSTGRES_PASSWORD},
    POSTGRES_DB=${POSTGRES_DB}}"

aws lambda update-function-configuration --function-name ${LAMBDA_FUNCTION} --environment "Variables=${variables}"
