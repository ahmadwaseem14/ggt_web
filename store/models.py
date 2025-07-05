from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, FileExtensionValidator, ValidationError
from PIL import Image
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
import os
from django.utils.text import slugify

def validate_square_image(image):
    """Validate that the image is square (1:1 ratio)"""
    img = Image.open(image)
    width, height = img.size
    if width != height:
        raise ValidationError(
            f"Image must be square (1:1 ratio). Current dimensions: {width}x{height}"
        )

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-date_subscribed']
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'

class ProductImage(models.Model):
    """Model to store images for all products"""
    image = models.ImageField(
        upload_to='product_images/',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
            validate_square_image
        ],
        null=False,
        blank=False,
        help_text="Product image (required, must be square 1:1 ratio)"
    )
    alt_text = models.CharField(
        max_length=100, 
        blank=False,
        help_text="Alternative text for the image"
    )
    is_primary = models.BooleanField(
        default=False, 
        help_text="Set as primary image?"
    )
    
    # Generic foreign key fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-uploaded_at']
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"Image for {self.content_object}"
    
    def save(self, *args, **kwargs):
        """Override save to ensure only one primary image per product"""
        if self.is_primary:
            # Set all other images of this product to not primary
            ProductImage.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id,
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)

class BaseProduct(models.Model):
    # ... existing fields
    description = models.TextField(
        null=False, 
        default="This is a high-quality product with excellent performance and reliability. Perfect for both professional and personal use.",
        help_text="Detailed description of the product"
    )
    
    class Meta:
        abstract = True

class GPU(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="Full product name (e.g., ASUS ROG STRIX GeForce RTX 3080 OC 10GB)"
    )
    
    # Brand (Choices)
    BRAND_CHOICES = [
        ('nvidia', 'NVIDIA'),
        ('amd', 'AMD'),
        ('intel', 'Intel'),
        ('other', 'Other'),
    ]
    brand = models.CharField(
        max_length=20, 
        choices=BRAND_CHOICES, 
        help_text="The brand of the GPU (e.g., NVIDIA, AMD)"
    )
    
    model = models.CharField(max_length=100, help_text="The model of the GPU (e.g., RTX 3080, RX 6800 XT)")
    
    # SKU (Automatically Generated as a Number)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False, 
        help_text="Automatically generated numeric SKU for the GPU"
    )
    
    # VRAM (Choices)
    VRAM_CHOICES = [
        (1, '1 GB'),
        (2, '2 GB'),
        (4, '4 GB'),
        (6, '6 GB'),
        (8, '8 GB'),
        (10, '10 GB'),
        (12, '12 GB'),
        (16, '16 GB'),
        (24, '24 GB'),
    ]
    vram = models.PositiveIntegerField(
        choices=VRAM_CHOICES, 
        help_text="The amount of VRAM in GB (e.g., 10 GB)"
    )
    
    # Memory Type (Choices)
    MEMORY_TYPE_CHOICES = [
        ('gddr3', 'GDDR3'),
        ('gddr4', 'GDDR4'),
        ('gddr5', 'GDDR5'),
        ('gddr5x', 'GDDR5X'),
        ('gddr6', 'GDDR6'),
        ('gddr6x', 'GDDR6X'),
        ('hbm1', 'HBM1'),
        ('hbm2', 'HBM2'),
        ('hbm2e', 'HBM2e'),
        ('hbm3', 'HBM3'),
    ]
    memory_type = models.CharField(
        max_length=20, 
        choices=MEMORY_TYPE_CHOICES, 
        blank=True, 
        help_text="The type of memory (e.g., GDDR6, GDDR6X)"
    )
    
    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the GPU"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this GPU a top pick?"
    )
    
    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the GPU (optional)"
    )
    
    # Specifications (Optional)
    interface = models.CharField(max_length=50, blank=True, help_text="The interface type (e.g., PCIe 4.0 x16)")
    clock_speed = models.PositiveIntegerField(null=True, blank=True, help_text="The base clock speed in MHz (e.g., 1440)")
    boost_clock_speed = models.PositiveIntegerField(null=True, blank=True, help_text="The boost clock speed in MHz (e.g., 1710)")
    cuda_cores = models.PositiveIntegerField(null=True, blank=True, help_text="The number of CUDA cores (for NVIDIA GPUs)")
    stream_processors = models.PositiveIntegerField(null=True, blank=True, help_text="The number of stream processors (for AMD GPUs)")
    
    # Dimensions and Power (Optional)
    length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="The length of the GPU in millimeters (e.g., 285.37)")
    tdp = models.PositiveIntegerField(null=True, blank=True, help_text="The Thermal Design Power in watts (e.g., 320)")
    recommended_psu = models.PositiveIntegerField(null=True, blank=True, help_text="The recommended minimum power supply in watts (e.g., 750)")
    
    # API and Feature Support (Optional)
    directx_support = models.CharField(max_length=50, blank=True, help_text="The DirectX version supported (e.g., DirectX 12 Ultimate)")
    opengl_support = models.CharField(max_length=50, blank=True, help_text="The OpenGL version supported (e.g., OpenGL 4.6)")
    ray_tracing_support = models.BooleanField(default=False, help_text="Does the GPU support ray tracing?")
    dlss_support = models.BooleanField(default=False, help_text="Does the GPU support DLSS?")
    
    # Ports and Connectivity (Optional)
    ports = models.JSONField(
        default=list,
        blank=True,
        help_text="A list of ports (e.g., ['HDMI 2.1', 'DisplayPort 1.4a', 'USB-C'])"
    )
    
    # Multi-GPU Support (Optional)
    multi_gpu_support = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="The type of multi-GPU support (e.g., SLI, NVLink, CrossFire)"
    )
    
    # Power Connectors (Optional)
    power_connectors = models.JSONField(
        default=list,
        blank=True,
        help_text="A list of power connectors (e.g., ['2x 8-pin', '12VHPWR'])"
    )
    
    # Cooling System (Optional)
    COOLING_CHOICES = [
        ('dual_fan', 'Dual Fan'),
        ('triple_fan', 'Triple Fan'),
        ('liquid_cooling', 'Liquid Cooling'),
        ('blower', 'Blower'),
    ]
    cooling_system = models.CharField(
        max_length=50, 
        choices=COOLING_CHOICES, 
        blank=True, 
        help_text="The type of cooling system (e.g., Dual Fan, Liquid Cooling)"
    )
    
    # Additional Information (Optional)
    description = models.TextField(
        null=False, 
        default="High-performance graphics card designed for gaming and professional applications. Features advanced cooling technology and excellent visual processing capabilities.",
        help_text="Detailed description of the GPU"
    )
    
    # Images (Required)
    images = GenericRelation(
        ProductImage,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='gpu'
    )
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate a numeric SKU automatically
        if not self.sku:
            # Create a base number using brand, model, and vram
            base_number = f"{self.brand[:3]}{self.model[:3]}{self.vram}"
            # Add a unique identifier (last 6 digits of UUID)
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "GPU"
        verbose_name_plural = "GPUs"

class CPU(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="Full product name (e.g., AMD Ryzen 9 5950X)"
    )

    # Brand Choices
    BRAND_CHOICES = [
        ('intel', 'Intel'),
        ('amd', 'AMD'),
        ('other', 'Other'),
    ]
    brand = models.CharField(
        max_length=20, 
        choices=BRAND_CHOICES, 
        help_text="The brand of the CPU (e.g., Intel, AMD)"
    )

    model = models.CharField(max_length=100, help_text="The model of the CPU (e.g., i9-13900K, Ryzen 9 7950X)")

    # SKU (Automatically Generated)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False, 
        help_text="Automatically generated numeric SKU for the CPU"
    )

    # Socket Types
    SOCKET_CHOICES = [
        # Intel Sockets
        ('LGA 775', 'LGA 775'),
        ('LGA 1156', 'LGA 1156'),
        ('LGA 1155', 'LGA 1155'),
        ('LGA 1150', 'LGA 1150'),
        ('LGA 1151', 'LGA 1151'),
        ('LGA 1200', 'LGA 1200'),
        ('LGA 1366', 'LGA 1366'),
        ('LGA 1567', 'LGA 1567'),
        ('LGA 1700', 'LGA 1700'),
        ('LGA 1851', 'LGA 1851'),
        ('LGA 2011', 'LGA 2011'),
        ('LGA 2011-3', 'LGA 2011-3'),
        ('LGA 2066', 'LGA 2066'),
        ('LGA 3647', 'LGA 3647'),
        ('LGA 4189', 'LGA 4189'),
        ('LGA 4677', 'LGA 4677'),
        ('LGA 771', 'LGA 771'),
        ('LGA 1356', 'LGA 1356'),
        ('LGA 2551', 'LGA 2551'),

        # AMD Sockets
        ('AM3', 'AM3'),
        ('AM3+', 'AM3+'),
        ('AM4', 'AM4'),
        ('AM5', 'AM5'),
        ('FM1', 'FM1'),
        ('FM2', 'FM2'),
        ('FM2+', 'FM2+'),
        ('TR4', 'TR4'),
        ('sTRX4', 'sTRX4'),
        ('sWRX8', 'sWRX8'),
        ('sTR5', 'sTR5'),
        ('SP3', 'SP3'),
        ('SP5', 'SP5'),
        ('SP6', 'SP6'),
        ('G34', 'G34'),
        ('C32', 'C32'),
        ('F (1207)', 'F (1207)'),

        # Legacy Sockets
        ('Socket 423', 'Socket 423'),
        ('Socket 478', 'Socket 478'),
        ('Socket 754', 'Socket 754'),
        ('Socket 939', 'Socket 939'),
    ]
    socket = models.CharField(
        max_length=20,
        choices=SOCKET_CHOICES,
        help_text="The CPU socket type (e.g., LGA 1700, AM5)"
    )

    # Core Count
    CORES_CHOICES = [
        (1, '1 Core'),
        (2, '2 Cores'),
        (4, '4 Cores'),
        (6, '6 Cores'),
        (8, '8 Cores'),
        (10, '10 Cores'),
        (12, '12 Cores'),
        (16, '16 Cores'),
        (24, '24 Cores'),
        (32, '32 Cores'),
        (48, '48 Cores'),
        (64, '64 Cores'),
        (96, '96 Cores'),
        (128, '128 Cores'),
    ]
    cores = models.PositiveIntegerField(
        choices=CORES_CHOICES,
        help_text="Number of CPU cores"
    )

    # Threads Count
    THREADS_CHOICES = [
        (2, '2 Threads'),
        (4, '4 Threads'),
        (8, '8 Threads'),
        (12, '12 Threads'),
        (16, '16 Threads'),
        (24, '24 Threads'),
        (32, '32 Threads'),
        (48, '48 Threads'),
        (64, '64 Threads'),
        (96, '96 Threads'),
        (128, '128 Threads'),
        (192, '192 Threads'),
        (256, '256 Threads'),
    ]
    threads = models.PositiveIntegerField(
        choices=THREADS_CHOICES,
        help_text="Number of CPU threads"
    )

    # Cache Memory (L3 Cache)
    CACHE_CHOICES = [
        (2, '2 MB'),
        (4, '4 MB'),
        (6, '6 MB'),
        (8, '8 MB'),
        (12, '12 MB'),
        (16, '16 MB'),
        (24, '24 MB'),
        (32, '32 MB'),
        (64, '64 MB'),
        (96, '96 MB'),
        (128, '128 MB'),
    ]
    cache = models.PositiveIntegerField(
        choices=CACHE_CHOICES,
        help_text="L3 Cache size in MB"
    )

    # Clock Speeds
    base_clock_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Base clock speed in GHz (e.g., 3.6 GHz)")
    boost_clock_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Boost clock speed in GHz (e.g., 5.3 GHz)")

    # TDP (Thermal Design Power)
    tdp = models.PositiveIntegerField(null=True, blank=True, help_text="Thermal Design Power in watts (e.g., 125W)")

    # Integrated Graphics
    integrated_graphics = models.CharField(max_length=100, blank=True, help_text="Integrated graphics model (e.g., Intel UHD 770)")

    # Overclocking Support
    overclockable = models.BooleanField(default=False, help_text="Is the CPU overclockable?")

    # Power Connectors
    power_connectors = models.JSONField(
        default=list,
        blank=True,
        help_text="A list of power connectors required (e.g., ['8-pin EPS', '4+4-pin EPS'])"
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the CPU (optional)"
    )

    # Cooling Solution
    cooling_solution = models.CharField(max_length=50, blank=True, help_text="Included cooling solution (e.g., Wraith Prism, None)")

    # Additional Features
    features = models.TextField(blank=True, help_text="Additional features like PCIe version support, memory compatibility, etc.")

    # Images (Required)
    images = GenericRelation(ProductImage)

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the CPU"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this CPU a top pick?"
    )

    description = models.TextField(
        null=False, 
        default="Powerful processor offering excellent multi-core performance for demanding applications. Energy-efficient design with advanced architecture.",
        help_text="Detailed description of the CPU"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model[:3]}{self.cores}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "CPU"
        verbose_name_plural = "CPUs"

class Case(models.Model):
    # Basic Information
    name = models.CharField(max_length=255, unique=True, help_text="The name of the PC case (e.g., MX600 RGB)")
    model = models.CharField(max_length=100, help_text="The model of the case (e.g., MX600 RGB White)")
    brand = models.CharField(max_length=100, help_text="The brand of the case (e.g., Cooler Master, Corsair, NZXT)")

    # Case Form Factor
    CASE_TYPE_CHOICES = [
        ('Full Tower', 'Full Tower'),
        ('Mid Tower', 'Mid Tower'),
        ('Mini Tower', 'Mini Tower'),
        ('Small Form Factor (SFF)', 'Small Form Factor (SFF)'),
        ('Micro-ATX', 'Micro-ATX'),
        ('Mini-ITX', 'Mini-ITX'),
        ('Cube Case', 'Cube Case'),
        ('Open-Air', 'Open-Air'),
        ('Rackmount', 'Rackmount'),
    ]
    case_type = models.CharField(
        max_length=50,
        choices=CASE_TYPE_CHOICES,
        help_text="The form factor of the case"
    )

    # Motherboard Compatibility
    supported_motherboards = models.JSONField(
        default=list,
        null=True,
        blank=True,
        help_text="List of motherboard sizes supported (e.g., ['ATX', 'Micro-ATX', 'Mini-ITX'])"
    )

    # Dimensions
    width_mm = models.PositiveIntegerField(help_text="Width in mm")
    height_mm = models.PositiveIntegerField(help_text="Height in mm")
    depth_mm = models.PositiveIntegerField(help_text="Depth in mm")

    width_in = models.FloatField(help_text="Width in inches")
    height_in = models.FloatField(help_text="Height in inches")
    depth_in = models.FloatField(help_text="Depth in inches")

    # I/O Panel
    io_ports = models.JSONField(
        default=list,
        null=True,
        blank=True,
        help_text="List of front-panel I/O ports (e.g., ['USB 3.0', 'USB Type-C', 'Audio Jack', 'RGB Button'])"
    )

    # Storage Support
    drive_bays_35 = models.PositiveIntegerField(default=0, help_text="Number of 3.5-inch drive bays")
    drive_bays_25 = models.PositiveIntegerField(default=0, help_text="Number of 2.5-inch drive bays (including converted bays)")

    # Expansion Slots
    horizontal_slots = models.PositiveIntegerField(default=0, help_text="Number of horizontal expansion slots")
    vertical_slots = models.PositiveIntegerField(default=0, help_text="Number of vertical expansion slots")
    vertical_gpu_support = models.BooleanField(default=False, help_text="Does the case support vertical GPU mounting?")

    # Cooling Support
    max_fan_mounts = models.PositiveIntegerField(default=0, help_text="Maximum number of fan mounts")
    preinstalled_fans = models.JSONField(
        default=list,
        null=True,
        blank=True,
        help_text="List of pre-installed fans with details (e.g., [{'location': 'Front', 'size': 140, 'type': 'ARGB'}])"
    )
    fan_speeds = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text="Dictionary of fan speeds (e.g., {'140mm': '500-1200 RPM', '120mm': '500-1400 RPM'})"
    )
    fan_connectors = models.JSONField(
        default=list,
        null=True,
        blank=True,
        help_text="List of fan connectors (e.g., ['5V 3 Pin (ARGB)', '4 Pin PWM'])"
    )

    # Water Cooling Support
    water_cooling_support = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text="Dictionary of supported radiator sizes by location (e.g., {'Front': ['360mm', '280mm'], 'Top': ['360mm']})"
    )

    # Aesthetic Features
    has_tempered_glass = models.BooleanField(default=False, help_text="Does the case have a tempered glass side panel?")
    has_rgb_sync = models.BooleanField(default=False, help_text="Does the case support RGB sync with the motherboard?")

    # Compatibility Limits
    max_gpu_length = models.PositiveIntegerField(help_text="Max GPU length in mm")
    max_cpu_cooler_height = models.PositiveIntegerField(help_text="Max CPU cooler height in mm")
    max_psu_length = models.PositiveIntegerField(help_text="Max PSU length in mm")

    # SKU (Automatically Generated)
    sku = models.CharField(max_length=20, unique=True, editable=False)

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the case"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this case a top pick?"
    )
    images = GenericRelation(ProductImage)
    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the case"
    )

    description = models.TextField(
        null=False, 
        default="Stylish and functional computer case with excellent airflow design. Features tool-less installation and multiple drive bays for easy customization.",
        help_text="Detailed description of the case"
    )

    def __str__(self):
        return f"{self.brand} {self.name} - {self.model}"

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model[:3]}{self.case_type[:3]}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "PC Case"
        verbose_name_plural = "PC Cases"

class RAM(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="Full product name (e.g., Corsair Vengeance RGB Pro 32GB DDR4-3600)"
    )
    # Predefined brand choices
    BRAND_CHOICES = [
        ('Corsair', 'Corsair'),
        ('G.Skill', 'G.Skill'),
        ('Kingston', 'Kingston'),
        ('Crucial', 'Crucial'),
        ('Samsung', 'Samsung'),
        ('ADATA', 'ADATA'),
        ('HyperX', 'HyperX'),
        ('TeamGroup', 'TeamGroup'),
        ('Patriot', 'Patriot'),
        ('T-Force', 'T-Force'),
    ]

    # RAM Type choices
    RAM_TYPE_CHOICES = [
        ('DDR2', 'DDR2'),
        ('DDR3', 'DDR3'),
        ('DDR3L', 'DDR3L'),
        ('DDR4', 'DDR4'),
        ('DDR5', 'DDR5'),
    ]

    # Capacity choices
    CAPACITY_CHOICES = [
        (2, '2GB'),
        (4, '4GB'),
        (8, '8GB'),
        (16, '16GB'),
        (32, '32GB'),
        (64, '64GB'),
        (128, '128GB'),
        (256, '256GB'),
    ]

    # Form Factor choices
    FORM_FACTOR_CHOICES = [
        ('DIMM', 'DIMM (Desktop)'),
        ('SODIMM', 'SODIMM (Laptop)'),
    ]

    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    model_name = models.CharField(max_length=100, help_text="e.g., Vengeance LPX, Ripjaws V, Ballistix Elite")

    ram_type = models.CharField(max_length=10, choices=RAM_TYPE_CHOICES)
    capacity = models.PositiveIntegerField(choices=CAPACITY_CHOICES, help_text="Select RAM Size (GB)")
    speed = models.PositiveIntegerField(help_text="Speed in MHz (e.g., 2400, 3200, 3600)")

    form_factor = models.CharField(max_length=10, choices=FORM_FACTOR_CHOICES)
    voltage = models.DecimalField(max_digits=3, decimal_places=2, help_text="Voltage (e.g., 1.2V, 1.35V)", default=1.2)

    ecc_support = models.BooleanField(default=False, help_text="Is ECC (Error-Correcting Code) supported?")
    rgb_lighting = models.BooleanField(default=False, help_text="Does it have RGB lighting?")

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the RAM (e.g., New, Used, Refurbished, Box Open)"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period (e.g., 1 Year, 2 Years)"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this RAM a top pick?"
    )

    # Images (Required)
    images = GenericRelation(ProductImage)

    # SKU (Automatically Generated)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the RAM"
    )

    description = models.TextField(
        null=False, 
        default="High-speed memory module designed for optimal system performance. Provides reliable operation with excellent compatibility across various systems.",
        help_text="Detailed description of the RAM"
    )

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model_name[:3]}{self.capacity}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model_name} {self.capacity}GB {self.ram_type} {self.speed}MHz"

class Motherboard(models.Model):
    # Basic Information
    name = models.CharField(max_length=255, unique=True, help_text="The name of the motherboard (e.g., ASUS ROG STRIX Z690-E)")
    model = models.CharField(max_length=100, help_text="The model of the motherboard (e.g., ROG STRIX Z690-E)")

    # Brand Choices
    BRAND_CHOICES = [
        # 🔹 Mainstream Brands
        ('asus', 'ASUS'),
        ('msi', 'MSI'),
        ('gigabyte', 'Gigabyte'),
        ('asrock', 'ASRock'),
        ('biostar', 'Biostar'),

        # 🔹 High-End & Enthusiast Brands
        ('evga', 'EVGA'),
        ('nzxt', 'NZXT'),
        ('supermicro', 'Supermicro'),

        # 🔹 Industrial & Workstation Brands
        ('intel_oem', 'Intel (OEM boards)'),
        ('tyan', 'Tyan'),
        ('supermicro', 'Supermicro'),

        # 🔹 OEM & Prebuilt PC Motherboards
        ('dell', 'Dell'),
        ('hp', 'HP'),
        ('lenovo', 'Lenovo'),
        ('acer', 'Acer'),
    ]
    brand = models.CharField(
        max_length=20,
        choices=BRAND_CHOICES,
        help_text="The brand of the motherboard"
    )

    # CPU Socket Compatibility
    SOCKET_CHOICES = [
        # Intel Sockets
        ('LGA 775', 'LGA 775'),
        ('LGA 1156', 'LGA 1156'),
        ('LGA 1155', 'LGA 1155'),
        ('LGA 1150', 'LGA 1150'),
        ('LGA 1151', 'LGA 1151'),
        ('LGA 1200', 'LGA 1200'),
        ('LGA 1366', 'LGA 1366'),
        ('LGA 1567', 'LGA 1567'),
        ('LGA 1700', 'LGA 1700'),
        ('LGA 1851', 'LGA 1851'),
        ('LGA 2011', 'LGA 2011'),
        ('LGA 2011-3', 'LGA 2011-3'),
        ('LGA 2066', 'LGA 2066'),
        ('LGA 3647', 'LGA 3647'),
        ('LGA 4189', 'LGA 4189'),
        ('LGA 4677', 'LGA 4677'),
        ('LGA 771', 'LGA 771'),
        ('LGA 1356', 'LGA 1356'),
        ('LGA 2551', 'LGA 2551'),

        # AMD Sockets
        ('AM3', 'AM3'),
        ('AM3+', 'AM3+'),
        ('AM4', 'AM4'),
        ('AM5', 'AM5'),
        ('FM1', 'FM1'),
        ('FM2', 'FM2'),
        ('FM2+', 'FM2+'),
        ('TR4', 'TR4'),
        ('sTRX4', 'sTRX4'),
        ('sWRX8', 'sWRX8'),
        ('sTR5', 'sTR5'),
        ('SP3', 'SP3'),
        ('SP5', 'SP5'),
        ('SP6', 'SP6'),
        ('G34', 'G34'),
        ('C32', 'C32'),
        ('F (1207)', 'F (1207)'),

        # Legacy Sockets
        ('Socket 423', 'Socket 423'),
        ('Socket 478', 'Socket 478'),
        ('Socket 754', 'Socket 754'),
        ('Socket 939', 'Socket 939'),
    ]
    socket = models.CharField(
        max_length=20,
        choices=SOCKET_CHOICES,
        help_text="Compatible CPU socket type"
    )

    # Chipset
    chipset = models.CharField(max_length=100, help_text="Chipset (e.g., Z690, B550, X570, H610)")

    # Form Factor
    FORM_FACTOR_CHOICES = [
        ('ATX', 'ATX'),
        ('Micro-ATX', 'Micro-ATX'),
        ('Mini-ITX', 'Mini-ITX'),
        ('E-ATX', 'E-ATX'),
        ('XL-ATX', 'XL-ATX'),
        ('SSI-CEB', 'SSI-CEB'),
        ('SSI-EEB', 'SSI-EEB'),
    ]
    form_factor = models.CharField(
        max_length=20,
        choices=FORM_FACTOR_CHOICES,
        help_text="Motherboard form factor"
    )

    # RAM Support
    RAM_TYPE_CHOICES = [
        ('DDR', 'DDR'),
        ('DDR2', 'DDR2'),
        ('DDR3', 'DDR3'),
        ('DDR3L', 'DDR3L'),
        ('DDR4', 'DDR4'),
        ('DDR5', 'DDR5'),
    ]
    ram_type = models.CharField(
        max_length=10,
        choices=RAM_TYPE_CHOICES,
        help_text="Supported RAM type"
    )
    ram_slots = models.PositiveIntegerField(
        default=2,
        help_text="Number of RAM slots"
    )
    max_ram = models.PositiveIntegerField(
        help_text="Maximum RAM capacity in GB"
    )

    # PCIe Slots
    PCIe_VERSION_CHOICES = [
        ('PCIe 3.0', 'PCIe 3.0'),
        ('PCIe 4.0', 'PCIe 4.0'),
        ('PCIe 5.0', 'PCIe 5.0'),
    ]
    pcie_version = models.CharField(
        max_length=10,
        choices=PCIe_VERSION_CHOICES,
        help_text="PCIe version supported"
    )
    pcie_slots = models.PositiveIntegerField(
        help_text="Number of PCIe slots"
    )

    # Storage Support
    sata_ports = models.PositiveIntegerField(
        help_text="Number of SATA ports"
    )
    m2_slots = models.PositiveIntegerField(
        help_text="Number of M.2 slots"
    )

    # USB Ports
    usb_ports = models.JSONField(
        default=list,
        blank=True,
        help_text="List of available USB ports (e.g., ['USB 3.2 Gen2', 'USB Type-C', 'USB 2.0'])"
    )

    # Networking
    has_wifi = models.BooleanField(default=False, help_text="Does the motherboard have built-in WiFi?")
    ethernet_speed = models.CharField(max_length=50, blank=True, help_text="Ethernet speed (e.g., 1GbE, 2.5GbE, 10GbE)")

    # RGB & Aesthetic Features
    has_rgb = models.BooleanField(default=False, help_text="Does the motherboard have RGB lighting?")

    # Power Connectors
    power_connectors = models.JSONField(
        default=list,
        blank=True,
        help_text="A list of power connectors (e.g., ['24-pin ATX', '8-pin EPS', '4+4-pin EPS'])"
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the motherboard"
    )

    # Images
    images = GenericRelation(ProductImage)

    # SKU (Automatically Generated)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False
    )

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the motherboard"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this motherboard a top pick?"
    )

    description = models.TextField(
        null=False, 
        default="Feature-rich motherboard with excellent build quality and component compatibility. Designed for stability and performance with multiple expansion options.",
        help_text="Detailed description of the motherboard"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model[:3]}{self.socket[:3]}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Motherboard"
        verbose_name_plural = "Motherboards"

class Tablet(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="Full product name (e.g., Apple iPad Pro 12.9-inch 2023)"
    )
    
    # Brand Choices
    BRAND_CHOICES = [
        ("Apple", "Apple"),
        ("Samsung", "Samsung"),
        ("Lenovo", "Lenovo"),
        ("Huawei", "Huawei"),
        ("Microsoft", "Microsoft"),
        ("Google", "Google"),
        ("Xiaomi", "Xiaomi"),
        ("Realme", "Realme"),
        ("Amazon", "Amazon (Fire Tablets)"),
        ("Asus", "Asus"),
        ("Sony", "Sony"),
        ("Docomo", "Docomo"),
        ("Alcatel", "Alcatel"),
        ("Honor", "Honor"),
    ]
    brand = models.CharField(
        max_length=50, 
        choices=BRAND_CHOICES,
        help_text="Select tablet brand"
    )
    
    model = models.CharField(
        max_length=100, 
        help_text="Tablet model number (e.g., A2764, SM-T970, etc.)"
    )

    # Display
    screen_size = models.FloatField(help_text="Screen size in inches (e.g., 12.9, 10.5)")
    screen_type = models.CharField(max_length=50, help_text="Screen type (e.g., IPS LCD, AMOLED, Retina)")
    resolution = models.CharField(max_length=50, help_text="Resolution (e.g., 2732 x 2048)")
    refresh_rate = models.PositiveIntegerField(default=60, help_text="Refresh rate in Hz (e.g., 60, 90, 120, 144)")

    # Performance
    chipset = models.CharField(max_length=100, help_text="Processor model (e.g., Apple M2, Snapdragon 8 Gen 1)")

    # RAM Choices
    RAM_CHOICES = [
        (2, "2GB"),
        (3, "3GB"),
        (4, "4GB"),
        (6, "6GB"),
        (8, "8GB"),
        (12, "12GB"),
        (16, "16GB"),
    ]
    ram = models.PositiveIntegerField(
        choices=RAM_CHOICES,
        help_text="Select RAM size"
    )

    # Storage Choices
    STORAGE_CHOICES = [
        (32, "32GB"),
        (64, "64GB"),
        (128, "128GB"),
        (256, "256GB"),
        (512, "512GB"),
        (1024, "1TB"),
        (2048, "2TB"),
    ]
    storage = models.PositiveIntegerField(
        choices=STORAGE_CHOICES,
        help_text="Select internal storage (ROM) size"
    )

    # Battery & Charging
    battery_capacity = models.PositiveIntegerField(help_text="Battery capacity in mAh")
    fast_charging = models.BooleanField(default=False, help_text="Supports fast charging?")
    wireless_charging = models.BooleanField(default=False, help_text="Supports wireless charging?")
    charging_wattage = models.PositiveIntegerField(default=10, help_text="Charging power (e.g., 10W, 18W, 45W)")

    # Camera
    rear_camera_mp = models.PositiveIntegerField(help_text="Rear camera resolution in MP (e.g., 12, 48)")
    front_camera_mp = models.PositiveIntegerField(help_text="Front camera resolution in MP (e.g., 7, 12)")

    # PTA Approval
    pta_approved = models.BooleanField(default=False, help_text="PTA Approved for Pakistan?")

    # Connectivity & Ports
    cellular = models.BooleanField(default=False, help_text="Supports SIM card?")
    sim_type = models.CharField(max_length=50, blank=True, null=True, help_text="SIM type (e.g., Nano-SIM, eSIM)")
    usb_type = models.CharField(max_length=20, help_text="USB type (e.g., USB-C, Lightning, Micro-USB)")
    headphone_jack = models.BooleanField(default=False, help_text="Has 3.5mm headphone jack?")
    sd_card_slot = models.BooleanField(default=False, help_text="Supports microSD card expansion?")

    # Operating System
    os = models.CharField(max_length=100, help_text="Operating System (e.g., iPadOS, Android 13, Windows 11)")
    os_version = models.CharField(max_length=50, help_text="OS version at launch")

    # Build & Design
    weight = models.FloatField(help_text="Weight in grams")
    dimensions = models.CharField(max_length=100, help_text="Dimensions (WxHxD) in mm (e.g., 247.6 x 178.5 x 5.9 mm)")
    material = models.CharField(max_length=50, help_text="Build material (e.g., Aluminum, Glass, Plastic)")

    # Extra Features
    stylus_support = models.BooleanField(default=False, help_text="Supports stylus?")
    keyboard_support = models.BooleanField(default=False, help_text="Supports external keyboards?")
    biometric_auth = models.CharField(max_length=50, help_text="Biometric authentication (e.g., Face ID, Fingerprint)")

    # Condition (Required)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES,
        help_text="The condition of the tablet"
    )
    
    # Warranty
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES,
        blank=True,
        help_text="The warranty period"
    )
    
    # Top Pick
    top_pick = models.BooleanField(
        default=False,
        help_text="Is this tablet a top pick?"
    )
    
    # Images
    images = GenericRelation(ProductImage)
    
    # SKU
    sku = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Automatically generated SKU"
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the tablet"
    )

    description = models.TextField(
        null=False, 
        default="Versatile tablet with responsive touchscreen and powerful performance. Features long battery life and excellent display quality for both work and entertainment.",
        help_text="Detailed description of the tablet"
    )

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model[:3]}{self.ram}{self.storage}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model} - {self.ram}GB RAM, {self.storage}GB Storage"

    class Meta:
        verbose_name = "Tablet"
        verbose_name_plural = "Tablets"

class Laptop(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="Full product name (e.g., MacBook Pro 16-inch 2023)"
    )

    # Brand Choices
    BRAND_CHOICES = [
        ('Dell', 'Dell'),
        ('HP', 'HP'),
        ('Lenovo', 'Lenovo'),
        ('ASUS', 'ASUS'),
        ('Acer', 'Acer'),
        ('MSI', 'MSI'),
        ('Apple', 'Apple'),
        ('Razer', 'Razer'),
        ('Samsung', 'Samsung'),
        ('Microsoft', 'Microsoft'),
        ('Gigabyte', 'Gigabyte'),
        ('Huawei', 'Huawei'),
    ]
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    model_name = models.CharField(max_length=100)
    
    # Processor Details
    PROCESSOR_BRAND_CHOICES = [
        ('Intel', 'Intel'),
        ('AMD', 'AMD'),
        ('Apple', 'Apple'),
        ('Qualcomm', 'Qualcomm'),
    ]
    processor_brand = models.CharField(max_length=50, choices=PROCESSOR_BRAND_CHOICES)
    processor_model = models.CharField(max_length=100)
    processor_generation = models.CharField(max_length=50)
    core_count = models.PositiveIntegerField()
    base_clock = models.FloatField(help_text="Base clock speed in GHz")
    boost_clock = models.FloatField(help_text="Boost clock speed in GHz")

    # Memory & Storage
    RAM_TYPE_CHOICES = [
        ('DDR3', 'DDR3'),
        ('DDR4', 'DDR4'),
        ('DDR5', 'DDR5'),
        ('LPDDR4', 'LPDDR4'),
        ('LPDDR4X', 'LPDDR4X'),
        ('LPDDR5', 'LPDDR5'),
    ]
    RAM_CAPACITY_CHOICES = [
        (4, '4GB'),
        (8, '8GB'),
        (16, '16GB'),
        (32, '32GB'),
        (64, '64GB'),
        (128, '128GB'),
    ]
    ram_capacity = models.PositiveIntegerField(choices=RAM_CAPACITY_CHOICES)
    ram_type = models.CharField(max_length=20, choices=RAM_TYPE_CHOICES)
    ram_speed = models.PositiveIntegerField(help_text="RAM speed in MHz")

    STORAGE_TYPE_CHOICES = [
        ('HDD', 'HDD'),
        ('SSD', 'SSD'),
        ('NVMe SSD', 'NVMe SSD'),
    ]
    STORAGE_CAPACITY_CHOICES = [
        (256, '256GB'),
        (512, '512GB'),
        (1024, '1TB'),
        (2048, '2TB'),
        (4096, '4TB'),
    ]
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPE_CHOICES)
    storage_capacity = models.PositiveIntegerField(choices=STORAGE_CAPACITY_CHOICES)

    # Display
    DISPLAY_TYPE_CHOICES = [
        ('IPS', 'IPS'),
        ('OLED', 'OLED'),
        ('Mini LED', 'Mini LED'),
        ('TN', 'TN'),
        ('VA', 'VA'),
    ]
    RESOLUTION_CHOICES = [
        ('1366x768', 'HD (1366x768)'),
        ('1920x1080', 'Full HD (1920x1080)'),
        ('2560x1440', 'QHD (2560x1440)'),
        ('3840x2160', '4K UHD (3840x2160)'),
        ('3456x2234', '3.5K (3456x2234)'),
    ]
    REFRESH_RATE_CHOICES = [
        (60, '60Hz'),
        (90, '90Hz'),
        (120, '120Hz'),
        (144, '144Hz'),
        (165, '165Hz'),
        (240, '240Hz'),
    ]
    screen_size = models.FloatField(help_text="Screen size in inches")
    resolution = models.CharField(max_length=50, choices=RESOLUTION_CHOICES)
    refresh_rate = models.PositiveIntegerField(choices=REFRESH_RATE_CHOICES)
    display_type = models.CharField(max_length=50, choices=DISPLAY_TYPE_CHOICES)
    brightness = models.PositiveIntegerField(help_text="Brightness in nits")
    touch_screen = models.BooleanField(default=False)

    # Graphics
    GPU_BRAND_CHOICES = [
        ('NVIDIA', 'NVIDIA'),
        ('AMD', 'AMD'),
        ('Intel', 'Intel'),
        ('Apple', 'Apple'),
    ]
    gpu_brand = models.CharField(max_length=50, choices=GPU_BRAND_CHOICES)
    gpu_model = models.CharField(max_length=100)
    gpu_memory = models.PositiveIntegerField(help_text="GPU memory in GB")

    # Battery & Power
    battery_capacity = models.PositiveIntegerField(help_text="Battery capacity in Whr")
    battery_life = models.CharField(max_length=50)
    power_adapter = models.PositiveIntegerField(help_text="Power adapter wattage")
    fast_charging = models.BooleanField(default=False)

    # Connectivity
    WIFI_STANDARD_CHOICES = [
        ('Wi-Fi 5', 'Wi-Fi 5 (802.11ac)'),
        ('Wi-Fi 6', 'Wi-Fi 6 (802.11ax)'),
        ('Wi-Fi 6E', 'Wi-Fi 6E'),
    ]
    BLUETOOTH_VERSION_CHOICES = [
        ('4.0', 'Bluetooth 4.0'),
        ('5.0', 'Bluetooth 5.0'),
        ('5.1', 'Bluetooth 5.1'),
        ('5.2', 'Bluetooth 5.2'),
    ]
    wifi_standard = models.CharField(max_length=20, choices=WIFI_STANDARD_CHOICES)
    bluetooth_version = models.CharField(max_length=20, choices=BLUETOOTH_VERSION_CHOICES)
    usb_ports = models.JSONField(help_text="List of USB ports and their types", blank=True, null=True)
    hdmi_ports = models.PositiveIntegerField(default=1)
    ethernet_port = models.BooleanField(default=False)
    headphone_jack = models.BooleanField(default=True)
    card_reader = models.BooleanField(default=False)

    # Physical Specifications
    COLOR_CHOICES = [
        ('Black', 'Black'),
        ('Silver', 'Silver'),
        ('Space Gray', 'Space Gray'),
        ('White', 'White'),
        ('Blue', 'Blue'),
        ('Red', 'Red'),
    ]
    MATERIAL_CHOICES = [
        ('Aluminum', 'Aluminum'),
        ('Plastic', 'Plastic'),
        ('Magnesium', 'Magnesium'),
        ('Carbon Fiber', 'Carbon Fiber'),
    ]
    weight = models.FloatField(help_text="Weight in kg")
    dimensions = models.CharField(max_length=50, help_text="WxDxH in mm")
    build_material = models.CharField(max_length=100, choices=MATERIAL_CHOICES)
    color = models.CharField(max_length=50, choices=COLOR_CHOICES)

    # Features
    WEBCAM_RESOLUTION_CHOICES = [
        ('720p', 'HD (720p)'),
        ('1080p', 'Full HD (1080p)'),
        ('1440p', 'QHD (1440p)'),
    ]
    backlit_keyboard = models.BooleanField(default=False)
    fingerprint_sensor = models.BooleanField(default=False)
    numeric_keypad = models.BooleanField(default=False)
    webcam_resolution = models.CharField(max_length=20, choices=WEBCAM_RESOLUTION_CHOICES)
    speakers = models.CharField(max_length=100)
    microphone = models.CharField(max_length=100)

    # Operating System
    OS_CHOICES = [
        ('Windows 10', 'Windows 10'),
        ('Windows 11', 'Windows 11'),
        ('macOS', 'macOS'),
        ('Linux', 'Linux'),
        ('ChromeOS', 'ChromeOS'),
    ]
    operating_system = models.CharField(max_length=50, choices=OS_CHOICES)
    os_version = models.CharField(max_length=50)

    # Additional Info
    warranty_info = models.TextField()

    # Standard Fields (unchanged)
    condition = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('used', 'Used'),
            ('refurbished', 'Refurbished'),
            ('box_open', 'Box Open'),
        ]
    )
    warranty = models.CharField(
        max_length=20,
        choices=[
            ('no_warranty', 'No Warranty'),
            ('1_day', '1 Day'),
            ('3_days', '3 Days'),
            ('1_week', '1 Week'),
            ('1_month', '1 Month'),
            ('6_months', '6 Months'),
            ('1_year', '1 Year'),
            ('2_years', '2 Years'),
            ('3_years', '3 Years'),
        ],
        blank=True
    )
    top_pick = models.BooleanField(default=False)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    images = GenericRelation(ProductImage)
    sku = models.CharField(max_length=20, unique=True, editable=False)

    description = models.TextField(
        null=False, 
        default="Powerful laptop combining performance and portability. Features high-quality display, responsive keyboard, and excellent battery life for productivity on the go.",
        help_text="Detailed description of the laptop"
    )

    def save(self, *args, **kwargs):
        if not self.sku:
            base = f"{self.brand[:3]}{self.model_name[:3]}{self.processor_model[:3]}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base}{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Laptop"
        verbose_name_plural = "Laptops"

class StorageDevice(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="The full name of the storage device (e.g., Samsung 970 EVO Plus 1TB NVMe SSD)"
    )
    # Predefined brand choices
    BRAND_CHOICES = [
        ('Seagate', 'Seagate'),
        ('Western Digital', 'Western Digital'),
        ('Samsung', 'Samsung'),
        ('Kingston', 'Kingston'),
        ('Crucial', 'Crucial'),
        ('ADATA', 'ADATA'),
        ('Toshiba', 'Toshiba'),
        ('Intel', 'Intel'),
        ('SK Hynix', 'SK Hynix'),
        ('TeamGroup', 'TeamGroup'),
    ]

    # Storage Type choices
    STORAGE_TYPE_CHOICES = [
        ('HDD', 'HDD (Hard Disk Drive)'),
        ('SSD', 'SSD (Solid State Drive)'),
        ('NVMe', 'NVMe SSD (PCIe)'),
    ]

    # Capacity choices
    CAPACITY_CHOICES = [
        (128, '128GB'),
        (256, '256GB'),
        (512, '512GB'),
        (1024, '1TB'),
        (2048, '2TB'),
        (4096, '4TB'),
        (8192, '8TB'),
        (12288, '12TB'),
        (16000, '16TB'),
    ]

    # Interface choices
    INTERFACE_CHOICES = [
        ('SATA', 'SATA'),
        ('PCIe Gen3', 'PCIe Gen3'),
        ('PCIe Gen4', 'PCIe Gen4'),
        ('PCIe Gen5', 'PCIe Gen5'),
    ]

    # Form Factor choices
    FORM_FACTOR_CHOICES = [
        ('2.5"', '2.5-inch'),
        ('3.5"', '3.5-inch'),
        ('M.2', 'M.2'),
        ('U.2', 'U.2'),
    ]

    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    model_name = models.CharField(max_length=100, help_text="e.g., Barracuda, 970 EVO, WD Black")

    storage_type = models.CharField(max_length=10, choices=STORAGE_TYPE_CHOICES)
    capacity = models.PositiveIntegerField(choices=CAPACITY_CHOICES, help_text="Select Storage Capacity (GB)")
    interface = models.CharField(max_length=20, choices=INTERFACE_CHOICES)
    form_factor = models.CharField(max_length=10, choices=FORM_FACTOR_CHOICES)

    # Additional attributes
    cache_size = models.PositiveIntegerField(blank=True, null=True, help_text="Cache size in MB (for HDDs)")
    rpm_speed = models.PositiveIntegerField(blank=True, null=True, help_text="RPM speed (for HDDs)")
    read_speed = models.PositiveIntegerField(blank=True, null=True, help_text="Read speed in MB/s (for SSDs)")
    write_speed = models.PositiveIntegerField(blank=True, null=True, help_text="Write speed in MB/s (for SSDs)")
    tbw = models.PositiveIntegerField(blank=True, null=True, help_text="Total Bytes Written (TBW) for SSD endurance")

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the storage device"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this storage device a top pick?"
    )

    # Images (Required)
    images = GenericRelation(ProductImage)

    # SKU (Automatically Generated)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the storage device"
    )

    description = models.TextField(
        null=False, 
        default="High-capacity storage solution with excellent read/write speeds. Reliable performance for both everyday use and demanding applications.",
        help_text="Detailed description of the storage device"
    )

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model_name[:3]}{self.capacity}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model_name} {self.capacity}GB {self.storage_type} {self.interface}"

class PSU(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="The full name of the PSU (e.g., Corsair RM850x 850W 80+ Gold)"
    )
    # Predefined brand choices
    BRAND_CHOICES = [
        ('Corsair', 'Corsair'),
        ('EVGA', 'EVGA'),
        ('Seasonic', 'Seasonic'),
        ('Thermaltake', 'Thermaltake'),
        ('Cooler Master', 'Cooler Master'),
        ('Be Quiet!', 'Be Quiet!'),
        ('SilverStone', 'SilverStone'),
        ('NZXT', 'NZXT'),
        ('Gigabyte', 'Gigabyte'),
        ('Deepcool', 'Deepcool'),
        ('ASUS', 'ASUS'),
        ('MSI', 'MSI'),
    ]

    # Wattage choices
    WATTAGE_CHOICES = [
        (450, '450W'),
        (550, '550W'),
        (650, '650W'),
        (750, '750W'),
        (850, '850W'),
        (1000, '1000W'),
        (1200, '1200W'),
        (1500, '1500W'),
        (1600, '1600W'),
    ]

    # Efficiency Rating choices
    EFFICIENCY_CHOICES = [
        ('80+ Bronze', '80+ Bronze'),
        ('80+ Silver', '80+ Silver'),
        ('80+ Gold', '80+ Gold'),
        ('80+ Platinum', '80+ Platinum'),
        ('80+ Titanium', '80+ Titanium'),
    ]

    # Modular type choices
    MODULAR_CHOICES = [
        ('Non-Modular', 'Non-Modular'),
        ('Semi-Modular', 'Semi-Modular'),
        ('Fully Modular', 'Fully Modular'),
    ]

    # Form factor choices
    FORM_FACTOR_CHOICES = [
        ('ATX', 'ATX'),
        ('SFX', 'SFX'),
        ('SFX-L', 'SFX-L'),
        ('TFX', 'TFX'),
    ]

    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    model_name = models.CharField(max_length=100, help_text="e.g., RM850x, SF600, Focus GX-750")
    wattage = models.PositiveIntegerField(choices=WATTAGE_CHOICES)
    efficiency_rating = models.CharField(max_length=20, choices=EFFICIENCY_CHOICES)
    modular_type = models.CharField(max_length=20, choices=MODULAR_CHOICES)
    form_factor = models.CharField(max_length=10, choices=FORM_FACTOR_CHOICES)

    # Connectors
    pci_e_connectors = models.PositiveIntegerField(help_text="Number of PCIe (6+2) connectors")
    cpu_power_connectors = models.PositiveIntegerField(help_text="Number of CPU (4+4) connectors")
    sata_connectors = models.PositiveIntegerField(help_text="Number of SATA connectors")
    molex_connectors = models.PositiveIntegerField(help_text="Number of Molex connectors")

    # Protection features
    has_ocp = models.BooleanField(default=True, help_text="Over Current Protection (OCP)")
    has_ovp = models.BooleanField(default=True, help_text="Over Voltage Protection (OVP)")
    has_uvp = models.BooleanField(default=True, help_text="Under Voltage Protection (UVP)")
    has_scp = models.BooleanField(default=True, help_text="Short Circuit Protection (SCP)")
    has_opp = models.BooleanField(default=True, help_text="Over Power Protection (OPP)")
    has_otp = models.BooleanField(default=True, help_text="Over Temperature Protection (OTP)")

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the PSU"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this PSU a top pick?"
    )

    # Images (Required)
    images = GenericRelation(ProductImage)

    # SKU (Automatically Generated)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the PSU"
    )

    description = models.TextField(
        null=False, 
        default="Reliable power supply unit with excellent efficiency ratings. Features stable power delivery and protective circuitry for system safety.",
        help_text="Detailed description of the PSU"
    )

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model_name[:3]}{self.wattage}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model_name} {self.wattage}W {self.efficiency_rating}"

class Monitor(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="The full name of the monitor (e.g., ASUS ROG Swift PG279QM 27\" 1440p 240Hz)"
    )
    # Panel type choices
    PANEL_TYPE_CHOICES = [
        ('IPS', 'IPS'),
        ('VA', 'VA'),
        ('TN', 'TN'),
        ('OLED', 'OLED'),
        ('Mini LED', 'Mini LED'),
    ]

    # Refresh rate choices
    REFRESH_RATE_CHOICES = [
        (60, '60Hz'),
        (75, '75Hz'),
        (120, '120Hz'),
        (144, '144Hz'),
        (165, '165Hz'),
        (240, '240Hz'),
        (360, '360Hz'),
    ]

    # Resolution choices
    RESOLUTION_CHOICES = [
        ('1920x1080', '1080p (1920x1080)'),
        ('2560x1440', '1440p (2560x1440)'),
        ('3840x2160', '4K (3840x2160)'),
        ('5120x2160', '5K (5120x2160)'),
        ('7680x4320', '8K (7680x4320)'),
    ]

    # Aspect ratio choices
    ASPECT_RATIO_CHOICES = [
        ('16:9', '16:9 (Standard)'),
        ('21:9', '21:9 (Ultrawide)'),
        ('32:9', '32:9 (Super Ultrawide)'),
    ]

    brand = models.CharField(max_length=50, help_text="Enter monitor brand (e.g., Dell, ASUS, LG)")
    model_name = models.CharField(max_length=100, help_text="Enter model name (e.g., ROG Swift PG259QN)")
    screen_size = models.DecimalField(max_digits=4, decimal_places=1, help_text="Size in inches (e.g., 27.0)")
    panel_type = models.CharField(max_length=20, choices=PANEL_TYPE_CHOICES)
    refresh_rate = models.PositiveIntegerField(choices=REFRESH_RATE_CHOICES)
    resolution = models.CharField(max_length=20, choices=RESOLUTION_CHOICES)
    aspect_ratio = models.CharField(max_length=10, choices=ASPECT_RATIO_CHOICES)

    # Connectivity options
    has_hdmi = models.BooleanField(default=True, help_text="Does it have HDMI?")
    has_displayport = models.BooleanField(default=True, help_text="Does it have DisplayPort?")
    has_usb_c = models.BooleanField(default=False, help_text="Does it have USB-C?")
    has_vga = models.BooleanField(default=False, help_text="Does it have VGA?")

    # Adaptive sync support
    supports_gsync = models.BooleanField(default=False, help_text="Supports NVIDIA G-Sync?")
    supports_freesync = models.BooleanField(default=False, help_text="Supports AMD FreeSync?")

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the monitor"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this monitor a top pick?"
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the monitor"
    )

    # Images
    images = GenericRelation(ProductImage)

    # SKU (Automatically Generated)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False
    )

    description = models.TextField(
        null=False, 
        default="High-quality display with excellent color accuracy and response time. Features ergonomic design and multiple connectivity options for versatile use.",
        help_text="Detailed description of the monitor"
    )

    def __str__(self):
        return f"{self.brand} {self.model_name} - {self.screen_size}\" {self.resolution} {self.refresh_rate}Hz"

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model_name[:3]}{self.screen_size}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Monitor"
        verbose_name_plural = "Monitors"

# Mouse Model
class Mouse(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="The full name of the mouse (e.g., Logitech G Pro X Superlight Wireless)"
    )
    CONNECTION_CHOICES = [("Wired", "Wired"), ("Wireless", "Wireless")]

    brand = models.CharField(max_length=50, help_text="Enter the brand (e.g., Logitech, Razer)")
    model_name = models.CharField(max_length=100)
    connection_type = models.CharField(max_length=10, choices=CONNECTION_CHOICES)
    dpi = models.PositiveIntegerField(help_text="Max DPI (e.g., 16000)")
    buttons = models.PositiveIntegerField(help_text="Number of buttons")
    has_rgb = models.BooleanField(default=False, help_text="RGB lighting?")

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the mouse"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this mouse a top pick?"
    )

    # Images (Required)
    images = GenericRelation(ProductImage)

    # SKU (Automatically Generated)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the mouse"
    )

    description = models.TextField(
        null=False, 
        default="Ergonomic mouse with precise tracking and customizable buttons. Designed for comfort during extended use with durable construction.",
        help_text="Detailed description of the mouse"
    )

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model_name[:3]}{self.dpi}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model_name} - {self.connection_type}, {self.dpi} DPI"

# Keyboard Model
class Keyboard(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="The full name of the keyboard (e.g., Corsair K70 RGB MK.2 Mechanical Gaming Keyboard)"
    )
    CONNECTION_CHOICES = [("Wired", "Wired"), ("Wireless", "Wireless")]
    TYPE_CHOICES = [("Mechanical", "Mechanical"), ("Membrane", "Membrane")]

    brand = models.CharField(max_length=50, help_text="Enter the brand (e.g., Corsair, ASUS)")
    model_name = models.CharField(max_length=100)
    connection_type = models.CharField(max_length=10, choices=CONNECTION_CHOICES)
    keyboard_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    has_rgb = models.BooleanField(default=False, help_text="RGB lighting?")
    num_keys = models.PositiveIntegerField(help_text="Total keys count")

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the keyboard"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this keyboard a top pick?"
    )

    # Images (Required)
    images = GenericRelation(ProductImage)

    # SKU (Automatically Generated)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the keyboard"
    )

    description = models.TextField(
        null=False, 
        default="Responsive keyboard with comfortable key travel and durable switches. Features anti-ghosting technology for accurate input during intensive use.",
        help_text="Detailed description of the keyboard"
    )

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model_name[:3]}{self.keyboard_type[:3]}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model_name} - {self.keyboard_type}, {self.connection_type}"

# Headset Model
class Headset(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="The full name of the headset (e.g., HyperX Cloud II Wireless Gaming Headset)"
    )
    CONNECTION_CHOICES = [("Wired", "Wired"), ("Wireless", "Wireless")]

    brand = models.CharField(max_length=50, help_text="Enter the brand (e.g., HyperX, SteelSeries)")
    model_name = models.CharField(max_length=100)
    connection_type = models.CharField(max_length=10, choices=CONNECTION_CHOICES)
    has_microphone = models.BooleanField(default=True, help_text="Has a microphone?")
    surround_sound = models.BooleanField(default=False, help_text="Virtual Surround Sound?")

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the headset"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this headset a top pick?"
    )

    # Images (Required)
    images = GenericRelation(ProductImage)

    # SKU (Automatically Generated)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the headset"
    )

    description = models.TextField(
        null=False, 
        default="Immersive audio headset with comfortable ear cups and clear microphone. Designed for extended gaming sessions with excellent sound positioning.",
        help_text="Detailed description of the headset"
    )

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model_name[:3]}{self.connection_type[:3]}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model_name} - {self.connection_type}, Mic: {self.has_microphone}"

# Speakers Model
class Speakers(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="The full name of the speakers (e.g., Logitech Z623 2.1 Speaker System)"
    )
    CONNECTION_CHOICES = [("Wired", "Wired"), ("Bluetooth", "Bluetooth")]

    brand = models.CharField(max_length=50, help_text="Enter the brand (e.g., Bose, JBL)")
    model_name = models.CharField(max_length=100)
    connection_type = models.CharField(max_length=10, choices=CONNECTION_CHOICES)
    wattage = models.PositiveIntegerField(help_text="Total Wattage (e.g., 50W)")
    has_subwoofer = models.BooleanField(default=False, help_text="Has a subwoofer?")

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the speakers"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this speaker set a top pick?"
    )

    # Images (Required)
    images = GenericRelation(ProductImage)

    # SKU (Automatically Generated)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the speakers"
    )

    description = models.TextField(
        null=False, 
        default="Premium speakers delivering rich, balanced sound with deep bass response. Compact design with multiple connectivity options for versatile setup.",
        help_text="Detailed description of the speakers"
    )

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model_name[:3]}{self.wattage}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model_name} - {self.connection_type}, {self.wattage}W"

# Other Accessories Model
class OtherAccessory(models.Model):
    # Basic Information
    name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="The full name of the accessory (e.g., NZXT Kraken Z73 360mm AIO Liquid Cooler)"
    )
    brand = models.CharField(max_length=50, help_text="Enter the brand (e.g., Generic, Lenovo)")
    model_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, help_text="Category (e.g., Cooling Pad, USB Hub)")

    # Condition (Choices)
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('box_open', 'Box Open'),
    ]
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        help_text="The condition of the accessory"
    )
    
    # Warranty (Choices)
    WARRANTY_CHOICES = [
        ('no_warranty', 'No Warranty'),
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('3_years', '3 Years'),
    ]
    warranty = models.CharField(
        max_length=20, 
        choices=WARRANTY_CHOICES, 
        blank=True, 
        help_text="The warranty period"
    )
    
    # Top Pick (Boolean Field)
    top_pick = models.BooleanField(
        default=False, 
        help_text="Is this accessory a top pick?"
    )

    # Images (Required)
    images = GenericRelation(ProductImage)

    # SKU (Automatically Generated)
    sku = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False
    )

    # Price (Optional)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="The price of the accessory"
    )

    description = models.TextField(
        null=False, 
        default="High-quality accessory designed to enhance your computing experience. Features durable construction and excellent compatibility.",
        help_text="Detailed description of the accessory"
    )

    def save(self, *args, **kwargs):
        if not self.sku:
            base_number = f"{self.brand[:3]}{self.model_name[:3]}{self.category[:3]}"
            unique_id = str(uuid.uuid4().int)[:6]
            self.sku = f"{base_number}{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model_name} - {self.category}"        

class ComparisonList(models.Model):
    """Model to store comparison lists for users"""
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='comparison_lists'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product_type = models.CharField(
        max_length=50,
        help_text="Type of products in this comparison (e.g., 'GPU', 'Laptop')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Comparison List"
        verbose_name_plural = "Comparison Lists"
    
    def __str__(self):
        owner = self.user.username if self.user else f"Session {self.session_key[:8]}"
        return f"{self.product_type} Comparison by {owner}"


class ComparisonItem(models.Model):
    """Individual items in a comparison list"""
    comparison_list = models.ForeignKey(
        ComparisonList, 
        on_delete=models.CASCADE,
        related_name='items'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Comparison Item"
        verbose_name_plural = "Comparison Items"
        ordering = ['added_at']
    
    def __str__(self):
        return f"{self.product} in {self.comparison_list}"

# Add this to your models.py file
class WishlistItem(models.Model):
    """Individual items in a user's wishlist"""
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='wishlist_items'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"
        ordering = ['-added_at']
    
    def __str__(self):
        owner = self.user.username if self.user else f"Session {self.session_key[:8]}"
        return f"{self.product} in {owner}'s wishlist"

# Add this to your existing models.py file

class Slider(models.Model):
    """Model for homepage slider images and content"""
    title = models.CharField(max_length=100, help_text="Internal title for this slide (not displayed)")
    heading = models.CharField(max_length=100, help_text="Main heading displayed on the slide")
    subheading = models.CharField(max_length=200, blank=True, help_text="Optional subheading displayed below the main heading")
    image = models.ImageField(upload_to='sliders/', help_text="Image for this slide (recommended size: 1920x800px)")
    button_text = models.CharField(max_length=30, blank=True, help_text="Optional button text (leave empty for no button)")
    button_link = models.CharField(max_length=255, blank=True, help_text="URL for the button (required if button text is provided)")
    order = models.PositiveIntegerField(default=0, help_text="Order in which slides are displayed (lower numbers first)")
    is_active = models.BooleanField(default=True, help_text="Whether this slide is currently displayed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    description = models.TextField(
        null=False,
        default="Featured promotional content for the homepage slider.",
        help_text="Additional information about this slider (not displayed on frontend)"
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Slider"
        verbose_name_plural = "Sliders"

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.email})"

class SiteNumber(models.Model):
    number = models.CharField(max_length=32, help_text="Primary contact number to display site-wide.")

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Site Number"
        verbose_name_plural = "Site Number"