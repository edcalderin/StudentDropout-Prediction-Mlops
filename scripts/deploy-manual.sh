variables="{
    PREDICTIONS_OUTPUT_STREAM=${PREDICTIONS_OUTPUT_STREAM},
    MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI},
    POSTGRES_USER=${POSTGRES_USER},
    POSTGRES_PASSWORD=${POSTGRES_PASSWORD},
    POSTGRES_DB=${POSTGRES_DB}}"

STATE=$(aws lambda get-function --function-name ${LAMBDA_FUNCTION} --region "us-east-2" --query 'Configuration.LastUpdateStatus' --output text)

while [[ "$STATE" == "InProgress" ]]
    do
        echo "Sleep 5 seconds..."
        sleep 5s
        STATE=$(aws lambda get-function --function-name ${LAMBDA_FUNCTION} --region "us-east-2" --query 'Configuration.LastUpdateStatus' --output text)
        echo $STATE
    done

aws lambda update-function-configuration --function-name ${LAMBDA_FUNCTION} --environment "Variables=${variables}"
