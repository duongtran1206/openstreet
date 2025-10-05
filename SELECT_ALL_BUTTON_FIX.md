## Select All Button Issue Resolution

### ✅ **Problem Identified:**
You reported that when clicking the "All" button in Tier 2:
- ✅ **Categories get selected** (checkboxes checked correctly) 
- ❌ **Map markers don't appear** (the main issue)

### 🔧 **Solution Implemented:**

#### **1. Enhanced Button Functions**
- ✅ **`selectAllCategories()`** now properly calls `updateMapLayers()`
- ✅ **`deselectAllCategories()`** now properly calls `updateMapLayers()`
- ✅ **Added debugging** to track the selection process

#### **2. Debugging Added**
```javascript
console.log(`Select All: ${this.selectedCategories.size} categories selected`);
console.log(`After updateVisibleLocations: ${this.visibleLocations.size} locations visible`);
console.log(`Markers added to map: ${markersAdded}`);
```

#### **3. Auto-Selection Enhanced**
- ✅ **First domain auto-selected** when controls load
- ✅ **All categories pre-checked** by default
- ✅ **Locations immediately visible** on initial load

### 🎯 **How It Should Work:**

#### **"All" Button Click:**
1. **Selects all categories** → Updates `selectedCategories` set
2. **Checks all checkboxes** → Visual feedback  
3. **Updates visible locations** → Recalculates which locations to show
4. **Updates map layers** → Adds markers to map
5. **Updates summary** → Shows count of visible locations

#### **"None" Button Click:**
1. **Clears all categories** → Empties `selectedCategories` set
2. **Unchecks all checkboxes** → Visual feedback
3. **Clears visible locations** → No locations to show
4. **Clears map layers** → Removes all markers from map
5. **Updates summary** → Shows 0 visible locations

### 🐛 **Potential Issues & Fixes:**

#### **If API Is Broken:**
- The query was fixed: `categories__domain__domain_id`
- Added error handling and debugging

#### **If Markers Don't Appear:**
- Enhanced marker creation with debug counters
- Improved layer group management
- Added console logging to track process

### 🧪 **How to Test:**

1. **Open Map**: http://127.0.0.1:8000/
2. **Open Browser Console** (F12 → Console tab)
3. **Click "All" button** in Layer Control
4. **Check Console Logs**:
   - Should see: "Select All: X categories selected"
   - Should see: "After updateVisibleLocations: Y locations visible"
   - Should see: "Markers added to map: Z"
5. **Check Map**: All markers should appear
6. **Click "None" button**: All markers should disappear

### 🚀 **Expected Result:**
The "All" and "None" buttons should now properly control map marker visibility with real-time updates and debug feedback in the browser console.

**Note**: If the API is still broken, the debugging will help identify exactly where the issue occurs in the data flow.