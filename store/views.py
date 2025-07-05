from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from itertools import chain
from operator import attrgetter
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from .models import GPU, CPU, RAM, Motherboard, Case, StorageDevice, PSU, Monitor, Tablet, Laptop, ComparisonList, ComparisonItem, WishlistItem, Slider, Mouse, Keyboard, Headset, Speakers, OtherAccessory
from django.db import models
from .forms import SubscriberForm, ContactForm

def home(request):
    """
    Home page view that displays top picks and latest arrivals
    """
    # Get active sliders ordered by their display order
    sliders = Slider.objects.filter(is_active=True).order_by('order')
    
    # Get the last 10 top picks for each category
    top_gpus = GPU.objects.filter(top_pick=True).order_by('-id')[:10]
    top_laptops = Laptop.objects.filter(top_pick=True).order_by('-id')[:10]
    top_tablets = Tablet.objects.filter(top_pick=True).order_by('-id')[:10]
    top_cases = Case.objects.filter(top_pick=True).order_by('-id')[:10]
    
    # Get latest arrivals (10 most recent products across selected categories)
    latest_gpus = GPU.objects.all().order_by('-id')[:6]
    latest_cpus = CPU.objects.all().order_by('-id')[:5]
    latest_rams = RAM.objects.all().order_by('-id')[:5]
    latest_motherboards = Motherboard.objects.all().order_by('-id')[:5]
    latest_cases = Case.objects.all().order_by('-id')[:5]
    latest_storage = StorageDevice.objects.all().order_by('-id')[:5]
    latest_psus = PSU.objects.all().order_by('-id')[:5]
    latest_monitors = Monitor.objects.all().order_by('-id')[:5]
    latest_tablets = Tablet.objects.all().order_by('-id')[:5]
    latest_laptops = Laptop.objects.all().order_by('-id')[:5]
    
    # Combine all latest products
    latest_products = sorted(
        chain(
            latest_gpus, latest_cpus, latest_rams, latest_motherboards,
            latest_cases, latest_storage, latest_psus, latest_monitors,
            latest_tablets, latest_laptops
        ),
        key=attrgetter('id'),
        reverse=True
    )[:20]  # Get the 20 most recent products overall
    
    # Create context dictionary with all data
    context = {
        'sliders': sliders,
        'top_gpus': top_gpus,
        'top_laptops': top_laptops,
        'top_tablets': top_tablets,
        'top_cases': top_cases,
        'latest_products': latest_products,
        'title': 'Home - Top PC Components and Devices'
    }
    
    return render(request, 'home/home.html', context)

def laptops_list(request):
    """
    View to display all laptops with filtering capabilities
    """
    # Start with all laptops
    laptops = Laptop.objects.all()
    
    # Get filter parameters from request
    brand = request.GET.get('brand')
    condition = request.GET.get('condition')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    processor = request.GET.get('processor')
    min_ram = request.GET.get('min_ram')
    min_storage = request.GET.get('min_storage')
    sort_by = request.GET.get('sort_by', 'newest')  # Default sort by newest
    
    # Apply filters
    if brand:
        laptops = laptops.filter(brand__iexact=brand)
    
    if condition:
        laptops = laptops.filter(condition__iexact=condition)
    
    if min_price:
        try:
            laptops = laptops.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            laptops = laptops.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            pass
    
    if processor:
        laptops = laptops.filter(processor_brand__icontains=processor)
    
    if min_ram:
        try:
            laptops = laptops.filter(ram_capacity__gte=int(min_ram))
        except (ValueError, TypeError):
            pass
    
    if min_storage:
        try:
            laptops = laptops.filter(storage_capacity__gte=int(min_storage))
        except (ValueError, TypeError):
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        laptops = laptops.order_by('price')
    elif sort_by == 'price_high':
        laptops = laptops.order_by('-price')
    elif sort_by == 'name_asc':
        laptops = laptops.order_by('name')
    elif sort_by == 'name_desc':
        laptops = laptops.order_by('-name')
    else:  # newest
        laptops = laptops.order_by('-id')
    
    # Get unique values for filter dropdowns
    all_brands = Laptop.objects.values_list('brand', flat=True).distinct()
    all_processors = Laptop.objects.values_list('processor_brand', flat=True).distinct()
    
    # Get min and max prices for price range filter
    price_range = Laptop.objects.aggregate(
        min_price=models.Min('price'),
        max_price=models.Max('price')
    )
    
    context = {
        'laptops': laptops,
        'all_brands': all_brands,
        'all_processors': all_processors,
        'current_brand': brand,
        'current_condition': condition,
        'current_processor': processor,
        'current_min_ram': min_ram,
        'current_min_storage': min_storage,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_sort': sort_by,
        'price_range': price_range,
        'title': 'Laptops - Browse All Models'
    }
    
    return render(request, 'store/laptops_list.html', context)

def laptop_detail(request, pk):
    """
    View to display detailed information about a specific laptop
    """
    laptop = get_object_or_404(Laptop, pk=pk)
    
    context = {
        'laptop': laptop,
        'title': f'{laptop.name} - Details'
    }
    
    return render(request, 'store/laptop_detail.html', context)

def add_to_comparison(request, product_sku):
    """Add a product to the comparison list using SKU"""
    # Map model names to their classes
    model_map = {
        'gpu': GPU,
        'cpu': CPU,
        'ram': RAM,
        'motherboard': Motherboard,
        'case': Case,
        'storagedevice': StorageDevice,
        'psu': PSU,
        'monitor': Monitor,
        'tablet': Tablet,
        'laptop': Laptop,
    }
    
    # Try to find the product in any of the models by SKU
    product = None
    model_name = None
    content_type = None
    
    for model_key, model_class in model_map.items():
        try:
            product = model_class.objects.get(sku=product_sku)
            model_name = model_key
            content_type = ContentType.objects.get_for_model(model_class)
            break
        except model_class.DoesNotExist:
            continue
    
    if not product:
        messages.error(request, f"Product with SKU {product_sku} not found.")
        return redirect('home')
    
    # Print debug information
    print(f"Found product: {product}, type: {model_name}, content_type: {content_type}")
    
    # Get comparison lists for the user/session
    if request.user.is_authenticated:
        comparison_lists = ComparisonList.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        comparison_lists = ComparisonList.objects.filter(session_key=session_key)
    
    # Check if there's an existing comparison list with a different product type
    for existing_list in comparison_lists:
        if existing_list.product_type != model_name and existing_list.items.exists():
            # Clear any existing messages first
            storage = messages.get_messages(request)
            for message in storage:
                pass  # This consumes the messages
            
            # Add the new error message
            messages.error(
                request, 
                f"Cannot add {model_name.upper()} to comparison. You already have a {existing_list.product_type.upper()} comparison list. Please clear your existing comparison first."
            )
            return redirect('comparison_view')
    
    # Get or create the appropriate comparison list
    if request.user.is_authenticated:
        comparison_list, created = ComparisonList.objects.get_or_create(
            user=request.user,
            product_type=model_name,
        )
    else:
        comparison_list, created = ComparisonList.objects.get_or_create(
            session_key=session_key,
            product_type=model_name,
        )
    
    # Check if this product is already in the comparison
    if ComparisonItem.objects.filter(
        comparison_list=comparison_list,
        content_type=content_type,
        object_id=product.id
    ).exists():
        messages.info(request, f"{product} is already in your comparison list.")
        return redirect('comparison_view')
    
    # Add the product to the comparison list
    ComparisonItem.objects.create(
        comparison_list=comparison_list,
        content_type=content_type,
        object_id=product.id
    )
    
    messages.success(request, f"{product} ({model_name.upper()}) added to your comparison list.")
    return redirect('comparison_view')

def comparison_view(request):
    """View the comparison list with all model fields"""
    if request.user.is_authenticated:
        comparison_lists = ComparisonList.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            comparison_lists = ComparisonList.objects.none()
        else:
            comparison_lists = ComparisonList.objects.filter(session_key=session_key)
    
    # For each comparison list, get all fields from the model
    for comparison_list in comparison_lists:
        if comparison_list.items.exists():
            first_item = comparison_list.items.first()
            model_class = first_item.content_type.model_class()
            
            # Get all fields from the model (excluding common fields)
            exclude_fields = ['id', 'sku', 'name', 'brand', 'price', 'old_price', 
                             'condition', 'description', 'top_pick', 'created_at', 
                             'updated_at', 'images']
            
            model_fields = []
            for field in model_class._meta.get_fields():
                if hasattr(field, 'name') and field.name not in exclude_fields and not field.is_relation:
                    model_fields.append({
                        'name': field.name,
                        'verbose_name': field.verbose_name.title() if hasattr(field, 'verbose_name') else field.name.replace('_', ' ').title(),
                        'field_type': field.get_internal_type()
                    })
            
            comparison_list.model_fields = model_fields
    
    context = {
        'comparison_lists': comparison_lists,
        'title': 'Product Comparison'
    }
    
    return render(request, 'store/comparison.html', context)

def remove_from_comparison(request, item_id):
    """Remove an item from the comparison list"""
    item = get_object_or_404(ComparisonItem, id=item_id)
    comparison_list = item.comparison_list
    
    # Check if the user owns this comparison list
    if request.user.is_authenticated:
        if comparison_list.user != request.user:
            messages.error(request, "You don't have permission to remove this item.")
            return redirect('comparison_view')
    else:
        session_key = request.session.session_key
        if comparison_list.session_key != session_key:
            messages.error(request, "You don't have permission to remove this item.")
            return redirect('comparison_view')
    
    product_name = str(item.product)
    item.delete()
    
    # Check if the comparison list is now empty
    if comparison_list.items.count() == 0:
        # Delete the empty comparison list
        comparison_list.delete()
        messages.success(request, f"{product_name} removed and empty comparison list deleted.")
    else:
        messages.success(request, f"{product_name} removed from your comparison list.")
    
    return redirect('comparison_view')

def clear_comparison(request, comparison_id):
    """Clear all items from a comparison list"""
    comparison_list = get_object_or_404(ComparisonList, id=comparison_id)
    
    # Check if the user owns this comparison list
    if request.user.is_authenticated:
        if comparison_list.user != request.user:
            messages.error(request, "You don't have permission to clear this comparison list.")
            return redirect('comparison_view')
    else:
        session_key = request.session.session_key
        if comparison_list.session_key != session_key:
            messages.error(request, "You don't have permission to clear this comparison list.")
            return redirect('comparison_view')
    
    # Get the product type before deleting
    product_type = comparison_list.product_type
    
    # Delete all items in the comparison list
    comparison_list.items.all().delete()
    
    # Delete the empty comparison list
    comparison_list.delete()
    
    messages.success(request, f"{product_type.upper()} comparison list cleared and removed.")
    return redirect('comparison_view')

def debug_comparison(request):
    """Debug view to see what's in the comparison lists"""
    if not request.user.is_superuser:
        return redirect('home')
    
    all_lists = ComparisonList.objects.all()
    all_items = ComparisonItem.objects.all()
    
    context = {
        'all_lists': all_lists,
        'all_items': all_items,
    }
    
    return render(request, 'store/debug_comparison.html', context)

def wishlist_view(request):
    """View the user's wishlist"""
    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            wishlist_items = WishlistItem.objects.none()
        else:
            wishlist_items = WishlistItem.objects.filter(session_key=session_key)
    
    context = {
        'wishlist_items': wishlist_items,
        'title': 'My Wishlist'
    }
    
    return render(request, 'store/wishlist.html', context)

def add_to_wishlist(request, product_sku):
    """Add a product to the wishlist using SKU"""
    # Map model names to their classes
    model_map = {
        'gpu': GPU,
        'cpu': CPU,
        'ram': RAM,
        'motherboard': Motherboard,
        'case': Case,
        'storagedevice': StorageDevice,
        'psu': PSU,
        'monitor': Monitor,
        'tablet': Tablet,
        'laptop': Laptop,
    }
    
    # Try to find the product in any of the models by SKU
    product = None
    content_type = None
    
    for model_key, model_class in model_map.items():
        try:
            product = model_class.objects.get(sku=product_sku)
            content_type = ContentType.objects.get_for_model(model_class)
            break
        except model_class.DoesNotExist:
            continue
    
    if not product:
        messages.error(request, f"Product with SKU {product_sku} not found.")
        return redirect('home')
    
    # Add to wishlist
    if request.user.is_authenticated:
        # Check if already in wishlist
        if WishlistItem.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=product.id
        ).exists():
            messages.info(request, f"{product} is already in your wishlist.")
            return redirect('wishlist_view')
            
        # Add to wishlist
        WishlistItem.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=product.id
        )
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
            
        # Check if already in wishlist
        if WishlistItem.objects.filter(
            session_key=session_key,
            content_type=content_type,
            object_id=product.id
        ).exists():
            messages.info(request, f"{product} is already in your wishlist.")
            return redirect('wishlist_view')
            
        # Add to wishlist
        WishlistItem.objects.create(
            session_key=session_key,
            content_type=content_type,
            object_id=product.id
        )
    
    messages.success(request, f"{product} added to your wishlist.")
    return redirect('wishlist_view')

def remove_from_wishlist(request, item_id):
    """Remove an item from the wishlist"""
    item = get_object_or_404(WishlistItem, id=item_id)
    
    # Check if the user owns this wishlist item
    if request.user.is_authenticated:
        if item.user != request.user:
            messages.error(request, "You don't have permission to remove this item.")
            return redirect('wishlist_view')
    else:
        session_key = request.session.session_key
        if item.session_key != session_key:
            messages.error(request, "You don't have permission to remove this item.")
            return redirect('wishlist_view')
    
    product_name = str(item.product)
    item.delete()
    
    messages.success(request, f"{product_name} removed from your wishlist.")
    return redirect('wishlist_view')

def quick_view(request, product_sku):
    """AJAX view to display a quick preview of a product"""
    # Map model names to their classes
    model_map = {
        'gpu': GPU,
        'cpu': CPU,
        'ram': RAM,
        'motherboard': Motherboard,
        'case': Case,
        'storagedevice': StorageDevice,
        'psu': PSU,
        'monitor': Monitor,
        'tablet': Tablet,
        'laptop': Laptop,
    }
    
    # Try to find the product in any of the models by SKU
    product = None
    model_name = None
    
    for model_key, model_class in model_map.items():
        try:
            product = model_class.objects.get(sku=product_sku)
            model_name = model_key
            break
        except model_class.DoesNotExist:
            continue
    
    if not product:
        return JsonResponse({'error': f"Product with SKU {product_sku} not found."}, status=404)
    
    context = {
        'product': product,
        'model_name': model_name,
    }
    
    return render(request, 'store/quick_view.html', context)

def product_detail(request, product_sku):
    """
    Generic product detail view that works for all product types using only SKU
    """
    # Map model names to their classes
    model_map = {
        'gpu': GPU,
        'cpu': CPU,
        'ram': RAM,
        'motherboard': Motherboard,
        'case': Case,
        'storagedevice': StorageDevice,
        'psu': PSU,
        'monitor': Monitor,
        'tablet': Tablet,
        'laptop': Laptop,
    }
    
    # Try to find the product in any of the models by SKU
    product = None
    product_type = None
    model_class = None
    
    for model_key, model_class_temp in model_map.items():
        try:
            product = model_class_temp.objects.get(sku=product_sku)
            product_type = model_key
            model_class = model_class_temp
            break
        except model_class_temp.DoesNotExist:
            continue
    
    if not product:
        messages.error(request, f"Product with SKU {product_sku} not found.")
        return redirect('home')
    
    # Get related products (same type, same brand, excluding current product)
    related_products = model_class.objects.filter(
        brand=product.brand
    ).exclude(
        id=product.id
    ).order_by('-top_pick', '?')[:4]  # Prioritize top picks, then random
    
    # Get specifications based on product fields
    specs = get_product_specs_from_fields(product)
    
    context = {
        'product': product,
        'product_type': product_type,
        'related_products': related_products,
        'specs': specs,
        'title': f'{product.name} - Details'
    }
    
    return render(request, 'store/product_detail.html', context)

def get_product_specs_from_fields(product):
    """
    Get product specifications by inspecting model fields
    Returns a list of dictionaries with section name and specs
    """
    specs = []
    
    # Get model fields
    fields = product._meta.get_fields()
    
    # Common specifications (always shown first)
    common_specs = {
        'Brand': product.brand,
        'SKU': product.sku,
        'Condition': product.condition.title() if hasattr(product, 'condition') else None,
    }
    
    # Filter out None values
    common_specs = {k: v for k, v in common_specs.items() if v is not None}
    
    # Add common specs section
    if common_specs:
        specs.append({'name': 'General', 'items': common_specs})
    
    # Technical specifications
    tech_specs = {}
    
    # Skip these fields as they're either in common specs or not relevant for display
    skip_fields = ['id', 'name', 'brand', 'sku', 'condition', 'price', 'old_price', 
                  'top_pick', 'description', 'created_at', 'updated_at', 'images']
    
    # Process each field
    for field in fields:
        # Skip relation fields and fields in skip_fields
        if field.is_relation or field.name in skip_fields:
            continue
        
        # Get the value
        value = getattr(product, field.name, None)
        
        # Skip None values
        if value is None:
            continue
        
        # Format field name for display
        field_name = field.name.replace('_', ' ').title()
        
        # Format value based on field type
        if isinstance(value, bool):
            formatted_value = "Yes" if value else "No"
        elif field.name.endswith('_clock') and isinstance(value, (int, float)):
            formatted_value = f"{value} MHz"
        elif field.name == 'tdp' and isinstance(value, (int, float)):
            formatted_value = f"{value} W"
        elif field.name in ['memory_size', 'vram', 'ram', 'capacity'] and isinstance(value, (int, float)):
            formatted_value = f"{value} GB"
        elif field.name == 'screen_size' and isinstance(value, (int, float)):
            formatted_value = f"{value}\""
        elif field.name == 'refresh_rate' and isinstance(value, (int, float)):
            formatted_value = f"{value} Hz"
        elif field.name == 'response_time' and isinstance(value, (int, float)):
            formatted_value = f"{value} ms"
        elif field.name == 'wattage' and isinstance(value, (int, float)):
            formatted_value = f"{value} W"
        else:
            formatted_value = str(value)
        
        tech_specs[field_name] = formatted_value
    
    # Add technical specs section if not empty
    if tech_specs:
        specs.append({'name': 'Technical Specifications', 'items': tech_specs})
    
    return specs

def product_list(request, product_type=None):
    """
    Generic product listing view with filtering capabilities
    """
    # Convert product_type to lowercase for case-insensitive matching
    product_type = product_type.lower() if product_type else None
    
    # Map model names to their classes
    model_map = {
        'gpu': GPU,
        'cpu': CPU,
        'ram': RAM,
        'motherboard': Motherboard,
        'case': Case,
        'storage': StorageDevice,
        'psu': PSU,
        'monitor': Monitor,
        'tablet': Tablet,
        'laptop': Laptop,
        'mouse': Mouse,
        'keyboard': Keyboard,
        'headset': Headset,
        'speakers': Speakers,
    }
    
    # Get the model class based on product_type
    if product_type not in model_map:
        messages.error(request, f"Invalid product type: {product_type}")
        return redirect('home')
    
    model_class = model_map[product_type]
    
    # Start with all products of the given type
    products = model_class.objects.all()
    
    # Get common filter parameters from request
    brand = request.GET.get('brand')
    condition = request.GET.get('condition')
    sort_by = request.GET.get('sort_by', 'newest')  # Default sort by newest
    
    # Apply common filters
    if brand:
        products = products.filter(brand__iexact=brand)
    
    if condition:
        products = products.filter(condition__iexact=condition)
    
    # Apply product-specific filters
    filter_options = {}
    model_fields = [field.name for field in model_class._meta.get_fields()]
    
    if product_type == 'gpu':
        if 'vram' in model_fields:
            vram = request.GET.get('vram')
            if vram:
                try:
                    products = products.filter(vram=int(vram))
                except (ValueError, TypeError):
                    pass
            filter_options['vram_options'] = model_class.objects.values_list('vram', flat=True).distinct()
        if 'memory_type' in model_fields:
            memory_type = request.GET.get('memory_type')
            if memory_type:
                products = products.filter(memory_type__iexact=memory_type)
            filter_options['memory_type_options'] = model_class.objects.values_list('memory_type', flat=True).distinct()
    
    elif product_type == 'cpu':
        if 'generation' in model_fields:
            generation = request.GET.get('generation')
            if generation:
                products = products.filter(generation__icontains=generation)
            filter_options['generation_options'] = model_class.objects.values_list('generation', flat=True).distinct()
        if 'cores' in model_fields:
            cores = request.GET.get('cores')
            if cores:
                try:
                    products = products.filter(cores__gte=int(cores))
                except (ValueError, TypeError):
                    pass
            filter_options['cores_options'] = sorted(model_class.objects.values_list('cores', flat=True).distinct())
        if 'threads' in model_fields:
            threads = request.GET.get('threads')
            if threads:
                try:
                    products = products.filter(threads__gte=int(threads))
                except (ValueError, TypeError):
                    pass
            filter_options['threads_options'] = sorted(model_class.objects.values_list('threads', flat=True).distinct())
    
    elif product_type == 'ram':
        if 'ram_type' in model_fields:
            ram_type = request.GET.get('ram_type')
            if ram_type:
                products = products.filter(ram_type__iexact=ram_type)
            filter_options['ram_type_options'] = model_class.objects.values_list('ram_type', flat=True).distinct()
        if 'capacity' in model_fields:
            capacity = request.GET.get('capacity')
            if capacity:
                try:
                    products = products.filter(capacity__gte=int(capacity))
                except (ValueError, TypeError):
                    pass
            filter_options['capacity_options'] = sorted(model_class.objects.values_list('capacity', flat=True).distinct())
        if 'form_factor' in model_fields:
            form_factor = request.GET.get('form_factor')
            if form_factor:
                products = products.filter(form_factor__iexact=form_factor)
            filter_options['form_factor_options'] = model_class.objects.values_list('form_factor', flat=True).distinct()
    
    elif product_type == 'laptop':
        if 'ram_capacity' in model_fields:
            min_ram = request.GET.get('min_ram')
            if min_ram:
                try:
                    products = products.filter(ram_capacity__gte=int(min_ram))
                except (ValueError, TypeError):
                    pass
            filter_options['ram_options'] = sorted(model_class.objects.values_list('ram_capacity', flat=True).distinct())
        if 'screen_size' in model_fields:
            screen_size = request.GET.get('screen_size')
            if screen_size:
                try:
                    products = products.filter(screen_size=float(screen_size))
                except (ValueError, TypeError):
                    pass
            filter_options['screen_size_options'] = sorted(model_class.objects.values_list('screen_size', flat=True).distinct())
    
    elif product_type == 'tablet':
        if 'ram_capacity' in model_fields:
            min_ram = request.GET.get('min_ram')
            if min_ram:
                try:
                    products = products.filter(ram_capacity__gte=int(min_ram))
                except (ValueError, TypeError):
                    pass
            filter_options['ram_options'] = sorted(model_class.objects.values_list('ram_capacity', flat=True).distinct())
        if 'storage' in model_fields:
            storage = request.GET.get('storage')
            if storage:
                try:
                    products = products.filter(storage__gte=int(storage))
                except (ValueError, TypeError):
                    pass
            filter_options['storage_options'] = sorted(model_class.objects.values_list('storage', flat=True).distinct())
        if 'screen_size' in model_fields:
            screen_size = request.GET.get('screen_size')
            if screen_size:
                try:
                    products = products.filter(screen_size=float(screen_size))
                except (ValueError, TypeError):
                    pass
            filter_options['screen_size_options'] = sorted(model_class.objects.values_list('screen_size', flat=True).distinct())
    
    elif product_type == 'storage':
        if 'storage_type' in model_fields:
            storage_type = request.GET.get('storage_type')
            if storage_type:
                products = products.filter(storage_type__iexact=storage_type)
            filter_options['storage_type_options'] = model_class.objects.values_list('storage_type', flat=True).distinct()
        if 'form_factor' in model_fields:
            form_factor = request.GET.get('form_factor')
            if form_factor:
                products = products.filter(form_factor__iexact=form_factor)
            filter_options['form_factor_options'] = model_class.objects.values_list('form_factor', flat=True).distinct()
    
    elif product_type == 'psu':
        if 'form_factor' in model_fields:
            form_factor = request.GET.get('form_factor')
            if form_factor:
                products = products.filter(form_factor__iexact=form_factor)
            filter_options['form_factor_options'] = model_class.objects.values_list('form_factor', flat=True).distinct()
        if 'wattage' in model_fields:
            wattage = request.GET.get('wattage')
            if wattage:
                try:
                    products = products.filter(wattage__gte=int(wattage))
                except (ValueError, TypeError):
                    pass
            filter_options['wattage_options'] = sorted(model_class.objects.values_list('wattage', flat=True).distinct())
    
    elif product_type == 'case':
        if 'case_type' in model_fields:
            case_type = request.GET.get('case_type')
            if case_type:
                products = products.filter(case_type__iexact=case_type)
            filter_options['case_type_options'] = model_class.objects.values_list('case_type', flat=True).distinct()
    
    elif product_type == 'monitor':
        if 'resolution' in model_fields:
            resolution = request.GET.get('resolution')
            if resolution:
                products = products.filter(resolution__iexact=resolution)
            filter_options['resolution_options'] = model_class.objects.values_list('resolution', flat=True).distinct()
        if 'screen_size' in model_fields:
            screen_size = request.GET.get('screen_size')
            if screen_size:
                try:
                    products = products.filter(screen_size=float(screen_size))
                except (ValueError, TypeError):
                    pass
            filter_options['screen_size_options'] = sorted(model_class.objects.values_list('screen_size', flat=True).distinct())
    
    elif product_type == 'keyboard':
        if 'connection_type' in model_fields:
            connection_type = request.GET.get('connection_type')
            if connection_type:
                products = products.filter(connection_type__iexact=connection_type)
            filter_options['connection_type_options'] = model_class.objects.values_list('connection_type', flat=True).distinct()
        if 'keyboard_type' in model_fields:
            keyboard_type = request.GET.get('keyboard_type')
            if keyboard_type:
                products = products.filter(keyboard_type__iexact=keyboard_type)
            filter_options['keyboard_type_options'] = model_class.objects.values_list('keyboard_type', flat=True).distinct()
    
    elif product_type == 'mouse':
        if 'dpi' in model_fields:
            dpi = request.GET.get('dpi')
            if dpi:
                try:
                    products = products.filter(dpi__gte=int(dpi))
                except (ValueError, TypeError):
                    pass
            filter_options['dpi_options'] = sorted(model_class.objects.values_list('dpi', flat=True).distinct())
        if 'connection_type' in model_fields:
            connection_type = request.GET.get('connection_type')
            if connection_type:
                products = products.filter(connection_type__iexact=connection_type)
            filter_options['connection_type_options'] = model_class.objects.values_list('connection_type', flat=True).distinct()
        if 'buttons' in model_fields:
            buttons = request.GET.get('buttons')
            if buttons:
                try:
                    products = products.filter(buttons__gte=int(buttons))
                except (ValueError, TypeError):
                    pass
            filter_options['buttons_options'] = sorted(model_class.objects.values_list('buttons', flat=True).distinct())
    
    elif product_type == 'motherboard':
        if 'form_factor' in model_fields:
            form_factor = request.GET.get('form_factor')
            if form_factor:
                products = products.filter(form_factor__iexact=form_factor)
            filter_options['form_factor_options'] = model_class.objects.values_list('form_factor', flat=True).distinct()
        if 'ram_type' in model_fields:
            ram_type = request.GET.get('ram_type')
            if ram_type:
                products = products.filter(ram_type__iexact=ram_type)
            filter_options['ram_type_options'] = model_class.objects.values_list('ram_type', flat=True).distinct()
        if 'ram_slots' in model_fields:
            ram_slots = request.GET.get('ram_slots')
            if ram_slots:
                try:
                    products = products.filter(ram_slots__gte=int(ram_slots))
                except (ValueError, TypeError):
                    pass
            filter_options['ram_slots_options'] = sorted(model_class.objects.values_list('ram_slots', flat=True).distinct())
    
    elif product_type == 'speakers':
        if 'connection_type' in model_fields:
            connection_type = request.GET.get('connection_type')
            if connection_type:
                products = products.filter(connection_type__iexact=connection_type)
            filter_options['connection_type_options'] = model_class.objects.values_list('connection_type', flat=True).distinct()
    
    # Apply sorting
    # Convert queryset to list for case-insensitive sorting like in all_products view
    products_list = list(products)
    
    if sort_by == 'price_low':
        products_list.sort(key=lambda x: x.price if x.price else float('inf'))
    elif sort_by == 'price_high':
        products_list.sort(key=lambda x: x.price if x.price else float('-inf'), reverse=True)
    elif sort_by == 'name_asc':
        products_list.sort(key=lambda x: x.name.lower())
    elif sort_by == 'name_desc':
        products_list.sort(key=lambda x: x.name.lower(), reverse=True)
    else:  # newest
        products_list.sort(key=lambda x: x.id, reverse=True)
    
    # Convert back to queryset-like object for template compatibility
    products = products_list
    
    # Get unique brands for filter dropdown
    all_brands = model_class.objects.values_list('brand', flat=True).distinct()
    
    # Update context to include counts for all categories
    context = {
        'products': products,
        'product_type': product_type,
        'product_type_display': product_type.replace('_', ' ').title(),
        'all_brands': all_brands,
        'current_brand': brand,
        'current_condition': condition,
        'current_sort': sort_by,
        'filter_options': filter_options,
        'title': f'{product_type.replace("_", " ").title()}s - Browse All',
        'cpu_count': CPU.objects.count(),
        'gpu_count': GPU.objects.count(),
        'ram_count': RAM.objects.count(),
        'storage_count': StorageDevice.objects.count(),
        'motherboard_count': Motherboard.objects.count(),
        'case_count': Case.objects.count(),
        'psu_count': PSU.objects.count(),
        'monitor_count': Monitor.objects.count(),
        'tablet_count': Tablet.objects.count(),
        'laptop_count': Laptop.objects.count(),
        'mouse_count': Mouse.objects.count(),
        'keyboard_count': Keyboard.objects.count(),
        'headset_count': Headset.objects.count(),
        'speakers_count': Speakers.objects.count(),
        'other_accessory_count': OtherAccessory.objects.count(),
    }
    
    return render(request, 'store/product_list.html', context)

def all_products(request):
    """View to handle both search and all products listing"""
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort_by', 'newest')
    condition = request.GET.get('condition', '')
    category = request.GET.get('category', '')
    
    # Update model map to include all categories
    model_map = {
        'GPU': GPU,
        'CPU': CPU,
        'RAM': RAM,
        'MOTHERBOARD': Motherboard,
        'CASE': Case,
        'STORAGE': StorageDevice,
        'PSU': PSU,
        'MONITOR': Monitor,
        'TABLET': Tablet,
        'LAPTOP': Laptop,
        'MOUSE': Mouse,  # Added
        'KEYBOARD': Keyboard,  # Added
        'HEADSET': Headset,  # Added
        'SPEAKERS': Speakers,  # Added
        'OTHER_ACCESSORY': OtherAccessory,  # Added
    }
    
    results = []
    for model_name, model in model_map.items():
        # Skip if category filter is active and doesn't match
        if category and category.upper() != model_name:
            continue
            
        queryset = model.objects.all()
        
        # Apply search filter if query exists
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(brand__icontains=query) |
                Q(description__icontains=query) |
                Q(sku__icontains=query)
            )
        
        # Apply condition filter
        if condition:
            queryset = queryset.filter(condition=condition)
        
        for product in queryset:
            results.append({
                'type': model_name,
                'product': product
            })
    
    # Apply sorting
    if sort_by == 'price_low':
        results.sort(key=lambda x: x['product'].price if x['product'].price else float('inf'))
    elif sort_by == 'price_high':
        results.sort(key=lambda x: x['product'].price if x['product'].price else float('-inf'), reverse=True)
    elif sort_by == 'name_asc':
        results.sort(key=lambda x: x['product'].name.lower())
    elif sort_by == 'name_desc':
        results.sort(key=lambda x: x['product'].name.lower(), reverse=True)
    else:  # newest
        results.sort(key=lambda x: x['product'].id, reverse=True)
    
    # Update categories list to include all categories with counts
    categories = [
        {'code': 'GPU', 'name': 'Graphics Cards', 'count': GPU.objects.count()},
        {'code': 'CPU', 'name': 'Processors', 'count': CPU.objects.count()},
        {'code': 'RAM', 'name': 'Memory', 'count': RAM.objects.count()},
        {'code': 'MOTHERBOARD', 'name': 'Motherboards', 'count': Motherboard.objects.count()},
        {'code': 'CASE', 'name': 'Cases', 'count': Case.objects.count()},
        {'code': 'STORAGE', 'name': 'Storage', 'count': StorageDevice.objects.count()},
        {'code': 'PSU', 'name': 'Power Supplies', 'count': PSU.objects.count()},
        {'code': 'MONITOR', 'name': 'Monitors', 'count': Monitor.objects.count()},
        {'code': 'TABLET', 'name': 'Tablets', 'count': Tablet.objects.count()},
        {'code': 'LAPTOP', 'name': 'Laptops', 'count': Laptop.objects.count()},
        {'code': 'MOUSE', 'name': 'Mice', 'count': Mouse.objects.count()},  # Added
        {'code': 'KEYBOARD', 'name': 'Keyboards', 'count': Keyboard.objects.count()},  # Added
        {'code': 'HEADSET', 'name': 'Headsets', 'count': Headset.objects.count()},  # Added
        {'code': 'SPEAKERS', 'name': 'Speakers', 'count': Speakers.objects.count()},  # Added
        {'code': 'OTHER_ACCESSORY', 'name': 'Other Accessories', 'count': OtherAccessory.objects.count()},  # Added
    ]
    
    context = {
        'query': query,
        'products': results,
        'total_count': len(results),
        'current_sort': sort_by,
        'current_condition': condition,
        'current_category': category,
        'categories': categories,
        'title': 'Search Results' if query else 'All Products',
        'conditions': ['new', 'used', 'refurbished', 'box_open'],
        'sort_options': [
            {'value': 'newest', 'label': 'Newest First'},
            {'value': 'price_low', 'label': 'Price: Low to High'},
            {'value': 'price_high', 'label': 'Price: High to Low'},
            {'value': 'name_asc', 'label': 'Name: A to Z'},
            {'value': 'name_desc', 'label': 'Name: Z to A'},
        ],
    }
    
    return render(request, 'store/all_products.html', context)

def all_categories(request):
    """
    View to display all product categories
    """
    # Get counts for each category
    context = {
        'gpu_count': GPU.objects.count(),
        'cpu_count': CPU.objects.count(),
        'ram_count': RAM.objects.count(),
        'motherboard_count': Motherboard.objects.count(),
        'case_count': Case.objects.count(),
        'storage_count': StorageDevice.objects.count(),
        'psu_count': PSU.objects.count(),
        'monitor_count': Monitor.objects.count(),
        'tablet_count': Tablet.objects.count(),
        'laptop_count': Laptop.objects.count(),
        'mouse_count': Mouse.objects.count(),
        'keyboard_count': Keyboard.objects.count(),
        'headset_count': Headset.objects.count(),
        'speakers_count': Speakers.objects.count(),
        'other_accessory_count': OtherAccessory.objects.count(),
        'title': 'All Categories'
    }
    
    return render(request, 'store/all_categories.html', context)

def subscribe_newsletter(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            response_data = {
                'success': True,
                'message': 'Thank you for subscribing to our newsletter!'
            }
        else:
            response_data = {
                'success': False,
                'message': form.errors.get('email', 'Subscription failed. Please try again.')
            }
            
        # Check if request is AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response_data)
            
        # For non-AJAX requests, maintain the old behavior
        if response_data['success']:
            messages.success(request, response_data['message'])
        else:
            messages.error(request, response_data['message'])
        return redirect(request.META.get('HTTP_REFERER', '/'))
        
    return redirect('home')

def about_us(request):
    return render(request, 'store/about_us.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for contacting us! We'll get back to you soon.")
            return redirect('contact')
        else:
            messages.error(request, "There was an error with your submission. Please check the form and try again.")
    else:
        form = ContactForm()
    return render(request, 'store/CONTACT_US.HTML', {'form': form, 'title': 'Contact Us'})

def faq(request):
    return render(request, 'store/faq.html')

def terms_and_conditions(request):
    return render(request, 'store/term.html')

def privacy_policy(request):
    return render(request, 'store/privacy_policy.html')

def order_return_policy_view(request):
    return render(request, 'store/order_return_policy.html')

def customer_support_view(request):
    return render(request, 'store/customer_support.html')

def why_ggt_view(request):
    return render(request, 'store/why_ggt.html')

def handler404(request, exception):
    """
    Custom 404 error handler
    """
    return render(request, '404.html', status=404)