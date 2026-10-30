#!/usr/bin/env bash
# Instalador da skill copywriter-mestre (macOS, Linux e WSL).
#
# Uso:
#   ./install.sh                  instala nas pastas padrão do seu usuário
#   ./install.sh --dest PASTA     instala só em PASTA (pode repetir a opção)
#   ./install.sh --project        instala dentro do diretório atual (somente este projeto)
#   ./install.sh --uninstall      remove a skill dos mesmos destinos
#   ./install.sh --dry-run        mostra o que seria feito, sem alterar nada
#
# Sem clonar o repositório:
#   curl -fsSL https://raw.githubusercontent.com/andreischuaste12-ctrl/copywriting-mestre/main/install.sh | bash

set -euo pipefail

SKILL_NAME="copywriter-mestre"
REPO_TARBALL="https://github.com/andreischuaste12-ctrl/copywriting-mestre/archive/refs/heads/main.tar.gz"

# Pastas de skills lidas por assistentes de IA compatíveis com o formato SKILL.md.
DEFAULT_SUBDIRS=(".claude/skills" ".agents/skills")

dests=()
mode="install"
dry_run=0
project=0

usage() { sed -n '2,13p' "$0" 2>/dev/null | sed 's/^# \{0,1\}//' || true; }

while [ $# -gt 0 ]; do
  case "$1" in
    --dest)      [ $# -ge 2 ] || { echo "Erro: --dest exige uma pasta." >&2; exit 2; }
                 dests+=("$2"); shift 2 ;;
    --project)   project=1; shift ;;
    --uninstall) mode="uninstall"; shift ;;
    --dry-run)   dry_run=1; shift ;;
    -h|--help)   usage; exit 0 ;;
    *) echo "Opção desconhecida: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ "${#dests[@]}" -eq 0 ]; then
  base="$HOME"; [ "$project" -eq 1 ] && base="$PWD"
  for sub in "${DEFAULT_SUBDIRS[@]}"; do dests+=("$base/$sub"); done
fi

run() { if [ "$dry_run" -eq 1 ]; then echo "[dry-run] $*"; else "$@"; fi; }

# Remove só uma pasta que seja, de fato, esta skill.
safe_remove() {
  local target="$1"
  case "$target" in */"$SKILL_NAME") ;; *) echo "Recusado: caminho inesperado: $target" >&2; return 1 ;; esac
  if [ ! -f "$target/SKILL.md" ] || ! grep -q "^name: $SKILL_NAME\$" "$target/SKILL.md"; then
    echo "Recusado: $target existe, mas não parece ser esta skill. Remova ou mova manualmente." >&2
    return 1
  fi
  run rm -rf -- "$target"
}

if [ "$mode" = "uninstall" ]; then
  for d in "${dests[@]}"; do
    t="$d/$SKILL_NAME"
    if [ -e "$t" ]; then safe_remove "$t" && echo "Removida: $t"; else echo "Não encontrada: $t"; fi
  done
  exit 0
fi

# Localiza o código-fonte: ao lado do script, ou baixa o repositório se rodou via curl.
src=""
script_dir=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
if [ -n "$script_dir" ] && [ -f "$script_dir/skills/$SKILL_NAME/SKILL.md" ]; then
  src="$script_dir/skills/$SKILL_NAME"
else
  command -v curl >/dev/null 2>&1 || { echo "Erro: curl é necessário para baixar a skill." >&2; exit 1; }
  command -v tar  >/dev/null 2>&1 || { echo "Erro: tar é necessário para extrair a skill." >&2; exit 1; }
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  echo "Baixando a skill..."
  curl -fsSL "$REPO_TARBALL" | tar -xz -C "$tmp"
  src="$(find "$tmp" -maxdepth 3 -type d -path "*/skills/$SKILL_NAME" | head -n 1)"
  [ -n "$src" ] && [ -f "$src/SKILL.md" ] || { echo "Erro: skill não encontrada no download." >&2; exit 1; }
fi

for d in "${dests[@]}"; do
  t="$d/$SKILL_NAME"
  run mkdir -p "$d"
  if [ -e "$t" ]; then safe_remove "$t"; fi
  run cp -R "$src" "$t"
  if [ "$dry_run" -eq 0 ] && [ ! -f "$t/SKILL.md" ]; then
    echo "Erro: falha ao instalar em $t" >&2; exit 1
  fi
  if [ "$dry_run" -eq 1 ]; then echo "Seria instalada: $t"; else echo "Instalada: $t"; fi
done

echo
echo "Pronto. Reinicie seu assistente de IA (ou abra uma nova sessão) e peça, por exemplo:"
echo "  \"Crie headlines para o meu produto\""
