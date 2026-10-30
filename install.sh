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

# Resolve caminhos existentes (incluindo links simbólicos) e normaliza os
# componentes ainda inexistentes sem criar diretórios, inclusive em --dry-run.
canonical_path() {
  local input="$1" current rest component candidate
  case "$input" in
    /*) current="/"; rest="${input#/}" ;;
    *) current="$PWD"; rest="$input" ;;
  esac
  while [ -n "$rest" ]; do
    if [[ "$rest" == */* ]]; then component="${rest%%/*}"; rest="${rest#*/}";
    else component="$rest"; rest=""; fi
    case "$component" in
      ""|.) continue ;;
      ..) current="$(dirname -- "$current")" ;;
      *)
        candidate="${current%/}/$component"
        if [ -d "$candidate" ]; then
          current="$(cd -P -- "$candidate" && pwd -P)"
        else
          current="$candidate"
        fi
        ;;
    esac
  done
  printf '%s\n' "${current:-/}"
}

paths_overlap() {
  local first="${1%/}" second="${2%/}"
  [ "$first" = "$second" ] && return 0
  case "$first/" in "$second/"*) return 0 ;; esac
  case "$second/" in "$first/"*) return 0 ;; esac
  return 1
}

validate_skill_dir() {
  local target="$1"
  case "$target" in */"$SKILL_NAME") ;; *) echo "Recusado: caminho inesperado: $target" >&2; return 1 ;; esac
  validate_skill_contents "$target"
}

validate_skill_contents() {
  local target="$1"
  if [ ! -f "$target/SKILL.md" ] || ! grep -q "^name: $SKILL_NAME\$" "$target/SKILL.md"; then
    echo "Recusado: $target existe, mas não parece ser esta skill. Remova ou mova manualmente." >&2
    return 1
  fi
}

# Remove só uma pasta que tenha sido validada como esta skill.
safe_remove() {
  local target="$1"
  validate_skill_dir "$target" || return 1
  run rm -rf -- "$target"
}

script_dir=""
local_src=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  script_dir="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
  if [ -f "$script_dir/skills/$SKILL_NAME/SKILL.md" ]; then
    local_src="$(canonical_path "$script_dir/skills/$SKILL_NAME")"
  fi
fi

if [ "$mode" = "uninstall" ]; then
  failed=0
  for d in "${dests[@]}"; do
    t="$d/$SKILL_NAME"
    if [ -e "$t" ] || [ -L "$t" ]; then
      if [ -n "$local_src" ]; then
        resolved_target="$(canonical_path "$t")"
        if paths_overlap "$local_src" "$resolved_target"; then
          echo "Recusado: o destino coincide ou se sobrepõe à pasta de origem: $t" >&2
          failed=1
          continue
        fi
      fi
      if safe_remove "$t"; then echo "Removida: $t"; else failed=1; fi
    else
      echo "Não encontrada: $t"
    fi
  done
  exit "$failed"
fi

# Localiza o código-fonte: ao lado do script, ou baixa o repositório se rodou via curl.
src="$local_src"
if [ -n "$src" ]; then
  :
else
  command -v curl >/dev/null 2>&1 || { echo "Erro: curl é necessário para baixar a skill." >&2; exit 1; }
  command -v tar  >/dev/null 2>&1 || { echo "Erro: tar é necessário para extrair a skill." >&2; exit 1; }
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  echo "Baixando a skill..."
  curl -fsSL "$REPO_TARBALL" | tar -xz -C "$tmp"
  src="$(find "$tmp" -maxdepth 3 -type d -path "*/skills/$SKILL_NAME" | head -n 1)"
  [ -n "$src" ] && [ -f "$src/SKILL.md" ] || { echo "Erro: skill não encontrada no download." >&2; exit 1; }
fi
src="$(canonical_path "$src")"
validate_skill_dir "$src"

for d in "${dests[@]}"; do
  t="$d/$SKILL_NAME"
  resolved_target="$(canonical_path "$t")"
  if paths_overlap "$src" "$resolved_target"; then
    echo "Recusado: o destino coincide ou se sobrepõe à pasta de origem: $t" >&2
    exit 1
  fi

  if [ -e "$t" ] || [ -L "$t" ]; then validate_skill_dir "$t"; fi

  if [ "$dry_run" -eq 1 ]; then
    echo "[dry-run] prepararia uma cópia validada de $src"
    if [ -e "$t" ] || [ -L "$t" ]; then echo "[dry-run] substituiria a instalação reconhecida em $t";
    else echo "[dry-run] instalaria em $t"; fi
    continue
  fi

  mkdir -p "$d"
  stage="$(mktemp -d "$d/.${SKILL_NAME}.stage.XXXXXX")"
  if ! cp -R "$src/." "$stage/"; then
    rm -rf -- "$stage"
    echo "Erro: não foi possível preparar a nova instalação." >&2
    exit 1
  fi
  if ! validate_skill_contents "$stage"; then
    rm -rf -- "$stage"
    echo "Erro: a cópia preparada não passou na validação." >&2
    exit 1
  fi

  backup=""
  if [ -e "$t" ] || [ -L "$t" ]; then
    backup="$(mktemp -d "$d/.${SKILL_NAME}.backup.XXXXXX")"
    if ! mv -- "$t" "$backup/previous"; then
      rm -rf -- "$stage" "$backup"
      echo "Erro: não foi possível preservar a instalação anterior." >&2
      exit 1
    fi
  fi
  if ! mv -- "$stage" "$t"; then
    if [ -n "$backup" ]; then
      if ! mv -- "$backup/previous" "$t"; then
        echo "Erro crítico: a instalação falhou e a versão anterior ficou em $backup/previous." >&2
        exit 1
      fi
      rmdir -- "$backup" 2>/dev/null || true
    fi
    rm -rf -- "$stage"
    echo "Erro: não foi possível ativar a nova instalação." >&2
    exit 1
  fi
  if [ -n "$backup" ] && ! rm -rf -- "$backup"; then
    echo "Aviso: instalação concluída; não foi possível remover o backup $backup." >&2
  fi
  echo "Instalada: $t"
done

echo
echo "Pronto. Reinicie seu assistente de IA (ou abra uma nova sessão) e peça, por exemplo:"
echo "  \"Crie headlines para o meu produto\""
