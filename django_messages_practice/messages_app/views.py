from django.shortcuts import render, redirect
from .models import Message
from .forms import MessageForm


def inbox(request):
    messages = Message.objects.all()
    return render(request, 'messages_app/inbox.html', {'messages': messages})


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
            return redirect('inbox')
    else:
        form = MessageForm()

    return render(request, 'messages_app/new_message.html', {'form': form})


def drafts(request):
    messages = Message.objects.filter(is_draft=True)
    return render(request, 'messages_app/drafts.html', {'messages': messages})


def sent(request):
    messages = Message.objects.filter(is_draft=False)
    return render(request, 'messages_app/sent.html', {'messages': messages})