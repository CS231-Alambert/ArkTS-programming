#!/bin/bash
# ArkAgent KB batch fetcher — fetches all HarmonyOS dev doc pages via Playwright
# Usage: bash /root/ArkAgent/scripts/fetch_all.sh [section]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FETCH_SCRIPT="$SCRIPT_DIR/fetch_huawei_doc.py"
DELAY=2

fetch_section() {
    local section=$1
    shift
    local slugs=("$@")
    local total=${#slugs[@]}
    local ok=0
    local fail=0

    echo ""
    echo "============================================"
    echo "  Section: $section ($total pages)"
    echo "============================================"

    for slug in "${slugs[@]}"; do
        echo ""
        echo "[$((ok+fail+1))/$total] $section/$slug"
        if python3 "$FETCH_SCRIPT" --slug "$slug" --section "$section" 2>&1; then
            ((ok++))
        else
            ((fail++))
            echo "  ⚠️  FAILED: $slug (continuing...)"
        fi
        sleep "$DELAY"
    done

    echo ""
    echo "--- $section done: $ok OK, $fail FAILED, $total total ---"
}

# ── ArkTS ──
ARKTS_SLUGS=(
    arkts-overview arkts-utils arkts-concurrency
    arkts-cross-language-interaction arkts-runtime arkts-compilation-tool-chain
    arkts-glossary arkts-get-started arkts-decorator-overview
    arkts-common-components-video-player buffer introduction-to-arkts
    start-with-ets-stage taskpool-introduction
    typescript-to-arkts-migration-guide worker-introduction xml-overview
)

# ── ArkUI ──
ARKUI_SLUGS=(
    arkui-overview arkts-ui-development arkts-use-ndk
    ui-js-dev ui-debug-optimize window-manager display-manager
    arkui-glossary arkts-glossary
)

# ── UI Design Kit ──
UIDESIGN_SLUGS=(
    ui-design-introduction ui-design-icon-process ui-design-navigation
    ui-design-sidebar ui-design-side-menu ui-design-hds-tabs
    ui-design-snackbar ui-design-actionbar ui-design-list-item-card
    ui-design-custom-symbol-res-register ui-design-visual-effect
    ui-design-multiwindowentryinapp ui-design-hds-component-material
    ui-design-faq localization-glossary
)

# ── ArkWeb (only the ones NOT already in KB) ──
ARKWEB_SLUGS=(
    web-set-attributes-events web-default-useragent
    web-cookie-and-data-storage-mgmt web-set-dark-mode
    web-open-in-new-window web-geolocation-permission
    web-incognito-mode web-sensor web-render-layout
    web-use-frontend-page-js web-manage-page-interaction
    web-manage-cyber-security-privacy web-manage-loading-browsing
    web-manage-upload-download web-file-upload web-download
    web-use-multimedia web-rtc app-takeovers-web-media
    web-picture-in-picture web_full_screen
    web-process-page-content web-print web-createpdf
    web-pdf-preview web-safe-area-insets web-menu
    web-clipboard web-data-detector web-debugging
)

# ── Main ──
SECTION="${1:-all}"

case "$SECTION" in
    arkts)
        fetch_section arkts "${ARKTS_SLUGS[@]}"
        ;;
    arkui)
        fetch_section arkui "${ARKUI_SLUGS[@]}"
        ;;
    ui-design-kit)
        fetch_section ui-design-kit "${UIDESIGN_SLUGS[@]}"
        ;;
    arkweb)
        fetch_section arkweb "${ARKWEB_SLUGS[@]}"
        ;;
    all)
        fetch_section arkts "${ARKTS_SLUGS[@]}"
        fetch_section arkui "${ARKUI_SLUGS[@]}"
        fetch_section ui-design-kit "${UIDESIGN_SLUGS[@]}"
        fetch_section arkweb "${ARKWEB_SLUGS[@]}"
        ;;
    *)
        echo "Usage: $0 [arkts|arkui|ui-design-kit|arkweb|all]"
        exit 1
        ;;
esac

echo ""
echo "============================================"
echo "  All done!"
echo "============================================"

# Count total MD files
echo ""
echo "KB file counts:"
for d in arkts arkui arkweb ui-design-kit; do
    count=$(ls /root/.cc-switch/skills/harmonyos-arkts/docs/$d/*.md 2>/dev/null | wc -l)
    echo "  $d: $count files"
done
