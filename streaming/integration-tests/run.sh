#!bin/sh

cd "$(dirname "$0")"

if [ "${LOCAL_IMAGE_NAME}" == "" ]; then
    LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
    export LOCAL_IMAGE_NAME=stream-student-dropout-classifier:$LOCAL_TAG
    echo "LOCAL_IMAGE_NAME is not set, building a new image with tag ${LOCAL_TAG}"
    docker build -t $LOCAL_IMAGE_NAME ../..
else
    echo "no need to build ${LOCAL_IMAGE_NAME}"
fi

export PREDICTIONS_OUTPUT_STREAM=student-dropout-output-stream
export POSTGRES_USER=user
export POSTGRES_PASSWORD=123
export POSTGRES_DB=db_test

docker-compose up -d

sleep 15

aws kinesis create-stream \
    --endpoint-url http://localhost:4566 \
    --stream-name ${PREDICTIONS_OUTPUT_STREAM} \
    --shard-count 1

sleep 3

# Test for Docker
echo "Testing docker..."
pipenv run python test_docker.py

ERROR_CODE=$? #Catching the error

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE} # Stop the current execution
fi
echo "Docker tested successfully!"

# Test for Postgres
echo "Testing Postgres DB..."
pipenv run python test_postgres.py

ERROR_CODE=$? #Catching the error

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE} # Stop the current execution
fi
echo "Postgres tested successfully!"

# Same for kinesis
echo "Testing kinesis..."
pipenv run python test_kinesis.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi
echo "Kinesis tested successfully!"

# If previous tests fullfilled successfully then:
echo "All good!"
docker-compose down
exit ${ERROR_CODE}
