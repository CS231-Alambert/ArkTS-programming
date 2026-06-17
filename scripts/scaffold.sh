#!/usr/bin/env bash
# scaffold.sh — Generate a HarmonyOS NEXT (API 12+) project skeleton.
# Usage: bash scaffold.sh <ProjectName> <com.example.app>
# Example: bash scaffold.sh MyApp com.example.myapp
#
# Output structure:
#   <ProjectName>/
#   ├── entry/src/main/
#   │   ├── ets/pages/Index.ets          ← Navigation skeleton
#   │   ├── ets/components/
#   │   ├── ets/viewmodel/
#   │   ├── ets/model/
#   │   │   └── resources/base/
#   │   │       ├── element/
#   │   │       ├── media/
#   │   │       └── profile/
#   │   │           ├── main_pages.json
#   │   │           └── route_map.json
#   │   └── module.json5
#   └── .arkts-check/00-scan.json        ← Auto-generated

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: bash scaffold.sh <ProjectName> <com.example.app> [--three-layer]"
  echo "Example: bash scaffold.sh MyApp com.example.myapp"
  echo "Options: --three-layer  Generate Common/Features/Products architecture"
  exit 1
fi

PROJECT_NAME="$1"
BUNDLE_NAME="$2"
THREE_LAYER=false
[ "${3:-}" = "--three-layer" ] && THREE_LAYER=true

ROOT="./$PROJECT_NAME"
ENTRY="$ROOT/entry/src/main"
ETS="$ENTRY/ets"
RESOURCES="$ENTRY/resources/base"

echo "🏗️  Scaffolding HarmonyOS NEXT project: $PROJECT_NAME"
echo "    Bundle: $BUNDLE_NAME"
echo "    Architecture: $([ "$THREE_LAYER" = true ] && echo 'Three-Layer (Common/Features/Products)' || echo 'Standard (entry module)')"

# ── Create directory structure ────────────────────────
mkdir -p "$ETS/pages"
mkdir -p "$ETS/components"
mkdir -p "$ETS/viewmodel"
mkdir -p "$ETS/model"
mkdir -p "$ETS/services"
mkdir -p "$ETS/common/utils"
mkdir -p "$RESOURCES/element"
mkdir -p "$RESOURCES/media"
mkdir -p "$RESOURCES/profile"
mkdir -p "$ENTRY"
mkdir -p "$ROOT/.arkts-check"

if [ "$THREE_LAYER" = true ]; then
  mkdir -p "$ROOT/common/basic/src/main/ets/components"
  mkdir -p "$ROOT/features/home/src/main/ets/views"
  mkdir -p "$ROOT/features/shop/src/main/ets/views"
  mkdir -p "$ROOT/features/user/src/main/ets/views"
  mkdir -p "$ROOT/products/entry"
  # Move entry into products
  rm -rf "$ROOT/entry"
  ENTRY="$ROOT/products/entry/src/main"
  ETS="$ENTRY/ets"
  RESOURCES="$ENTRY/resources/base"
  # Re-create entry structure under products
  mkdir -p "$ETS/pages"
  mkdir -p "$ETS/components"
  mkdir -p "$ETS/viewmodel"
  mkdir -p "$ETS/model"
  mkdir -p "$ETS/services"
  mkdir -p "$ETS/common/utils"
  mkdir -p "$RESOURCES/element"
  mkdir -p "$RESOURCES/media"
  mkdir -p "$RESOURCES/profile"
  mkdir -p "$ENTRY"
fi

# ── module.json5 ─────────────────────────────────────
cat > "$ENTRY/module.json5" << MODULEEOF
{
  "module": {
    "name": "entry",
    "type": "entry",
    "description": "\$string:module_desc",
    "mainElement": "EntryAbility",
    "deviceTypes": ["phone", "tablet"],
    "deliveryWithInstall": true,
    "installationFree": false,
    "pages": "\$profile:main_pages",
    "routerMap": "\$profile:route_map",
    "requestPermissions": [
      { "name": "ohos.permission.INTERNET" }
    ],
    "abilities": [
      {
        "name": "EntryAbility",
        "srcEntry": "./ets/entryability/EntryAbility.ts",
        "description": "\$string:EntryAbility_desc",
        "icon": "\$media:icon",
        "label": "\$string:EntryAbility_label",
        "startWindowIcon": "\$media:icon",
        "startWindowBackground": "\$color:start_window_background",
        "exported": true,
        "skills": [
          {
            "entities": ["entity.system.home"],
            "actions": ["action.system.home"]
          }
        ]
      }
    ]
  }
}
MODULEEOF

# ── main_pages.json ──────────────────────────────────
cat > "$RESOURCES/profile/main_pages.json" << PAGESEOF
{
  "src": ["pages/Index"]
}
PAGESEOF

# ── route_map.json (Navigation) ──────────────────────
cat > "$RESOURCES/profile/route_map.json" << ROUTEEOF
{
  "routerMap": []
}
ROUTEEOF

# ── Index.ets (Navigation skeleton) ──────────────────
cat > "$ETS/pages/Index.ets" << INDEXEOF
@Entry
@Component
struct Index {
  @Provide('pageStack') pageStack: NavPathStack = new NavPathStack()

  build() {
    Navigation(this.pageStack) {
      Column() {
        Text('Hello $PROJECT_NAME')
          .fontSize(30)
          .fontWeight(FontWeight.Bold)
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.Center)
    }
    .navBarWidth('100%')
    .mode(NavigationMode.Stack)
    .hideNavBar(true)
  }
}
INDEXEOF

# ── Component placeholder ────────────────────────────
cat > "$ETS/components/.gitkeep" << 'GITKEEP'
GITKEEP

# ── EntryAbility placeholder ─────────────────────────
mkdir -p "$ETS/entryability"
cat > "$ETS/entryability/EntryAbility.ts" << ABILITYEOF
import { UIAbility, Want, AbilityConstant } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';

const DOMAIN: number = 0x0000;
const TAG: string = 'EntryAbility';

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    hilog.info(DOMAIN, TAG, 'Ability onCreate');
  }

  onDestroy(): void {
    hilog.info(DOMAIN, TAG, 'Ability onDestroy');
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    hilog.info(DOMAIN, TAG, 'Ability onWindowStageCreate');
    windowStage.loadContent('pages/Index', (err) => {
      if (err.code) {
        hilog.error(DOMAIN, TAG, 'Failed to load the content. Cause: %{public}s', JSON.stringify(err));
        return;
      }
      hilog.info(DOMAIN, TAG, 'Succeeded in loading the content.');
    });
  }

  onWindowStageDestroy(): void {
    hilog.info(DOMAIN, TAG, 'Ability onWindowStageDestroy');
  }

  onForeground(): void {
    hilog.info(DOMAIN, TAG, 'Ability onForeground');
  }

  onBackground(): void {
    hilog.info(DOMAIN, TAG, 'Ability onBackground');
  }
}
ABILITYEOF

# ── Three-layer boilerplate (optional) ───────────────
if [ "$THREE_LAYER" = true ]; then
  ROOT_DIR="$ROOT"
  # Common/basic Index.ets
  echo "export * from './src/main/ets/components'" > "$ROOT_DIR/common/basic/Index.ets"
  # Features/home Index.ets
  echo "export * from './src/main/ets/views'" > "$ROOT_DIR/features/home/Index.ets"
  # Features/home HomeView
  cat > "$ROOT_DIR/features/home/src/main/ets/views/HomeView.ets" << 'HOMEEOF'
@Component
export struct HomeView {
  build() {
    Column() { Text('首页').fontSize(20) }
  }
}
HOMEEOF
  # Features/shop
  echo "export * from './src/main/ets/views'" > "$ROOT_DIR/features/shop/Index.ets"
  cat > "$ROOT_DIR/features/shop/src/main/ets/views/ShopView.ets" << 'SHOPEOF'
@Component
export struct ShopView {
  build() {
    Column() { Text('商城').fontSize(20) }
  }
}
SHOPEOF
  # Features/user
  echo "export * from './src/main/ets/views'" > "$ROOT_DIR/features/user/Index.ets"
  cat > "$ROOT_DIR/features/user/src/main/ets/views/UserView.ets" << 'USEREOF'
@Component
export struct UserView {
  build() {
    Column() { Text('我的').fontSize(20) }
  }
}
USEREOF
  # products/entry Index.ets with Tabs
  cat > "$ETS/pages/Index.ets" << 'THREEEOF'
import { HomeView } from 'home';
import { ShopView } from 'shop';
import { UserView } from 'user';

@Entry
@Component
struct Index {
  build() {
    Tabs() {
      TabContent() { HomeView() }.tabBar('首页')
      TabContent() { ShopView() }.tabBar('商城')
      TabContent() { UserView() }.tabBar('我的')
    }
    .barPosition(BarPosition.End)
    .height('100%')
    .width('100%')
  }
}
THREEEOF
fi

# ── Run Step 0 scan ──────────────────────────────────
echo ""
echo "Running Step 0 scan..."
python3 -c "
import json, os
root='$([ "$THREE_LAYER" = true ] && echo "$ROOT_DIR" || echo "$ROOT")'
entry_src=os.path.join(root, 'entry/src/main') if '$THREE_LAYER' == 'false' else os.path.join(root, 'products/entry/src/main')
data={
  'media': os.listdir(os.path.join(entry_src, 'resources/base/media/')) if os.path.exists(os.path.join(entry_src, 'resources/base/media/')) else [],
  'pages': ['pages/Index'],
  'components': [],
  'hasInternetPermission': True,
  'isThreeLayer': True if '$THREE_LAYER' == 'true' else False,
  'timestamp': '$(date -Iseconds)'
}
json.dump(data, open(os.path.join(root, '.arkts-check/00-scan.json'),'w'), ensure_ascii=False, indent=2)
print('✓ 00-scan.json written')
"

echo ""
echo "========================================="
echo "✅ Project scaffolded: $ROOT"
echo "   Architecture: $([ "$THREE_LAYER" = true ] && echo 'Three-Layer' || echo 'Standard')"
echo "   Navigation: NavPathStack skeleton ready"
echo "   Permissions: INTERNET pre-declared"
echo "   Step 0 scan: .arkts-check/00-scan.json generated"
echo ""
echo "Next steps:"
echo "  1. Open $PROJECT_NAME in DevEco Studio"
echo "  2. Configure build-profile.json5 (SDK version, signing)"
echo "  3. Start coding → Step 1 of hard-gate pipeline"
echo "========================================="
