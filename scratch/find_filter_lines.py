import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

funcs = [
    'syncTabUI', 'toggleMultiselect', 'toggleOption', 'updateSelectionFromCheckboxes',
    'updateMultiselectPlaceholder', 'applyGia', 'toggleSearchClearBtn', 'clearSearchInput',
    'onSearchInput', 'toggleSearchBar', 'getFiltered', 'matchCriteriaHelper',
    'renderCriteriaCheckboxes', 'updateStaticTabsVisibility', 'toggleFilter', 'closeFilter',
    'buildDistrictTabs', 'buildWardTabs', 'buildDuongTabs', 'buildHuongTabs',
    'updateFilterSummary', 'resetFilters', 'clearAllFilters', 'toggleFavFilter',
    'applyFilter', 'checkPoolFallbackSearch', 'searchPoolRows'
]

for name in funcs:
    for idx, line in enumerate(lines):
        if f"function {name}" in line or f"{name} = function" in line:
            print(f"{name}: line {idx+1}")
            break
