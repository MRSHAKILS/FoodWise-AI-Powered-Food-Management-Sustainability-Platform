from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from food.models import FoodItem, ConsumptionLog

User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            "full_name",
            "email",
            "password",
            "confirm_password",
            "household_size",
            "dietary_preferences",
            "location",
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            raise forms.ValidationError("Passwords do not match!")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]   # username = email
        user.password = make_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile with budget and dietary preferences"""
    class Meta:
        model = User
        fields = ['full_name', 'email', 'household_size', 'dietary_preferences', 'location', 'budget_limit']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500'}),
            'household_size': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'min': '1'}),
            'dietary_preferences': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'placeholder': 'e.g., Vegetarian, Vegan, Gluten-free'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500'}),
            'budget_limit': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'step': '0.01', 'placeholder': 'Monthly budget'}),
        }
        labels = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'household_size': 'Household Size',
            'dietary_preferences': 'Dietary Preferences',
            'location': 'Location',
            'budget_limit': 'Monthly Budget Limit ($)',
        }


class FoodItemForm(forms.ModelForm):
    """Form for adding/editing food items in inventory"""
    class Meta:
        model = FoodItem
        fields = ['name', 'quantity', 'unit', 'category', 'purchase_date', 'expiration_date', 'price', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'placeholder': 'e.g., Tomatoes'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'step': '0.01', 'min': '0'}),
            'unit': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'placeholder': 'e.g., kg, units, liters'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500'}),
            'purchase_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'type': 'date'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'rows': '3', 'placeholder': 'Additional notes...'}),
        }
        labels = {
            'name': 'Item Name',
            'quantity': 'Quantity',
            'unit': 'Unit',
            'category': 'Category',
            'purchase_date': 'Purchase Date',
            'expiration_date': 'Expiration Date',
            'price': 'Price ($)',
            'notes': 'Notes',
        }


class ConsumptionLogForm(forms.ModelForm):
    """Form for logging daily food consumption"""
    class Meta:
        model = ConsumptionLog
        fields = ['item_name', 'quantity', 'unit', 'category', 'consumption_date', 'notes']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'placeholder': 'e.g., Milk'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'step': '0.01', 'min': '0'}),
            'unit': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'placeholder': 'e.g., liters, kg, units'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500'}),
            'consumption_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500', 'rows': '3', 'placeholder': 'Additional notes...'}),
        }
        labels = {
            'item_name': 'Item Name',
            'quantity': 'Quantity',
            'unit': 'Unit',
            'category': 'Category',
            'consumption_date': 'Consumption Date',
            'notes': 'Notes',
        }
