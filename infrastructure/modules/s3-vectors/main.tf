resource "awscc_s3vectors_vector_bucket" "this" {
  provider = awscc

  vector_bucket_name = var.bucket_name
  encryption_configuration = {
    sse_type = "AES256"
  }
  tags = [
    { key = "Name", value = var.bucket_name },
    { key = "Project", value = var.project_name },
    { key = "Environment", value = var.environment },
    { key = "ManagedBy", value = "terraform" },
  ]
}

resource "awscc_s3vectors_index" "this" {
  provider = awscc

  index_name         = var.index_name
  vector_bucket_name = awscc_s3vectors_vector_bucket.this.vector_bucket_name
  data_type          = "float32"
  dimension          = var.dimension
  distance_metric    = "cosine"
  tags = [
    { key = "Name", value = var.index_name },
    { key = "Project", value = var.project_name },
    { key = "Environment", value = var.environment },
    { key = "ManagedBy", value = "terraform" },
  ]
}
