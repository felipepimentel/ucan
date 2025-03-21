#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SCREENSHOT_DIR="$PROJECT_ROOT/assets/screen"
mkdir -p "$SCREENSHOT_DIR"

# Executa aplicação Python com aceleração gráfica desativada
QT_QUICK_BACKEND=software QT_OPENGL=software poetry run ucan &
PROGRAM_PID=$!

echo "⏳ Aguardando aplicação inicializar..."
sleep 5

# Obtém ID da janela pelo PID
WINDOW_ID=$(xdotool search --pid "$PROGRAM_PID" | head -n 1)

if [ -z "$WINDOW_ID" ]; then
    echo "❌ Nenhuma janela encontrada para o PID $PROGRAM_PID"
    kill "$PROGRAM_PID"
    exit 1
fi

# Salva janela atualmente ativa para restaurar depois
ORIGINAL_WINDOW=$(xdotool getactivewindow)

# Desminimiza e traz explicitamente a janela para frente
xdotool windowmap "$WINDOW_ID"
wmctrl -i -a "$WINDOW_ID"
sleep 1

echo "📸 Capturando screenshot da janela correta (gnome-screenshot)..."
rm -f "$SCREENSHOT_DIR/screenshot.png"

# Captura robusta usando gnome-screenshot
gnome-screenshot -w --file="$SCREENSHOT_DIR/screenshot.png"

# Restaura janela anterior após captura
if [ -n "$ORIGINAL_WINDOW" ]; then
    wmctrl -i -a "$ORIGINAL_WINDOW"
fi

echo "🔴 Fechando aplicação..."
wmctrl -ic "$WINDOW_ID"

sleep 3

# Força encerramento se necessário
if kill -0 "$PROGRAM_PID" 2>/dev/null; then
    echo "⚠️ Forçando encerramento da aplicação..."
    kill -9 "$PROGRAM_PID"
fi

echo "✅ Screenshot salvo em $SCREENSHOT_DIR/screenshot.png"
