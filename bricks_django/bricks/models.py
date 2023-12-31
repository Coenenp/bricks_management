from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth.models import User

class Color(models.Model):
    ColorID = models.AutoField(primary_key=True)
    BricklinkColorID = models.IntegerField(unique=True)
    LEGOColorID = models.IntegerField(null=True, blank=True)
    WebrickColorID = models.IntegerField(null=True, blank=True)
    RebrickableColorID = models.IntegerField(null=True, blank=True)
    LDrawColorID = models.IntegerField(null=True, blank=True)
    BrickOwlColorID = models.IntegerField(null=True, blank=True)
    GobricksColorID = models.IntegerField(null=True, blank=True)
    Name = models.CharField(max_length=255, unique=True)
    ColorType = models.CharField(max_length=255)
    ColorTimeline = models.CharField(max_length=255, null=True, blank=True)
    RGB = models.CharField(max_length=255)
    HEX = models.CharField(max_length=255)

    def __str__(self):
        return self.Name

class Category(models.Model):
    CategoryID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.Name

class Type(models.Model):
    TypeID = models.AutoField(primary_key=True)
    ParentID = models.IntegerField()
    Name = models.CharField(max_length=255)

    def __str__(self):
        return self.Name  

class Item(models.Model):
    ItemID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=15, unique=True)
    Description = models.CharField(max_length=255)
    ImageReference = models.CharField(max_length=255, null=True, blank=True)
    WebrickImageReference = models.CharField(max_length=255, null=True, blank=True) 
    TypeID = models.ForeignKey(Type, default=1, on_delete=models.CASCADE)
    SubtypeID = models.ForeignKey(Type, on_delete=models.CASCADE, related_name='subtype_items')
    InternalURL = models.ImageField(upload_to='downloaded_images/', null=True, blank=True)
    WebrickInternalURL = models.ImageField(upload_to='downloaded_webrick_images/', null=True, blank=True)  

    def clean(self):
        if self.SubtypeID.ParentID != 0 and self.TypeID.TypeID != self.SubtypeID.ParentID:
            raise ValidationError(f'Invalid subtype for the selected type. Type ID: {self.TypeID.TypeID}, Subtype ID: {self.SubtypeID.TypeID}, Subtype Parent ID: {self.SubtypeID.ParentID}')

        if self.SubtypeID.ParentID == 0:
            raise ValidationError("Invalid subtype for the selected type.")
        
    def __str__(self):
        return f'{self.Name} - {self.Description}'

class ItemAlias(models.Model):
    AliasID = models.AutoField(primary_key=True)
    Item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='aliases')
    AliasName = models.CharField(max_length=15)

    class Meta:
        verbose_name_plural = 'aliases'
        unique_together = ('Item', 'AliasName')

    def __str__(self):
        return f'{self.AliasName} - {self.Item}'

class Part(models.Model):
    PartID = models.AutoField(primary_key=True)
    ItemID = models.ForeignKey(Item, on_delete=models.CASCADE)
    ColorID = models.ForeignKey(Color, on_delete=models.CASCADE)
    ImageReference = models.CharField(max_length=255, null=True, blank=True)
    InternalURL = models.ImageField(upload_to='downloaded_part_images/', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Add the unique_together constraint
    class Meta:
        unique_together = ('ItemID', 'ColorID')
    
    def __str__(self):
        return f'{self.ItemID} - {self.ColorID}'

class List(models.Model):
    ListID = models.AutoField(primary_key=True)
    CategoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    Name = models.CharField(max_length=255, unique=True)
    Description = models.CharField(max_length=255)
    
    def __str__(self):
        return self.Name

class ListPart(models.Model):
    ListPartID = models.AutoField(primary_key=True)
    ListID = models.ForeignKey(List, on_delete=models.CASCADE)
    PartID = models.ForeignKey(Part, on_delete=models.CASCADE)
    Quantity = models.IntegerField(validators=[MinValueValidator(1)])
    date_updated = models.DateTimeField(default=timezone.now)
    
    # Add the unique_together constraint
    class Meta:
        unique_together = ('ListID', 'PartID')
    def __str__(self):
        return f'{self.ListID} - {self.PartID} - {self.Quantity}'

class SetPart(models.Model):
    SetPartID = models.AutoField(primary_key=True)
    ItemID = models.ForeignKey(Item, on_delete=models.CASCADE)
    ColorID = models.ForeignKey(Color, on_delete=models.CASCADE)
    ImageReference = models.CharField(max_length=255, null=True, blank=True) 
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Add the unique_together constraint
    class Meta:
        unique_together = ('ItemID', 'ColorID')
    
    def __str__(self):
        return f'{self.ItemID} - {self.ColorID}'


class SetList(models.Model):
    YEAR_CHOICES = [(r, r) for r in range(1950, timezone.now().year + 1)]
    
    SetListID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=255, unique=True)
    Description = models.CharField(max_length=255)
    Information = models.TextField(null=True, blank=True)
    ImageReference = models.CharField(max_length=255, null=True, blank=True) 
    Year = models.IntegerField(choices=YEAR_CHOICES, default=timezone.now().year)
    BuildInstructions = models.CharField(max_length=255, null=True, blank=True) 
    LEGOReference = models.CharField(max_length=255, null=True, blank=True) 
    ToysPeriodReference = models.CharField(max_length=255, null=True, blank=True) 
    
    def __str__(self):
        return self.Name

class SetListPart(models.Model):
    SetListPartID = models.AutoField(primary_key=True)
    SetListID = models.ForeignKey(SetList, on_delete=models.CASCADE)
    SetPartID = models.ForeignKey(SetPart, on_delete=models.CASCADE)
    Quantity = models.IntegerField(validators=[MinValueValidator(1)])
    date_updated = models.DateTimeField(default=timezone.now)
    
    # Add the unique_together constraint
    class Meta:
        unique_together = ('SetListID', 'SetPartID')

    def __str__(self):
        return f'{self.SetListID} - {self.SetPartID} - {self.Quantity}'

