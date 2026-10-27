#!/usr/bin/env bash
# NewsMind on the Ubuntu debug host, port 8007.
#   bash /www/wwwroot/NewsMind8007/start.sh --daemon
#   bash /www/wwwroot/NewsMind8007/start.sh --stop
#   bash /www/wwwroot/NewsMind8007/start.sh --status

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8007}"
HOST="${HOST:-0.0.0.0}"
BACKEND="$ROOT/backend"
VENV="$BACKEND/.venv"
PY="$VENV/bin/python"
LOG_DIR="$ROOT/logs"
PID_FILE="$ROOT/newsmind.pid"
LOG_FILE="$LOG_DIR/newsmind.log"
REQ="$BACKEND/requirements-prod.txt"
STAMP="$VENV/.req-stamp"
DAEMON=0
ACTION="start"

for arg in "$@"; do
  case "$arg" in
    --daemon|-d) DAEMON=1 ;;
    --stop) ACTION="stop" ;;
    --status) ACTION="status" ;;
    --help|-h)
      echo "Usage: $0 [--daemon] [--stop] [--status]"
      echo "  default port 8007, listen 0.0.0.0"
      exit 0
      ;;
    *)
      echo "[error] unknown arg: $arg"
      exit 1
      ;;
  esac
done

is_running() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

stop_pid() {
  local pid="$1"
  kill "$pid" 2>/dev/null || true
  pkill -P "$pid" >/dev/null 2>&1 || true
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    kill -0 "$pid" 2>/dev/null || return 0
    sleep 0.4
  done
  kill -9 "$pid" 2>/dev/null || true
  pkill -9 -P "$pid" >/dev/null 2>&1 || true
}

if [[ "$ACTION" == "stop" ]]; then
  if is_running; then
    pid="$(cat "$PID_FILE")"
    echo "[info] stopping pid=$pid ..."
    stop_pid "$pid"
    rm -f "$PID_FILE"
    echo "[info] stopped"
  else
    rm -f "$PID_FILE"
    echo "[info] not running"
  fi
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${PORT}/tcp" >/dev/null 2>&1 || true
  fi
  exit 0
fi

if [[ "$ACTION" == "status" ]]; then
  if is_running; then
    echo "[info] running pid=$(cat "$PID_FILE")  http://${HOST}:${PORT}"
    exit 0
  fi
  echo "[info] not running"
  exit 1
fi

cd "$BACKEND"

if is_running; then
  echo "[error] already running pid=$(cat "$PID_FILE"). Stop first: bash $ROOT/start.sh --stop"
  exit 1
fi

if [[ ! -f "$BACKEND/app/main.py" ]]; then
  echo "[error] missing $BACKEND/app/main.py"
  exit 1
fi

if [[ ! -f "$REQ" ]]; then
  echo "[error] missing $REQ"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[error] python3 not found"
  exit 1
fi

if [[ ! -x "$PY" ]]; then
  if ! python3 -m venv "$VENV"; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y
    apt-get install -y python3-venv python3-pip
    python3 -m venv "$VENV"
  fi
fi

if ! "$PY" -m pip --version >/dev/null 2>&1; then
  "$PY" -m ensurepip --upgrade
fi

req_hash="$(sha256sum "$REQ" | awk '{print $1}')"
installed="$(cat "$STAMP" 2>/dev/null || true)"
if [[ "$installed" != "$req_hash" ]] || ! "$PY" -c "import fastapi,uvicorn,sqlalchemy" >/dev/null 2>&1; then
  echo "[info] installing python packages ..."
  "$PY" -m pip install -q --upgrade pip
  "$PY" -m pip install -q -r "$REQ"
  echo "$req_hash" >"$STAMP"
fi

export DEBUG=false
export DATABASE_URL="sqlite:///${BACKEND}/newsmind.db"
export PYTHONUNBUFFERED=1

mkdir -p "$LOG_DIR"
echo "[info] starting http://${HOST}:${PORT}"

if [[ "$DAEMON" -eq 1 ]]; then
  nohup "$PY" -m uvicorn app.main:app --host "$HOST" --port "$PORT" --workers 1 >>"$LOG_FILE" 2>&1 &
  echo $! >"$PID_FILE"
  sleep 0.8
  if is_running; then
    echo "[info] started in background pid=$(cat "$PID_FILE")"
    echo "[info] log: $LOG_FILE"
  else
    echo "[error] start failed, see log: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
  fi
else
  exec "$PY" -m uvicorn app.main:app --host "$HOST" --port "$PORT" --workers 1
fi
