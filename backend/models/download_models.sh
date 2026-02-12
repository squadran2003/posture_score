#!/bin/bash
# Download MediaPipe pose landmarker model
# Run from the backend/models/ directory

MODEL_URL="https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
MODEL_FILE="pose_landmarker_lite.task"

if [ -f "$MODEL_FILE" ]; then
    echo "Model already exists: $MODEL_FILE"
else
    echo "Downloading $MODEL_FILE..."
    curl -L -o "$MODEL_FILE" "$MODEL_URL"
    echo "Done."
fi
