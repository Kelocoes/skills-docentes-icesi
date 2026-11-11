#!/bin/bash
# init_skill_output.sh - Creates skill output directory structure and INFO.md
# Usage: ./init_skill_output.sh <skill_name> <executed_by> <prompt>

SKILL_NAME="$1"
EXECUTED_BY="$2"
PROMPT="$3"

if [ -z "$SKILL_NAME" ] || [ -z "$EXECUTED_BY" ] || [ -z "$PROMPT" ]; then
    echo "Usage: $0 <skill_name> <executed_by> <prompt>"
    exit 1
fi

DATE_STR=$(date +"%m-%d-%Y")
OUTPUT_BASE_DIR="output-skills/${SKILL_NAME}"

# Calculate next increment counter (e.g. 01, 02)
COUNTER=1
while [ -d "${OUTPUT_BASE_DIR}/${DATE_STR}_$(printf "%02d" $COUNTER)" ]; do
    COUNTER=$((COUNTER + 1))
done

COUNTER_STR=$(printf "%02d" $COUNTER)
TARGET_DIR="${OUTPUT_BASE_DIR}/${DATE_STR}_${COUNTER_STR}"

mkdir -p "$TARGET_DIR"

INFO_FILE="${TARGET_DIR}/INFO.md"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S %z")

cat << EOF > "$INFO_FILE"
# Execution Information

- **Skill**: ${SKILL_NAME}
- **Executed By**: ${EXECUTED_BY}
- **Date & Time**: ${TIMESTAMP}
- **Prompt**:
${PROMPT}
EOF

echo "$TARGET_DIR"
