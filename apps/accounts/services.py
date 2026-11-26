from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.accounts.models import Address


def set_default_address(*, user, address_pk):
    """Atomically make one of ``user``'s addresses the default one."""
    with transaction.atomic():
        addresses = Address.objects.select_for_update().filter(user=user)
        address = get_object_or_404(addresses, pk=address_pk)

        addresses.exclude(pk=address.pk).update(is_default=False)
        address.is_default = True
        address.save(update_fields=["is_default", "updated_at"])

    return address
