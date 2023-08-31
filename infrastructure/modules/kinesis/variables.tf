variable "stream_name" {
    type = string
    description = "Kinesis input stream"
}

variable "shard_count" {
    type = number
}

variable "retention_period" {
    type = number
}

variable "shard_level_metrics" {
    type = list(string)
    default = [
        "IncomingBytes",
        "OutgoingBytes",
        "OutgoingRecords",
        "IncomingBytes",
        "ReadProvisionedThroughputExceeded",
        "WriteProvisionedThroughputExceeded",
        "IteratorAgeMilliseconds"
    ]
}

variable "tags" {
    description = "Tags for Kinesis stream"
    default = "student-dropout"
}
