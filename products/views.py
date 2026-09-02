from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import *
from django.urls import reverse_lazy
from .forms import *

# Create your views here.

class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'

    def get_queryset(self):
        return Product.objects.filter(status='P')

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'


class AddProductView(LoginRequiredMixin, FormView):
    template_name = 'products/add.html'
    form_class = ProductForm
    
    def get_success_url(self):
        return reverse_lazy('products:add_variant', kwargs={'slug': self.product.slug})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if not 'formset' in ctx:
            ctx['formset'] = ProductVariantFormset(prefix='variant')
        return ctx

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = ProductVariantFormset(request.POST, prefix='variant')

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        with transaction.atomic():
            self.product = form.save()
            formset.instance = self.product
            formset.save()
        messages.success(self.request, 'product created')
        return redirect('products:detail', self.product)

    def form_invalid(self, form, formset):
        ctx = self.get_context_data(form=form, formset=formset)
        return self.render_to_response(ctx)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'products/update.html'
    form_class = ProductForm

    def get_object(self, queryset=None):
        return get_object_or_404(Product, slug=self.kwargs.get('slug'), user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'slug': self.object.slug})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('products:list')

    def get_object(self, queryset=None):
        return get_object_or_404(Product, slug=self.kwargs.get('slug'), user=self.request.user)

class AddVariantView(LoginRequiredMixin, FormView):
    template_name = 'products/variant/add.html'
    form_class = ProductVariantForm

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'slug': self.product.slug})

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, slug=self.kwargs.get('slug'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = self.product
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'variant added')
        return super().form_valid(form)

class VariantUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductVariant
    template_name = 'products/variant/update.html'
    form_class = ProductVariantForm

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, slug=self.kwargs.get('slug'), user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'slug': self.kwargs.get('slug')})

    def get_object(self, queryset=None):
        return get_object_or_404(ProductVariant, product=self.product, pk=self.kwargs.get('id'))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = self.product
        return kwargs

class VariantDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductVariant

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'slug': self.product.slug})

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, slug=self.kwargs.get('slug'), user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            ProductVariant,
            product=self.product,
            pk=self.kwargs.get('id'),
        )