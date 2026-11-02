#!/usr/bin/env bash
# Installer for the skill copywriter-master (macOS, Linux, and WSL).
#
# Usage:
#   ./install.sh                  installs to the default user directories
#   ./install.sh --dest PATH      installs only to PATH (option may be repeated)
#   ./install.sh --project        installs in the current directory (this project only)
#   ./install.sh --uninstall      removes the skill from the same destinations
#   ./install.sh --dry-run        shows what would happen without making changes
#
# Without cloning the repository, install the pinned release (archive checksum is verified):
#   curl -fsSL https://github.com/andreischuaste12-ctrl/copywriting-mestre/releases/download/v<version>/install.sh | bash
#   ... | bash -s -- --sha256 <hash published out of band>   # optional stronger check

set -euo pipefail

SKILL_NAME="copywriter-master"
# Remote installs fetch this exact release archive and verify its SHA-256; they never follow a moving branch.
# tools/release.py check fails when this pin differs from VERSION.
RELEASE_VERSION="1.4.0"
RELEASE_BASE_URL="${COPYWRITER_RELEASE_BASE_URL:-https://github.com/andreischuaste12-ctrl/copywriting-mestre/releases/download/v${RELEASE_VERSION}}"
ARCHIVE_NAME="${SKILL_NAME}-${RELEASE_VERSION}.zip"

# Skill directories read by AI assistants that support the SKILL.md format.
DEFAULT_SUBDIRS=(".claude/skills" ".agents/skills")

dests=()
mode="install"
dry_run=0
project=0
expected_sha256=""

usage() { sed -n '2,14p' "$0" 2>/dev/null | sed 's/^# \{0,1\}//' || true; }

while [ $# -gt 0 ]; do
  case "$1" in
    --dest)      [ $# -ge 2 ] || { echo "Error: --dest requires a directory." >&2; exit 2; }
                 dests+=("$2"); shift 2 ;;
    --project)   project=1; shift ;;
    --uninstall) mode="uninstall"; shift ;;
    --dry-run)   dry_run=1; shift ;;
    --sha256)    [ $# -ge 2 ] || { echo "Error: --sha256 requires a hash." >&2; exit 2; }
                 expected_sha256="$2"; shift 2 ;;
    -h|--help)   usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ "${#dests[@]}" -eq 0 ]; then
  base="$HOME"; [ "$project" -eq 1 ] && base="$PWD"
  for sub in "${DEFAULT_SUBDIRS[@]}"; do dests+=("$base/$sub"); done
fi

run() { if [ "$dry_run" -eq 1 ]; then echo "[dry-run] $*"; else "$@"; fi; }

# Resolve existing paths (including symbolic links) and normalize nonexistent
# components without creating directories, including in --dry-run mode.
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
  case "$target" in */"$SKILL_NAME") ;; *) echo "Refused: unexpected path: $target" >&2; return 1 ;; esac
  validate_skill_contents "$target"
}

validate_skill_contents() {
  local target="$1"
  if [ ! -f "$target/SKILL.md" ] || ! grep -q "^name: $SKILL_NAME\$" "$target/SKILL.md"; then
    echo "Refused: $target exists but does not appear to be this skill. Remove or move it manually." >&2
    return 1
  fi
}

# Remove only a directory validated as this skill.
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
          echo "Refused: destination matches or overlaps the source directory: $t" >&2
          failed=1
          continue
        fi
      fi
      if safe_remove "$t"; then echo "Removed: $t"; else failed=1; fi
    else
      echo "Not found: $t"
    fi
  done
  exit "$failed"
fi

# Locate source beside this script, or download the pinned release archive when run via curl.
sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum -- "$1" | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then shasum -a 256 -- "$1" | cut -d' ' -f1
  else echo "Error: sha256sum or shasum is required to verify the download." >&2; return 1; fi
}

src="$local_src"
if [ -n "$src" ]; then
  :
else
  for tool in curl unzip; do
    command -v "$tool" >/dev/null 2>&1 || { echo "Error: $tool is required to download the skill." >&2; exit 1; }
  done
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  echo "Downloading $ARCHIVE_NAME (release v$RELEASE_VERSION)..."
  curl -fsSL "$RELEASE_BASE_URL/$ARCHIVE_NAME" -o "$tmp/$ARCHIVE_NAME" \
    || { echo "Error: could not download $RELEASE_BASE_URL/$ARCHIVE_NAME. Has release v$RELEASE_VERSION been published?" >&2; exit 1; }
  curl -fsSL "$RELEASE_BASE_URL/SHA256SUMS" -o "$tmp/SHA256SUMS" \
    || { echo "Error: could not download SHA256SUMS for release v$RELEASE_VERSION." >&2; exit 1; }
  listed="$(awk -v name="$ARCHIVE_NAME" '$2 == name { print $1 }' "$tmp/SHA256SUMS")"
  actual="$(sha256_of "$tmp/$ARCHIVE_NAME")" || exit 1
  if [ -z "$listed" ] || [ "$listed" != "$actual" ]; then
    echo "Error: checksum mismatch for $ARCHIVE_NAME; refusing to install." >&2; exit 1
  fi
  if [ -n "$expected_sha256" ] && [ "$(printf '%s' "$expected_sha256" | tr 'A-F' 'a-f')" != "$actual" ]; then
    echo "Error: archive does not match the --sha256 you supplied; refusing to install." >&2; exit 1
  fi
  unzip -q "$tmp/$ARCHIVE_NAME" -d "$tmp/extract" || { echo "Error: could not extract the archive." >&2; exit 1; }
  src="$tmp/extract/$SKILL_NAME"
  [ -f "$src/SKILL.md" ] || { echo "Error: skill was not found in the archive." >&2; exit 1; }
fi
src="$(canonical_path "$src")"
validate_skill_dir "$src"

for d in "${dests[@]}"; do
  t="$d/$SKILL_NAME"
  resolved_target="$(canonical_path "$t")"
  if paths_overlap "$src" "$resolved_target"; then
    echo "Refused: destination matches or overlaps the source directory: $t" >&2
    exit 1
  fi

  if [ -e "$t" ] || [ -L "$t" ]; then validate_skill_dir "$t"; fi

  if [ "$dry_run" -eq 1 ]; then
    echo "[dry-run] would prepare a validated copy of $src"
    if [ -e "$t" ] || [ -L "$t" ]; then echo "[dry-run] would replace the recognized installation at $t";
    else echo "[dry-run] would install to $t"; fi
    continue
  fi

  mkdir -p "$d"
  stage="$(mktemp -d "$d/.${SKILL_NAME}.stage.XXXXXX")"
  if ! cp -R "$src/." "$stage/"; then
    rm -rf -- "$stage"
    echo "Error: could not prepare the new installation." >&2
    exit 1
  fi
  if ! validate_skill_contents "$stage"; then
    rm -rf -- "$stage"
    echo "Error: the staged copy did not pass validation." >&2
    exit 1
  fi

  backup=""
  if [ -e "$t" ] || [ -L "$t" ]; then
    backup="$(mktemp -d "$d/.${SKILL_NAME}.backup.XXXXXX")"
    if ! mv -- "$t" "$backup/previous"; then
      rm -rf -- "$stage" "$backup"
      echo "Error: could not preserve the previous installation." >&2
      exit 1
    fi
  fi
  if ! mv -- "$stage" "$t"; then
    if [ -n "$backup" ]; then
      if ! mv -- "$backup/previous" "$t"; then
        echo "Critical error: installation failed and the previous version remains at $backup/previous." >&2
        exit 1
      fi
      rmdir -- "$backup" 2>/dev/null || true
    fi
    rm -rf -- "$stage"
    echo "Error: could not activate the new installation." >&2
    exit 1
  fi
  if [ -n "$backup" ] && ! rm -rf -- "$backup"; then
    echo "Warning: installation completed; could not remove backup $backup." >&2
  fi
  echo "Installed: $t"
done

echo
echo "Done. Restart your AI assistant (or open a new session) and try a request such as:"
echo "  \"Write headlines for my product\""
