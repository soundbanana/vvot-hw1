terraform {
  required_version = ">= 0.13"

  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
    telegram = {
      source = "yi-jiayu/telegram"
    }
  }
}

# Yandex Cloud provider configuration
provider "yandex" {
  cloud_id                 = var.CLOUD_ID
  folder_id                = var.FOLDER_ID
  service_account_key_file = var.SERVICE_ACCOUNT_KEY_FILE_PATH
}

# Telegram provider configuration
provider "telegram" {
  bot_token = var.TELEGRAM_BOT_TOKEN
}

# Variables
variable "CLOUD_ID" {
  type        = string
  description = "Yandex Cloud ID."
}

variable "FOLDER_ID" {
  type        = string
  description = "Yandex Cloud Folder ID."
}

variable "SERVICE_ACCOUNT_KEY_FILE_PATH" {
  type        = string
  description = "Path to the key for service account with admin role."
}

variable "SERVICE_ACCOUNT_ID" {
  type        = string
  description = "Admin Service Account ID"
}

variable "SERVERLESS_FUNCTION_NAME" {
  type        = string
  description = "Name for the serverless function in Yandex Cloud"
}

variable "BUCKET_NAME" {
  type        = string
  description = "Name for the Bucket in Yandex Cloud"
}

variable "BUCKET_OBJECT_GPT_INSTRUCTIONS_KEY" {
  type        = string
  description = "Name for the Instructions file inside Bucket"
}

variable "TELEGRAM_BOT_TOKEN" {
  type        = string
  description = "Telegram Bot API Token."
}

# Package the Telegram bot code
resource "archive_file" "bot_code" {
  type        = "zip"
  source_dir  = "./src"
  output_path = "./archive/telegram.zip"
}

# Service Account
resource "yandex_iam_service_account_api_key" "sa_api_key" {
  service_account_id = var.SERVICE_ACCOUNT_ID
}

# Yandex Cloud Function configuration
resource "yandex_function" "func" {
  name               = var.SERVERLESS_FUNCTION_NAME
  runtime            = "python312"
  entrypoint         = "main.handler"
  memory             = 128
  service_account_id = var.SERVICE_ACCOUNT_ID
  user_hash          = archive_file.bot_code.output_sha256

  environment = {
    "TELEGRAM_BOT_TOKEN"                 = var.TELEGRAM_BOT_TOKEN
    "FOLDER_ID"                          = var.FOLDER_ID
    "SERVICE_ACCOUNT_API_KEY"            = yandex_iam_service_account_api_key.sa_api_key.secret_key
    "BUCKET_NAME"                        = var.BUCKET_NAME
    "BUCKET_OBJECT_GPT_INSTRUCTIONS_KEY" = var.BUCKET_OBJECT_GPT_INSTRUCTIONS_KEY
  }

  content {
    zip_filename = archive_file.bot_code.output_path
  }

  mounts {
    name = var.BUCKET_NAME
    mode = "ro"
    object_storage {
      bucket = yandex_storage_bucket.instructions_bucket.bucket
    }
  }
}

# Object Storage
resource "yandex_storage_bucket" "instructions_bucket" {
  bucket = var.BUCKET_NAME
}

resource "yandex_storage_object" "gpt_instructions" {
  bucket = yandex_storage_bucket.instructions_bucket.id
  key    = var.BUCKET_OBJECT_GPT_INSTRUCTIONS_KEY
  source = "./instructions/gpt_instructions.txt"
}

# Set Telegram Bot Webhook
resource "telegram_bot_webhook" "set_webhook" {
  url = "https://api.telegram.org/bot${var.TELEGRAM_BOT_TOKEN}/setWebhook?url=https://functions.yandexcloud.net/${yandex_function.func.id}"
}

# Outputs
output "function_url" {
  description = "The public URL of the deployed Yandex Function."
  value       = "https://functions.yandexcloud.net/${yandex_function.func.id}"
}

output "webhook_url" {
  description = "The Telegram webhook URL configured for the bot."
  value       = telegram_bot_webhook.set_webhook.url
}