from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Max
from datetime import datetime
from django.contrib import messages
from .models import Message


@login_required
def chat_room(request, room_name):
    search_query = request.GET.get('search', '')

    # Fetch all users except the logged-in user
    users = User.objects.exclude(id=request.user.id)

    # Fetch messages for the selected chat room (sorted)
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    ).order_by('timestamp')

    # If search_query exists, filter messages
    if search_query:
        chats = chats.filter(content__icontains=search_query)

    # Get last messages from each user efficiently using `Max`
    last_messages = (
        Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
        .values("sender", "receiver")
        .annotate(last_message_time=Max("timestamp"))
    )

    # Convert to dictionary for quick lookup
    last_message_dict = {}
    for msg in last_messages:
        key = (msg["sender"], msg["receiver"])
        last_message_dict[key] = msg["last_message_time"]

    user_last_messages = []
    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user, receiver=user) | Q(receiver=request.user, sender=user))
        ).order_by('-timestamp').first()  # Fetch only the latest message

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # Sort users based on last message timestamp (handling None cases)
    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else datetime.min,
        reverse=True
    )

    return render(request, 'chat.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query,
    })





# https://janhavi.hhosting.in/