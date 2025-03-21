#!/bin/bash

# Executa o seu programa Python com Poetry em segundo plano
poetry run ucan &
PROGRAM_PID=$!

# Aguarda a inicialização do programa
sleep 3

# Captura a janela ativa com ImageMagick
import -window "$(xdotool getactivewindow)" ./assets/screen/screenshot.png

# Fecha gentilmente a janela ativa com wmctrl (melhor abordagem para apps gráficos)
ACTIVE_WINDOW=$(xdotool getactivewindow)
wmctrl -ic "$ACTIVE_WINDOW"

# Espera até 3 segundos para fechamento
sleep 3

# Se ainda estiver aberto após a tentativa acima, força fechamento
if kill -0 "$PROGRAM_PID" 2>/dev/null; then
    kill -9 "$PROGRAM_PID"
fi
