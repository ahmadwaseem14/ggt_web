from django.contrib import admin
from .models import (
    GPU, CPU, RAM, Motherboard, Case, StorageDevice, 
    PSU, Monitor, Mouse, Keyboard, Headset, Speakers, 
    OtherAccessory, Tablet, Laptop, ProductImage, Slider, Subscriber, ContactMessage, SiteNumber
)
from .forms import (
    GPUForm, CPUForm, RAMForm, MotherboardForm, CaseForm, 
    StorageDeviceForm, PSUForm, MonitorForm, MouseForm, 
    KeyboardForm, HeadsetForm, SpeakersForm, OtherAccessoryForm,
    TabletForm, LaptopForm
)
from django.contrib.contenttypes.admin import GenericTabularInline

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['content_object', 'image', 'is_primary', 'uploaded_at']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['alt_text']

class ProductImageInline(GenericTabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary']
    max_num = 10

# Common base list_display and list_filter for all models
BASE_LIST_DISPLAY = ['name', 'brand', 'sku', 'price', 'condition', 'top_pick']
BASE_LIST_FILTER = ['brand', 'condition', 'warranty', 'top_pick']
BASE_SEARCH_FIELDS = ['name', 'brand', 'sku']

@admin.register(GPU)
class GPUAdmin(admin.ModelAdmin):
    form = GPUForm
    list_display = BASE_LIST_DISPLAY + ['model', 'vram']  # sku already in BASE_LIST_DISPLAY
    list_filter = BASE_LIST_FILTER + ['vram']
    search_fields = BASE_SEARCH_FIELDS + ['description']
    inlines = [ProductImageInline]

@admin.register(CPU)
class CPUAdmin(admin.ModelAdmin):
    form = CPUForm
    list_display = BASE_LIST_DISPLAY + ['model', 'cores']  # sku already in BASE_LIST_DISPLAY
    list_filter = BASE_LIST_FILTER + ['cores']
    search_fields = BASE_SEARCH_FIELDS + ['description']
    inlines = [ProductImageInline]

@admin.register(RAM)
class RAMAdmin(admin.ModelAdmin):
    form = RAMForm
    list_display = BASE_LIST_DISPLAY + ['model_name', 'capacity']  # sku already in BASE_LIST_DISPLAY
    list_filter = BASE_LIST_FILTER + ['capacity']
    search_fields = BASE_SEARCH_FIELDS + ['description']
    inlines = [ProductImageInline]

@admin.register(Motherboard)
class MotherboardAdmin(admin.ModelAdmin):
    form = MotherboardForm
    list_display = ['brand', 'model', 'socket', 'condition', 'warranty', 'top_pick', 'price', 'sku']
    list_filter = ['brand', 'socket', 'condition', 'warranty', 'top_pick']
    search_fields = ['brand', 'model', 'sku', 'description']
    inlines = [ProductImageInline]

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    form = CaseForm
    list_display = ['brand', 'model', 'case_type', 'condition', 'warranty', 'top_pick', 'sku']
    list_filter = ['brand', 'case_type', 'condition', 'warranty', 'top_pick']
    search_fields = ['brand', 'model', 'sku', 'description']
    inlines = [ProductImageInline]

@admin.register(StorageDevice)
class StorageDeviceAdmin(admin.ModelAdmin):
    form = StorageDeviceForm
    list_display = ['brand', 'model_name', 'storage_type', 'capacity', 'condition', 'warranty', 'top_pick', 'sku']
    list_filter = ['brand', 'storage_type', 'condition', 'warranty', 'top_pick']
    search_fields = ['brand', 'model_name', 'sku', 'description']
    inlines = [ProductImageInline]

@admin.register(PSU)
class PSUAdmin(admin.ModelAdmin):
    form = PSUForm
    list_display = ['brand', 'model_name', 'wattage', 'efficiency_rating', 'condition', 'warranty', 'top_pick', 'sku']
    list_filter = ['brand', 'wattage', 'condition', 'warranty', 'top_pick']
    search_fields = ['brand', 'model_name', 'sku', 'description']
    inlines = [ProductImageInline]

@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    form = MonitorForm
    list_display = ['brand', 'model_name', 'screen_size', 'resolution', 'condition', 'warranty', 'top_pick', 'price', 'sku']
    list_filter = ['brand', 'panel_type', 'condition', 'warranty', 'top_pick']
    search_fields = ['brand', 'model_name', 'sku', 'description']
    inlines = [ProductImageInline]

@admin.register(Mouse)
class MouseAdmin(admin.ModelAdmin):
    form = MouseForm
    list_display = ['brand', 'model_name', 'connection_type', 'condition', 'warranty', 'top_pick', 'sku']
    list_filter = ['brand', 'connection_type', 'condition', 'warranty', 'top_pick']
    search_fields = ['brand', 'model_name', 'sku', 'description']
    inlines = [ProductImageInline]

@admin.register(Keyboard)
class KeyboardAdmin(admin.ModelAdmin):
    form = KeyboardForm
    list_display = ['brand', 'model_name', 'keyboard_type', 'condition', 'warranty', 'top_pick', 'sku']
    list_filter = ['brand', 'keyboard_type', 'condition', 'warranty', 'top_pick']
    search_fields = ['brand', 'model_name', 'sku', 'description']
    inlines = [ProductImageInline]

@admin.register(Headset)
class HeadsetAdmin(admin.ModelAdmin):
    form = HeadsetForm
    list_display = ['brand', 'model_name', 'connection_type', 'condition', 'warranty', 'top_pick', 'sku']
    list_filter = ['brand', 'connection_type', 'condition', 'warranty', 'top_pick']
    search_fields = ['brand', 'model_name', 'sku', 'description']
    inlines = [ProductImageInline]

@admin.register(Speakers)
class SpeakersAdmin(admin.ModelAdmin):
    form = SpeakersForm
    list_display = ['brand', 'model_name', 'connection_type', 'wattage', 'condition', 'warranty', 'top_pick', 'sku']
    list_filter = ['brand', 'connection_type', 'condition', 'warranty', 'top_pick']
    search_fields = ['brand', 'model_name', 'sku', 'description']
    inlines = [ProductImageInline]

@admin.register(OtherAccessory)
class OtherAccessoryAdmin(admin.ModelAdmin):
    form = OtherAccessoryForm
    list_display = ['brand', 'model_name', 'category', 'condition', 'warranty', 'top_pick', 'sku']
    list_filter = ['brand', 'category', 'condition', 'warranty', 'top_pick']
    search_fields = ['brand', 'model_name', 'sku', 'description']
    inlines = [ProductImageInline]

@admin.register(Tablet)
class TabletAdmin(admin.ModelAdmin):
    form = TabletForm
    list_display = [
        'name', 'brand', 'model', 'screen_size', 'chipset',
        'ram', 'storage', 'condition', 'warranty', 'top_pick', 'sku'
    ]
    list_filter = [
        'brand', 'ram', 'storage', 'screen_type',
        'cellular', 'pta_approved', 'condition', 'warranty', 'top_pick'
    ]
    search_fields = ['name', 'brand', 'model', 'sku', 'chipset', 'description']
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'brand', 'model']
        }),
        ('Display', {
            'fields': ['screen_size', 'screen_type', 'resolution', 'refresh_rate']
        }),
        ('Performance', {
            'fields': ['chipset', 'ram', 'storage']
        }),
        ('Battery & Charging', {
            'fields': ['battery_capacity', 'fast_charging', 'wireless_charging', 'charging_wattage']
        }),
        ('Camera', {
            'fields': ['rear_camera_mp', 'front_camera_mp']
        }),
        ('Connectivity & Ports', {
            'fields': ['cellular', 'sim_type', 'usb_type', 'headphone_jack', 'sd_card_slot']
        }),
        ('Software & Features', {
            'fields': ['os', 'os_version', 'pta_approved']
        }),
        ('Physical Specifications', {
            'fields': ['weight', 'dimensions', 'material']
        }),
        ('Additional Features', {
            'fields': ['stylus_support', 'keyboard_support', 'biometric_auth']
        }),
        ('Product Status', {
            'fields': ['condition', 'warranty', 'top_pick']
        }),
    ]
    inlines = [ProductImageInline]

@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    form = LaptopForm
    list_display = BASE_LIST_DISPLAY + ['model_name', 'processor_model', 'ram_capacity']  # sku already in BASE_LIST_DISPLAY
    list_filter = BASE_LIST_FILTER + ['processor_brand', 'ram_capacity', 'storage_type']
    search_fields = BASE_SEARCH_FIELDS + ['processor_model', 'model_name', 'description']
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'brand', 'model_name']
        }),
        ('Processor', {
            'fields': [
                'processor_brand', 'processor_model', 'processor_generation',
                'core_count', 'base_clock', 'boost_clock'
            ]
        }),
        ('Memory & Storage', {
            'fields': [
                'ram_capacity', 'ram_type', 'ram_speed',
                'storage_type', 'storage_capacity'
            ]
        }),
        ('Display', {
            'fields': [
                'screen_size', 'resolution', 'refresh_rate',
                'display_type', 'brightness', 'touch_screen'
            ]
        }),
        ('Graphics', {
            'fields': [
                'gpu_brand', 'gpu_model', 'gpu_memory'
            ]
        }),
        ('Battery & Power', {
            'fields': [
                'battery_capacity', 'battery_life',
                'power_adapter', 'fast_charging'
            ]
        }),
        ('Connectivity', {
            'fields': [
                'wifi_standard', 'bluetooth_version',
                'usb_ports', 'hdmi_ports', 'ethernet_port',
                'headphone_jack', 'card_reader'
            ]
        }),
        ('Physical Specifications', {
            'fields': [
                'weight', 'dimensions', 'build_material',
                'color', 'backlit_keyboard', 'fingerprint_sensor'
            ]
        }),
        ('Operating System', {
            'fields': [
                'operating_system', 'os_version'
            ]
        }),
        ('Additional Features', {
            'fields': [
                'webcam_resolution', 'speakers', 'microphone',
                'numeric_keypad', 'warranty_info'
            ]
        }),
        ('Product Status', {
            'fields': ['condition', 'warranty', 'top_pick', 'price']
        }),
    ]
    inlines = [ProductImageInline]

class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'heading', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'heading', 'subheading', 'description')
    list_editable = ('order', 'is_active')
    fieldsets = (
        ('Content', {
            'fields': ('title', 'heading', 'subheading', 'image')
        }),
        ('Button', {
            'fields': ('button_text', 'button_link')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
        ('Additional Information', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )
    
admin.site.register(Slider, SliderAdmin)

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed', 'is_active')
    list_filter = ('is_active', 'date_subscribed')
    search_fields = ('email',)
    date_hierarchy = 'date_subscribed'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at', 'is_read')
    list_filter = ('is_read', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'submitted_at')
    ordering = ('-submitted_at',)

@admin.register(SiteNumber)
class SiteNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)

    def has_add_permission(self, request):
        # Only allow one instance
        if SiteNumber.objects.count() >= 1:
            return False
        return super().has_add_permission(request)