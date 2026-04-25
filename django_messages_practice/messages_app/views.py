from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Message
from .forms import MessageForm


@login_required
def inbox(request):
    messages = Message.objects.all()
    return render(request, 'messages_app/inbox.html', {'messages': messages})


@login_required
def new_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)

            if 'save_draft' in request.POST:
                message.is_draft = True
            else:
                message.is_draft = False

            message.save()
            if message.is_draft:
                django_messages.success(request, "Message saved as a draft.")
            else:
                django_messages.success(request, "Message sent successfully.")
            return redirect('inbox')
    else:
        form = MessageForm()

    return render(request, 'messages_app/new_message.html', {'form': form})


@login_required
def drafts(request):
    messages = Message.objects.filter(is_draft=True)
    return render(request, 'messages_app/drafts.html', {'messages': messages})


@login_required
def sent(request):
    messages = Message.objects.filter(is_draft=False)
    return render(request, 'messages_app/sent.html', {'messages': messages})
