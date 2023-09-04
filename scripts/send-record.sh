KINESIS_INPUT_STREAM=student-dropout-input-stream

aws kinesis put-record \
        --stream-name $KINESIS_INPUT_STREAM \
        --partition-key 1 \
        --data '{
                "student_features" : {
                        "GDP": 1.74,
                        "Inflation rate": 1.4,
                        "Tuition fees up to date": 1,
                        "Scholarship holder": 0,
                        "Curricular units 1st sem (approved)": 5,
                        "Curricular units 1st sem (enrolled)": 6,
                        "Curricular units 2nd sem (approved)": 5
                },
                "student_id": 256
                }' \
        --cli-binary-format raw-in-base64-out
