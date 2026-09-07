from django.utils.text import slugify

def set_slug(instance, value):
    base_slug = slugify(value)
    counter = 1

    if not base_slug:
        raise ValueError('cannot generate slug')

    queryset = instance.__class__.objects.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    slug = base_slug
    while queryset.filter(slug=slug).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1

    instance.slug = slug
    return slug