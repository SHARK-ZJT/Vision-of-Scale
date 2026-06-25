#!/bin/bash
set -e

echo "=== Vision of Scale — Harness Initialization ==="

# 1. Check virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
  if [ -d "venv" ]; then
    echo "⚠️  Virtual environment not activated. Run:"
    echo "   venv\\Scripts\\activate   (Windows)"
    echo "   source venv/bin/activate  (Mac/Linux)"
    exit 1
  else
    echo "📦 No venv found. Creating..."
    python -m venv venv
    echo "✅ venv created. Activate it and re-run ./init.sh"
    exit 1
  fi
fi
echo "✅ Virtual environment: $VIRTUAL_ENV"

# 2. Check dependencies
if [ -f "requirements.txt" ]; then
  echo "📦 Checking dependencies..."
  python -m pip install -r requirements.txt -q
  echo "✅ Dependencies installed"
fi

# 3. Syntax check
echo "🔍 Python syntax check..."
python -m compileall . -q
echo "✅ Syntax OK"

# 4. Import check (can the app module be loaded?)
echo "🔍 App import check..."
python -c "from app.main import create_app; app = create_app(); print('✅ App loaded successfully')"

echo ""
echo "=== Verification Complete ==="
echo ""
echo "Next steps:"
echo "1. Read feature_list.json to see current feature state"
echo "2. Pick ONE unfinished feature to work on"
echo "3. Implement only that feature"
echo "4. Re-run verification before claiming done"
