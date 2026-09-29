# club/forms.py
from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
  class Meta:
    model = Member
    fields = ["email", "full_name", "phone", "dob"]
    widgets = {
      "dob": forms.DateInput(attrs={"type": "date"}),
    }
    labels = {
      "phone": "Phone (optional)",
      "dob": "DOB (optional)",
    }

  def validate_unique(self):
    # A matching email is expected for returning members — the view looks up
    # the existing Member via get_or_create rather than treating this as an error.
    pass