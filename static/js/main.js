// تنفيذ عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded!');
    
    // إخفاء تنبيهات النجاح بعد 5 ثوان
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-success');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// وظيفة للبحث في الجداول
function tableSearch(inputId, tableId) {
    var input = document.getElementById(inputId);
    var filter = input.value.toUpperCase();
    var table = document.getElementById(tableId);
    var tr = table.getElementsByTagName("tr");
    
    for (var i = 1; i < tr.length; i++) {
        var found = false;
        var td = tr[i].getElementsByTagName("td");
        
        for (var j = 0; j < td.length; j++) {
            if (td[j]) {
                var txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
        }
        
        if (found) {
            tr[i].style.display = "";
        } else {
            tr[i].style.display = "none";
        }
    }
}