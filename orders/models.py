from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F
from inventory.models import Product
from django.utils import timezone

class Order(models.Model):
    """نموذج للطلبات"""
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        REJECTED = 'REJECTED', _('Rejected')
    
    order_number = models.CharField(max_length=20, unique=True, verbose_name=_('Order Number'))
    client = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='orders', verbose_name=_('Client'))
    status = models.CharField(max_length=15, choices=OrderStatus.choices, default=OrderStatus.PENDING, verbose_name=_('Status'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_orders', verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.client.username}"
    
    @property
    def total_amount(self):
        """حساب المبلغ الإجمالي للطلب"""
        return self.items.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or 0
    
    @property
    def total_items(self):
        """حساب العدد الإجمالي للعناصر في الطلب"""
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0
    
    def save(self, *args, **kwargs):
        """إنشاء رقم طلب فريد إذا لم يكن موجودًا"""
        if not self.order_number:
            prefix = 'ORD'
            timestamp = timezone.now().strftime('%Y%m%d%H%M')
            self.order_number = f"{prefix}{timestamp}"
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']


class OrderItem(models.Model):
    """نموذج لعناصر الطلب"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_('Order'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name=_('Product'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Price'))
    notes = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Notes'))
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.order_number}"
    
    @property
    def subtotal(self):
        """حساب المبلغ الفرعي للعنصر"""
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        """تعيين السعر من المنتج إذا لم يتم تحديده"""
        if not self.price:
            self.price = self.product.price
        
        # إذا كان الطلب مكتمل، قم بتقليل المخزون
        if self.order.status == Order.OrderStatus.COMPLETED and not self.id:
            from inventory.models import StockMovement
            # إنشاء حركة مخزون جديدة
            StockMovement.objects.create(
                product=self.product,
                quantity=self.quantity,
                movement_type=StockMovement.MovementType.REDUCTION,
                reference=f"Order #{self.order.order_number}",
                created_by=self.order.created_by
            )
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        unique_together = ('order', 'product')
# Create your models here.
