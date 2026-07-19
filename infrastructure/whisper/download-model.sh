#!/bin/sh
set -eu
model_name="${WHISPER_MODEL:-small}"
model_path="/models/ggml-${model_name}.bin"
if [ ! -s "$model_path" ]; then
  echo "Downloading whisper.cpp model: ${model_name}"
  curl --fail --location --retry 3 --output "${model_path}.tmp" \
    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-${model_name}.bin"
  mv "${model_path}.tmp" "$model_path"
fi
exec whisper-server --host 0.0.0.0 --port 8080 --model "$model_path" --language "${STT_LANGUAGE:-ja}" --no-gpu
