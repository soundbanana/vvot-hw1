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

# Variables for configuration
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
  description = "Path to the Yandex service account key file."
}

variable "SERVERLESS_FUNCTION_NAME" {
  type        = string
  description = "Name for the serverless function in Yandex Cloud."
}

variable "TELEGRAM_BOT_TOKEN" {
  type        = string
  description = "Telegram Bot API Token."
}

# Package the Telegram bot code
resource "archive_file" "bot_code" {
  type        = "zip"
  source_dir  = "./src"
  output_path = "telegram.zip"
}

# Yandex Cloud Function configuration
resource "yandex_function" "func" {
  name       = var.SERVERLESS_FUNCTION_NAME
  runtime    = "python312"
  entrypoint = "main.handler"
  memory     = 128
  user_hash  = archive_file.bot_code.output_sha256

  environment = {
    "TELEGRAM_BOT_TOKEN" = var.TELEGRAM_BOT_TOKEN
  }

  content {
    zip_filename = archive_file.bot_code.output_path
  }
}

# Set Telegram Bot Webhook
resource "telegram_bot_webhook" "set_webhook" {
  url = "https://api.telegram.org/bot${var.TELEGRAM_BOT_TOKEN}/setWebhook?url=https://functions.yandexcloud.net/${yandex_function.func.id}"
}

# Outputs for important resources
output "function_url" {
  description = "The public URL of the deployed Yandex Function."
  value       = "https://functions.yandexcloud.net/${yandex_function.func.id}"
}

output "webhook_url" {
  description = "The Telegram webhook URL configured for the bot."
  value       = telegram_bot_webhook.set_webhook.url
}