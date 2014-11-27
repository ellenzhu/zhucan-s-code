from django.shortcuts import render, redirect
from myblog.forms import UserForm

def register(request):
  if request.method == "POST":
    user_form = UserForm(data=request.POST)
    if user_form.is_valid():
      user = user_form.save()
      user.set_password(user.password)
      user.save()
      return redirect('post.views.latest_post')
  else:
    user_form = UserForm()

  return render(request, 'registration/register.html', {'form': user_form})
