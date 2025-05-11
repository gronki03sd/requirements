from django import forms
from .models import Product, Category, StockMovement

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'description', 'cost_price', 
                  'selling_price', 'quantity', 'reorder_level', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'reference', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # إذا كان هناك منتج محدد مسبقًا في URL
        if 'initial' in kwargs and 'product' in kwargs['initial']:
            self.fields['product'].widget.attrs['readonly'] = True