# Hướng dẫn debug Select All / Deselect All buttons

## Bước 1: Mở browser và truy cập
- Mở http://127.0.0.1:8000/
- Mở Developer Tools (F12)
- Chuyển sang tab Console

## Bước 2: Kiểm tra elements có tồn tại
```javascript
// Check if buttons exist
console.log('Select All button:', document.getElementById('select-all-layers'));
console.log('Deselect All button:', document.getElementById('deselect-all-layers'));
console.log('All control buttons:', document.querySelectorAll('.control-btn'));
```

## Bước 3: Kiểm tra business map object
```javascript
// Check if map is initialized
console.log('Business map object:', window.businessMap);
console.log('Categories:', window.businessMap.categories);
```

## Bước 4: Test functions manually
```javascript
// Test select all function
window.businessMap.testSelectAll();

// Test deselect all function  
window.businessMap.testDeselectAll();
```

## Bước 5: Test buttons manually
```javascript
// Test button click events manually
document.getElementById('select-all-layers').click();
document.getElementById('deselect-all-layers').click();
```

## Bước 6: Add manual event listeners (if needed)
```javascript
// Add manual event listeners
document.getElementById('select-all-layers').addEventListener('click', function() {
    console.log('Manual: Select All clicked');
    window.businessMap.selectAllLayers(true);
});

document.getElementById('deselect-all-layers').addEventListener('click', function() {
    console.log('Manual: Deselect All clicked');  
    window.businessMap.selectAllLayers(false);
});
```

## Debug output mong đợi:
- "Setting up layer control buttons..." 
- "Select All button: <button element>"
- "Deselect All button: <button element>"
- "Select All button event listener added"
- "Deselect All button event listener added"

## Nếu buttons vẫn không hoạt động:
1. Kiểm tra console có lỗi JavaScript nào không
2. Kiểm tra buttons có được render đúng không
3. Chạy các test functions manual ở trên
4. Kiểm tra CSS có che phủ buttons không