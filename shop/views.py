from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, FormView, ListView, DetailView
from .models import Product, Cart, CartItem, Order
from .forms import AddToCartForm
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from .forms import CheckoutForm
from django.contrib.auth.mixins import LoginRequiredMixin


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ProductListView(TemplateView):
    template_name = 'product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context


class CartView(TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        cart = Cart.objects.filter(id=cart_id).first() if cart_id else None
        context['cart'] = cart
        return context


#Добавлениев корзину
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_id = request.session.get('cart_id', None)
    if not cart_id: #создаём корзину если её нету
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id
    else:
        cart = Cart.objects.get(id=cart_id) #используем существующую корзину пользователя

    cart_item, created = CartItem.objects.get_or_create(product=product)
    if not created:  # если товар уже есть в корзине при клике на "добавить в корзину" увеличить его количество
        cart_item.quantity += 1
        cart_item.save()
    cart.items.add(cart_item)
    cart.save()
    return redirect('/')


#Удаление с корзины
def remove_from_cart(request, item_id):
    cart_id = request.session.get('cart_id', None)
    cart = Cart.objects.get(id=cart_id)
    item = get_object_or_404(CartItem, id=item_id)
    cart.items.remove(item)
    item.delete()
    return redirect('cart_view')


#Изменение количества товаров в корзине
def update_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)

        #пробуем считать значение, т.е. при передачи пустого блока возникает ошибка(int(None))
        quantity_str = request.POST.get('quantity', '1')
        try:
            new_quantity = int(quantity_str)
        except ValueError:
            new_quantity = 0  #если значение некорректное, устанавливаем 0

        #обновляем количество, если оно больше 0
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item.delete()  #удаляем товар из корзины, если количество <= 0

    return redirect('cart_view')


class CheckoutView(LoginRequiredMixin, FormView):
    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('order_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id')
        cart = Cart.objects.filter(id=cart_id).first()
        context['cart'] = cart
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get('cart_id')
        cart = Cart.objects.filter(id=cart_id).first()

        if not cart or not cart.items.exists():
            form.add_error(None, "Your cart is empty.")
            return self.form_invalid(form)

        #создаем заказ
        address = form.cleaned_data['address']
        phone_number = form.cleaned_data['phone_number']
        order = Order.objects.create(
            user=self.request.user,
            total_price=cart.total_price(),
            address=address,
            phone_number=phone_number,
        )
        for item in cart.items.all():
            order.items.add(item)

        cart.items.clear()
        self.request.session.pop('cart_id', None)

        new_cart = Cart.objects.create()
        self.request.session['cart_id'] = new_cart.id

        self.request.session['order_id'] = order.id
        return super().form_valid(form)


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

    def get_object(self):
        order = get_object_or_404(Order, id=self.kwargs['pk'], user=self.request.user)
        return order
