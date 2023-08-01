# Generated by Django 3.2.5 on 2022-01-19 05:43

import ckeditor.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import shop.models
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('slug', models.SlugField(max_length=255)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('name', models.CharField(blank=True, default='', max_length=20)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Fresh'), (10, 'Paid')], default=0)),
                ('discount_label', models.CharField(blank=True, max_length=120, null=True)),
                ('discount_amount', models.IntegerField(default=0)),
                ('total_without_tax', models.IntegerField(default=0)),
                ('tax', models.IntegerField(default=0)),
                ('total_price', models.IntegerField(default=0)),
                ('shipping_tax_rate', models.IntegerField(default=0)),
                ('shipping_amount', models.IntegerField(default=0)),
                ('shipping_tax', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CartProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('quantity', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('unit_price', models.IntegerField(default=0, verbose_name='individual item rate')),
                ('amount', models.IntegerField(default=0, verbose_name='individual rate * quantity')),
                ('discount_label', models.CharField(blank=True, max_length=200, null=True, verbose_name='discount percentage')),
                ('discount_amount', models.IntegerField(default=0, verbose_name='discount amount')),
                ('total_without_tax', models.IntegerField(default=0, verbose_name='total without tax')),
                ('tax', models.IntegerField(default=0)),
                ('total_price', models.IntegerField(default=0, verbose_name='total without tax + tax')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('slug', models.SlugField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('priority', models.PositiveSmallIntegerField(default=1, help_text='1 is higher than 2')),
                ('size_chart', ckeditor.fields.RichTextField(blank=True)),
                ('shipping_and_returns', ckeditor.fields.RichTextField(blank=True)),
                ('placeholder', models.TextField(blank=True, max_length=528, null=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='DiscountCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('slug', models.SlugField(max_length=255)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('category_type', models.PositiveSmallIntegerField(choices=[(0, 'Applied to All Users'), (10, 'Applied to User Groups #coming soon')], default=0)),
                ('min_cart_amount', models.FloatField(default=0)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Percentage'), (2, 'Absolute Rupees')], default=1)),
                ('value', models.FloatField(blank=True, null=True, verbose_name='Percentage or Fix amount of discount')),
                ('start_date_time', models.DateTimeField()),
                ('end_date_time', models.DateTimeField()),
            ],
            options={
                'verbose_name_plural': 'Discount Categories',
            },
        ),
        migrations.CreateModel(
            name='DiscountCoupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('code', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=255)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('discount_value', models.FloatField(default=0)),
                ('discount_type', models.PositiveSmallIntegerField(choices=[(1, 'Percentage'), (2, 'Absolute Rupees')])),
                ('max_discount', models.FloatField(default=0)),
                ('min_cart_amount', models.FloatField(default=0)),
                ('summary', models.CharField(blank=True, max_length=300, null=True)),
                ('discount_image', models.ImageField(blank=True, null=True, upload_to='discount_image')),
                ('coupon_type', models.PositiveSmallIntegerField(choices=[(1, 'First time purchases'), (2, 'All purchases')], default=2, help_text='Apply discount on all purchases or on first purchase')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalCart',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('modified', models.DateTimeField(blank=True, editable=False)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('name', models.CharField(blank=True, default='', max_length=20)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Fresh'), (10, 'Paid')], default=0)),
                ('discount_label', models.CharField(blank=True, max_length=120, null=True)),
                ('discount_amount', models.IntegerField(default=0)),
                ('total_without_tax', models.IntegerField(default=0)),
                ('tax', models.IntegerField(default=0)),
                ('total_price', models.IntegerField(default=0)),
                ('shipping_tax_rate', models.IntegerField(default=0)),
                ('shipping_amount', models.IntegerField(default=0)),
                ('shipping_tax', models.IntegerField(default=0)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical cart',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalCartProducts',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('modified', models.DateTimeField(blank=True, editable=False)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('quantity', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('unit_price', models.IntegerField(default=0, verbose_name='individual item rate')),
                ('amount', models.IntegerField(default=0, verbose_name='individual rate * quantity')),
                ('discount_label', models.CharField(blank=True, max_length=200, null=True, verbose_name='discount percentage')),
                ('discount_amount', models.IntegerField(default=0, verbose_name='discount amount')),
                ('total_without_tax', models.IntegerField(default=0, verbose_name='total without tax')),
                ('tax', models.IntegerField(default=0)),
                ('total_price', models.IntegerField(default=0, verbose_name='total without tax + tax')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical cart products',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOrder',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('modified', models.DateTimeField(blank=True, editable=False)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('name', models.CharField(max_length=220)),
                ('email', models.CharField(max_length=255)),
                ('mobile', models.BigIntegerField()),
                ('invoice_number', models.CharField(blank=True, max_length=20, null=True)),
                ('discount_label', models.CharField(blank=True, max_length=200, null=True)),
                ('discount_amount', models.IntegerField(default=0)),
                ('total_without_tax', models.IntegerField(default=0)),
                ('tax', models.IntegerField(default=0)),
                ('total_price', models.IntegerField(default=0)),
                ('shipping_address', models.CharField(blank=True, max_length=512, null=True)),
                ('billing_address', models.CharField(blank=True, max_length=512, null=True)),
                ('shipping_tax_rate', models.IntegerField(default=0)),
                ('shipping_amount', models.IntegerField(default=0)),
                ('shipping_tax', models.IntegerField(default=0)),
                ('order_status', models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (10, 'Placed'), (20, 'Processing'), (30, 'Shipped'), (40, 'Complete'), (50, 'Canceled')], default=0)),
                ('payment_status', models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (10, 'Processing'), (20, 'Approved'), (30, 'Reversed'), (40, 'Failed')], default=0)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical order',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOrderPayment',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('gateway', models.SmallIntegerField(choices=[(1, 'Razorpay')])),
                ('gateway_order_id', models.CharField(blank=True, max_length=120, null=True)),
                ('gateway_payment_id', models.CharField(blank=True, max_length=120, null=True)),
                ('gateway_signature', models.CharField(blank=True, max_length=120, null=True, verbose_name='The transaction signature')),
                ('is_success', models.SmallIntegerField(choices=[(2, 'Yes'), (1, 'No')], default=1)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical order payment',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOrderProducts',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('manufacturer', models.CharField(blank=True, max_length=512, null=True)),
                ('name', models.CharField(blank=True, max_length=512, null=True)),
                ('option_name', models.CharField(blank=True, max_length=512, null=True)),
                ('quantity', models.IntegerField()),
                ('unit_price', models.IntegerField()),
                ('amount', models.IntegerField(default=0, verbose_name='individual rate * quantity')),
                ('discount_label', models.CharField(blank=True, max_length=200, null=True)),
                ('discount_amount', models.IntegerField(default=0)),
                ('total_without_tax', models.IntegerField(default=0)),
                ('tax', models.IntegerField(default=0)),
                ('total_price', models.IntegerField(default=0)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical order products',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProductOption',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('modified', models.DateTimeField(blank=True, editable=False)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('sku', models.CharField(blank=True, max_length=100, null=True)),
                ('quantity', models.IntegerField(default=0)),
                ('priority', models.IntegerField(default=1)),
                ('list_price', models.FloatField(default=0, verbose_name='MRP(Including Tax)')),
                ('selling_price', models.FloatField(default=0, verbose_name='Selling Price(After Discounts,Including Tax)')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical product option',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProductOptionAttributes',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('modified', models.DateTimeField(blank=True, editable=False)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('value', models.CharField(blank=True, max_length=120, null=True)),
                ('label', models.CharField(blank=True, max_length=120, null=True)),
                ('priority', models.PositiveSmallIntegerField(default=99)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical product option attributes',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HomepageCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('enabled', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=120)),
                ('subtitle', models.CharField(blank=True, max_length=120)),
                ('button_text', models.CharField(max_length=120)),
                ('priority', models.PositiveSmallIntegerField(default=1, help_text='1 is higher than 2')),
                ('image', models.ImageField(help_text='minimum width: 775px', max_length=250, null=True, upload_to='upload/homepage/')),
            ],
            options={
                'verbose_name_plural': 'Homepage Categories',
            },
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('slug', models.SlugField(max_length=255)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('name', models.CharField(max_length=220)),
                ('email', models.CharField(max_length=255)),
                ('mobile', models.BigIntegerField()),
                ('invoice_number', models.CharField(blank=True, max_length=20, null=True)),
                ('discount_label', models.CharField(blank=True, max_length=200, null=True)),
                ('discount_amount', models.IntegerField(default=0)),
                ('total_without_tax', models.IntegerField(default=0)),
                ('tax', models.IntegerField(default=0)),
                ('total_price', models.IntegerField(default=0)),
                ('shipping_address', models.CharField(blank=True, max_length=512, null=True)),
                ('billing_address', models.CharField(blank=True, max_length=512, null=True)),
                ('shipping_tax_rate', models.IntegerField(default=0)),
                ('shipping_amount', models.IntegerField(default=0)),
                ('shipping_tax', models.IntegerField(default=0)),
                ('order_status', models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (10, 'Placed'), (20, 'Processing'), (30, 'Shipped'), (40, 'Complete'), (50, 'Canceled')], default=0)),
                ('payment_status', models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (10, 'Processing'), (20, 'Approved'), (30, 'Reversed'), (40, 'Failed')], default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('street', models.CharField(max_length=512)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('pincode', models.CharField(max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='OrderPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gateway', models.SmallIntegerField(choices=[(1, 'Razorpay')])),
                ('gateway_order_id', models.CharField(blank=True, max_length=120, null=True)),
                ('gateway_payment_id', models.CharField(blank=True, max_length=120, null=True)),
                ('gateway_signature', models.CharField(blank=True, max_length=120, null=True, verbose_name='The transaction signature')),
                ('is_success', models.SmallIntegerField(choices=[(2, 'Yes'), (1, 'No')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='OrderProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manufacturer', models.CharField(blank=True, max_length=512, null=True)),
                ('name', models.CharField(blank=True, max_length=512, null=True)),
                ('option_name', models.CharField(blank=True, max_length=512, null=True)),
                ('quantity', models.IntegerField()),
                ('unit_price', models.IntegerField()),
                ('amount', models.IntegerField(default=0, verbose_name='individual rate * quantity')),
                ('discount_label', models.CharField(blank=True, max_length=200, null=True)),
                ('discount_amount', models.IntegerField(default=0)),
                ('total_without_tax', models.IntegerField(default=0)),
                ('tax', models.IntegerField(default=0)),
                ('total_price', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='OrderShipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('shipment_company', models.CharField(blank=True, max_length=200, null=True)),
                ('shipped_on', models.DateField(blank=True, null=True)),
                ('tracking_no', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderShipmentAttributes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('key', models.PositiveSmallIntegerField(choices=[(0, 'Provider'), (1, 'Order Id'), (2, 'Shipment Id'), (3, 'AWB No'), (4, 'Courier Name'), (5, 'Length in cms'), (6, 'Width in cms'), (7, 'Height in cms'), (8, 'Weight in grams'), (10, 'Courier id'), (11, 'Shipment order status'), (12, 'Additional info of shipment Order'), (13, 'Payment type'), (14, 'Shipment Order Shlip link')])),
                ('value', models.CharField(max_length=300)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProducOptionStatictAttributes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('name', models.CharField(max_length=200)),
                ('value', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('slug', models.SlugField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('summary', models.CharField(blank=True, max_length=512, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('hsn', models.CharField(blank=True, max_length=100, null=True)),
                ('sku', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.SmallIntegerField(choices=[(1, 'Enabled'), (0, 'Disabled')], default=0)),
                ('return_days', models.SmallIntegerField(default=0)),
                ('youtube_link', models.URLField(blank=True, null=True)),
                ('weight_gram', models.PositiveSmallIntegerField(default=0)),
                ('width', models.CharField(blank=True, max_length=120, null=True)),
                ('height', models.CharField(blank=True, max_length=120, null=True)),
                ('length', models.CharField(blank=True, max_length=120, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductAttributes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('name', models.CharField(max_length=200)),
                ('value', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('sku', models.CharField(blank=True, max_length=100, null=True)),
                ('quantity', models.IntegerField(default=0)),
                ('priority', models.IntegerField(default=1)),
                ('list_price', models.FloatField(default=0, verbose_name='MRP(Including Tax)')),
                ('selling_price', models.FloatField(default=0, verbose_name='Selling Price(After Discounts,Including Tax)')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductOptionAttributes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('value', models.CharField(blank=True, max_length=120, null=True)),
                ('label', models.CharField(blank=True, max_length=120, null=True)),
                ('priority', models.PositiveSmallIntegerField(default=99)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductOptionImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('image', models.ImageField(blank=True, max_length=250, null=True, upload_to=shop.models.product_image_directory)),
                ('is_common', models.BooleanField(default=False, verbose_name='Is this image common for all options')),
                ('priority', models.IntegerField(default=1)),
            ],
            options={
                'ordering': ('priority',),
            },
        ),
        migrations.CreateModel(
            name='TaxClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name_plural': 'Tax Classes',
            },
        ),
        migrations.CreateModel(
            name='TaxClassBracket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_rate', models.FloatField(default=0)),
                ('max_rate', models.FloatField(default=0)),
                ('cgst_rate', models.FloatField(default=0)),
                ('sgst_rate', models.FloatField(default=0)),
                ('igst_rate', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('object_status', models.SmallIntegerField(choices=[(0, 'Deleted'), (1, 'Active')], default=1)),
                ('product_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.productoption')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
