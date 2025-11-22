from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from users.models import CustomUser


@permission_required("users.view_customuser")
def block_user(self, pk):
    user = CustomUser.objects.get(pk=pk)
    user.is_active = not user.is_active
    user.save()
    return redirect(reverse("users:users_list"))


def email_verification(request, token):
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.save()
    return HttpResponseRedirect(reverse("newsletter:home"))
