def get_dashboard_stats():
    """استخراج البيانات الأساسية للوحة التحكم الرئيسية"""
    return {
        'total_products': 0,
        'low_stock_count': 0,
        'stock_value': 0,
        'today_orders': 0,
        'orders_this_month': 0,
        'today_sales': 0,
        'monthly_sales': 0
    }

def get_monthly_sales_data(year=None):
    """استخراج بيانات المبيعات الشهرية للسنة المحددة"""
    return {
        'labels': ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
        'data': [0, 0, 0, 0, 0, 0]
    }