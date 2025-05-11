from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'pk': self.pk})
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    sku = models.CharField(max_length=20, unique=True, verbose_name=_('SKU'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name=_('Category'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Cost Price'))
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Selling Price'))
    reorder_level = models.PositiveIntegerField(default=10, verbose_name=_('Reorder Level'))
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name=_('Image'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.pk})
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level
    
    @property
    def profit_margin(self):
        if self.cost_price:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['name']


class StockMovement(models.Model):
    MOVEMENT_IN = 'IN'
    MOVEMENT_OUT = 'OUT'
    MOVEMENT_ADJUSTMENT = 'ADJUSTMENT'
    
    MOVEMENT_TYPES = [
        (MOVEMENT_IN, _('Stock In')),
        (MOVEMENT_OUT, _('Stock Out')),
        (MOVEMENT_ADJUSTMENT, _('Stock Adjustment')),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements', verbose_name=_('Product'))
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name=_('Movement Type'))
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Reference'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        if is_new:
            if self.movement_type == self.MOVEMENT_IN:
                self.product.quantity += self.quantity
            elif self.movement_type == self.MOVEMENT_OUT:
                if self.product.quantity >= self.quantity:
                    self.product.quantity -= self.quantity
                else:
                    raise ValueError(_('Insufficient stock available'))
            elif self.movement_type == self.MOVEMENT_ADJUSTMENT:
                self.product.quantity = self.quantity
            
            self.product.save()
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('Stock Movement')
        verbose_name_plural = _('Stock Movements')
        ordering = ['-created_at']