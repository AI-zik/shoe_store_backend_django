import stripe
from decimal import Decimal
from django.db import models
from django.conf import settings
from users.models import User
from shoes.models import AvailableShoeSize


# each transaction
class Transaction(models.Model):
    id = models.AutoField(primary_key=True, null=False, auto_created=True)
    payment_intent_id = models.CharField(max_length=120, unique=True)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "transaction"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.time}"

# each shoe model bought and the quantity
class Purchase(models.Model):
    id= models.AutoField(primary_key=True, null=False, auto_created=True)
    quantity = models.PositiveSmallIntegerField(null=False, blank=False, default=0)
    shoe = models.ForeignKey(AvailableShoeSize, on_delete=models.DO_NOTHING)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    discount = models.DecimalField(max_digits=4, decimal_places=1, default= Decimal('0.00'))
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="items")

    class Meta:
        db_table = "purchase"
        unique_together = ["transaction", "shoe"]

    def __str__(self):
        return f"{self.transaction.user} {self.shoe.name}"