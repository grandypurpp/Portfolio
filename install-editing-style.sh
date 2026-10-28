#!/usr/bin/env bash
# Installs the signature-edit-style skill for Claude Code on this machine, so it
# applies to every project (client and personal), not just this repo.
#   ./install-editing-style.sh
set -euo pipefail

repo="$(cd "$(dirname "$0")" && pwd)"
dest="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/signature-edit-style"

mkdir -p "$dest"
cp -R "$repo/.claude/skills/signature-edit-style/." "$dest/"

# Ship the Remotion template alongside the skill (without node_modules / renders).
mkdir -p "$dest/template"
tar -C "$repo/editing-style-template" --exclude=node_modules --exclude=out -cf - . | tar -C "$dest/template" -xf -

echo "Installed skill → $dest"
echo "Remotion template → $dest/template (run 'npm install' there or copy it into a project)"

# DeepFilterNet: free, local speech enhancer used by scripts/enhance_audio.py (falls back to ffmpeg without it).
df_ver="0.5.6"
case "$(uname -s)-$(uname -m)" in
  Darwin-arm64)  df_asset="aarch64-apple-darwin" ;;
  Darwin-x86_64) df_asset="x86_64-apple-darwin" ;;
  Linux-x86_64)  df_asset="x86_64-unknown-linux-musl" ;;
  Linux-aarch64) df_asset="aarch64-unknown-linux-gnu" ;;
  *)             df_asset="" ;;
esac
if [ -n "$df_asset" ] && [ ! -x "$dest/bin/deep-filter" ]; then
  echo "Downloading DeepFilterNet $df_ver ($df_asset)…"
  mkdir -p "$dest/bin"
  if curl -fsSL -o "$dest/bin/deep-filter" \
      "https://github.com/Rikorose/DeepFilterNet/releases/download/v$df_ver/deep-filter-$df_ver-$df_asset"; then
    chmod +x "$dest/bin/deep-filter"
    # macOS quarantines downloaded binaries; clear it so it can run
    [ "$(uname -s)" = Darwin ] && xattr -d com.apple.quarantine "$dest/bin/deep-filter" 2>/dev/null || true
  else
    rm -f "$dest/bin/deep-filter"
    echo "DeepFilterNet download failed; enhance_audio.py will use the ffmpeg fallback."
  fi
fi

if command -v python3 >/dev/null; then
  echo "Installing analyzer deps (faster-whisper, librosa)…"
  python3 -m pip install --user --quiet faster-whisper librosa || echo "pip install failed; run: python3 -m pip install faster-whisper librosa"
fi
command -v ffmpeg >/dev/null || echo "NOTE: ffmpeg not found. Install it (macOS: brew install ffmpeg)."
command -v node >/dev/null || echo "NOTE: Node.js not found. Install Node 18+ to render with Remotion."
echo "Done. Restart Claude Code, then ask for 'my edit style' or run /signature-edit-style."
