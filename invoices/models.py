# في ملف invoices/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from orders.models import Order

class Invoice(models.Model):
    """نموذج للفواتير"""
    class InvoiceStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PAID = 'PAID', _('Paid')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    invoice_number = models.CharField(max_length=20, unique=True, verbose_name=_('Invoice Number'))
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice', verbose_name=_('Order'))
    status = models.CharField(max_length=10, choices=InvoiceStatus.choices, default=InvoiceStatus.PENDING, verbose_name=_('Status'))
    issue_date = models.DateField(default=timezone.now, verbose_name=_('Issue Date'))
    due_date = models.DateField(blank=True, null=True, verbose_name=_('Due Date'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_('Tax Rate (%)'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Discount'))
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='invoices', verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    def __str__(self):
        return f"Invoice #{self.invoice_number} for Order #{self.order.order_number}"
    
    @property
    def subtotal(self):
        """حساب المبلغ الفرعي للفاتورة (بدون ضريبة وخصم)"""
        return self.order.total_amount
    
    @property
    def tax_amount(self):
        """حساب مبلغ الضريبة"""
        return self.subtotal * (self.tax_rate / 100)
    
    @property
    def total_amount(self):
        """حساب المبلغ الإجمالي للفاتورة (بعد الضريبة والخصم)"""
        return self.subtotal + self.tax_amount - self.discount
    
    def save(self, *args, **kwargs):
        """إنشاء رقم فاتورة فريد إذا لم يكن موجودًا"""
        if not self.invoice_number:
            prefix = 'INV'
            timestamp = timezone.now().strftime('%Y%m%d%H%M')
            self.invoice_number = f"{prefix}{timestamp}"
        
        # تعيين تاريخ الاستحقاق كـ 30 يومًا بعد تاريخ الإصدار إذا لم يتم تحديده
        if not self.due_date:
            self.due_date = self.issue_date + timezone.timedelta(days=30)
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        ordering = ['-issue_date']


class Payment(models.Model):
    """نموذج لمدفوعات الفواتير"""
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', _('Cash')
        BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
        CREDIT_CARD = 'CREDIT_CARD', _('Credit Card')
        CHEQUE = 'CHEQUE', _('Cheque')
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name=_('Invoice'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    method = models.CharField(max_length=15, choices=PaymentMethod.choices, verbose_name=_('Payment Method'))
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Reference'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))
    payment_date = models.DateField(default=timezone.now, verbose_name=_('Payment Date'))
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='recorded_payments', verbose_name=_('Recorded By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    def __str__(self):
        return f"Payment of {self.amount} for Invoice #{self.invoice.invoice_number}"
    
    def save(self, *args, **kwargs):
        """تحديث حالة الفاتورة إذا تم دفع المبلغ بالكامل"""
        super().save(*args, **kwargs)
        
        # حساب إجمالي المدفوعات للفاتورة
        total_paid = self.invoice.payments.aggregate(total=models.Sum('amount'))['total'] or 0
        
        # تحديث حالة الفاتورة إذا تم دفع المبلغ بالكامل
        if total_paid >= self.invoice.total_amount and self.invoice.status != Invoice.InvoiceStatus.PAID:
            self.invoice.status = Invoice.InvoiceStatus.PAID
            self.invoice.save()
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-payment_date']