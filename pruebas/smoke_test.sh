#!/bin/sh
# Prueba rápida de la API. Uso:  sh pruebas/smoke_test.sh [URL_BASE]
# Por defecto prueba http://localhost:5000
BASE="${1:-http://localhost:5000}"
OK=0; FALLAS=0

verificar() {  # descripción, código_esperado, código_obtenido
    if [ "$2" = "$3" ]; then OK=$((OK+1)); echo "  OK     $1 (HTTP $3)"
    else FALLAS=$((FALLAS+1)); echo "  FALLA  $1 (esperado $2, obtenido $3)"; fi
}
codigo() { curl -s -o /dev/null -w "%{http_code}" "$@"; }

echo "Probando API en $BASE"
verificar "GET /health"                200 "$(codigo "$BASE/health")"
verificar "GET /productos"             200 "$(codigo "$BASE/productos")"
verificar "POST /productos (válido)"   201 "$(codigo -X POST "$BASE/productos" -H 'Content-Type: application/json' -d '{"nombre":"Prueba smoke","precio":1000,"stock":5}')"
verificar "POST /productos (inválido)" 400 "$(codigo -X POST "$BASE/productos" -H 'Content-Type: application/json' -d '{"nombre":"","precio":-5}')"
ID=$(curl -s "$BASE/productos" | grep -o '"id": *[0-9]*' | tail -1 | grep -o '[0-9]*$')
verificar "GET /productos/$ID"         200 "$(codigo "$BASE/productos/$ID")"
verificar "PUT /productos/$ID"         200 "$(codigo -X PUT "$BASE/productos/$ID" -H 'Content-Type: application/json' -d '{"nombre":"Prueba editada","precio":2000,"stock":9}')"
verificar "DELETE /productos/$ID"      200 "$(codigo -X DELETE "$BASE/productos/$ID")"
verificar "GET producto borrado"       404 "$(codigo "$BASE/productos/$ID")"

echo "Resultado: $OK correctas, $FALLAS con falla"
[ "$FALLAS" -eq 0 ]
