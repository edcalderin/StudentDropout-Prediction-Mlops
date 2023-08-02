#!bin/sh

cd "$(dirname "$0")"

if [ "${LOCAL_IMAGE_NAME}" == "" ]; then
    LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
    export LOCAL_IMAGE_NAME=stream-model-duration:$LOCAL_TAG
    echo "LOCAL_IMAGE_NAME is not set, building a new image with tag ${LOCAL_TAG}"
    docker build -t $LOCAL_IMAGE_NAME ..
else
    echo "no need to build ${LOCAL_IMAGE_NAME}"
fi

export PREDICTIONS_STREAM_NAME=ride_predictions

docker-compose up -d

sleep 1

aws kinesis create-stream \
    --endpoint-url http://localhost:4566 \
    --stream-name ${PREDICTIONS_STREAM_NAME} \
    --shard-count 1

# Test for Docker

pipenv run python test_docker.py

ERROR_CODE=$? #Catching the error

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE} # Stop the current execution
fi

# Same for kinesis

pipenv run python test_kinesis.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi

# If previous tests fullfilled successfully then:
docker-compose down
exit ${ERROR_CODE}
echo "All good!"
