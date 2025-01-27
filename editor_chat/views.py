from openai import OpenAI
from django.http import JsonResponse, StreamingHttpResponse
import json
import os
from django.utils.dateparse import parse_datetime
from .models import AIChat
from datetime import datetime
# Create your views here.
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_messages(option, prompt, command=None):
    messages_map = {
        "continue": [
            {
                "role": "system",
                "content": (
                    "You are an AI writing assistant that continues existing text based on context from prior text. "
                    "Give more weight/priority to the later characters than the beginning ones. "
                    "Limit your response to no more than 200 characters, but make sure to construct complete sentences. "
                    "Use Markdown formatting when appropriate."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "improve": [
            {
                "role": "system",
                "content": (
                    "You are an AI writing assistant that improves existing text. "
                    "Limit your response to no more than 200 characters, but make sure to construct complete sentences. "
                    "Use Markdown formatting when appropriate."
                ),
            },
            {
                "role": "user",
                "content": f"The existing text is: {prompt}. You have to respect the command: {command}",
            },
        ],
        "shorter": [
            {
                "role": "system",
                "content": (
                    "You are an AI writing assistant that shortens existing text. "
                    "Use Markdown formatting when appropriate."
                ),
            },
            {
                "role": "user",
                "content": f"The existing text is: {prompt}. You have to respect the command: {command}",
            },
        ],
        "longer": [
            {
                "role": "system",
                "content": (
                    "You are an AI writing assistant that lengthens existing text. "
                    "Use Markdown formatting when appropriate."
                ),
            },
            {
                "role": "user",
                "content": f"The existing text is: {prompt}. You have to respect the command: {command}",
            },
        ],
        "fix": [
            {
                "role": "system",
                "content": (
                    "You will be provided with statements, and your task is to convert them to standard English."
                ),
            },
            {
                "role": "user",
                "content": f"The existing text is: {prompt}. You have to respect the command: {command}",
            },
        ],
        "zap": [
            {
                "role": "system",
                "content": (
                    "You are an AI writing assistant that generates text based on a prompt. "
                    "You take an input from the user and a command for manipulating the text. "
                    "Use Markdown formatting when appropriate."
                ),
            },
            {
                "role": "user",
                "content": f"For this text: {prompt}. You have to respect the command: {command}",
            },
        ],
        "instruction": [
            {
                "role": "system",
                "content": (
                    "You are an AI writing assistant that generates text based on a prompt. "
                    "You take an input from the user and a command for manipulating the text. "
                    "Use Markdown formatting when appropriate."
                ),
            },
            {
                "role": "user",
                "content": f"For this text: {prompt}. You have to respect the command: {command}",
            },
        ],
        "chart": [
            {
                "role": "system",
                "content": (
                    "You are an AI writing assistant that generates text based on a prompt. "
                    "You take an input from the user and a command for manipulating the text. "
                    "Use Markdown formatting when appropriate."
                ),
            },
            {
                "role": "user",
                "content": f"For this text: {prompt}. Please provide only the labels and datasets with the JSON object format received from OpenAI, converted into a format compatible with Notion. The output must include two arrays: one for the labels and one for the datasets. Format the response as a valid only JavaScript object for using with Chart.js, and do not include instructions for chart or language. and You have to respect the command: {command},",
            },            
        ],
    }

    return messages_map.get(option, [])

def save_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Extract data from request
            option = data['option']
            prompt = data['prompt']
            collected_messages = data['collectedMsg']
            session_id = data['session_id']
            user_id = data['user_id']
            res = AIChat.objects.create(
                content=collected_messages,
                model="gpt-4o",  # or dynamically set this value
                type=option,  # Ensure `option` is correctly set elsewhere in your code
                user_question=prompt,  # This should be the user's input
                session_id=session_id,  # The session identifier
                user_id = user_id
            )
            res.save()
            user = {
                'created_at': res.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if isinstance(res.created_at, datetime) else res.created_at,
                'session_id': res.session_id,
                'content': res.content,
                'user_id': res.user_id,
                'user_question': res.user_question
            }

            chatHis = {
                'id': res.id,
                'user_id': res.user_id,
                'content': res.content,
                'created_at': res.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if isinstance(res.created_at, datetime) else res.created_at,
                'model': res.model,
                'response_id': res.response_id,
                'session_id': res.session_id,
                'total_tokens': res.total_tokens,
                'type': res.type,
                'user_question': res.user_question
            }

            if user and chatHis is not None:
                print("success")
                return JsonResponse(
                    {'message: ': 'created successfully!',
                     'user': user,
                     'chatHis': chatHis
                    },
                    status=200

                )
            return JsonResponse(
                {'message: ' : 'internal server Error happened!'},
                 status=400
            )

        except Exception as e:
            print(f"Error occurred: {e}")  # Log the error for debugging
            return JsonResponse({'error': 'An internal error occurred. Please try again later.'}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=400)        

def create_chat_stream(request):
    if request.method == 'POST':
        try: 
            data = json.loads(request.body)
            # Extract data from request
            option = data['option']
            prompt = data['prompt']
            command = data['command']

            # Prepare messages for the chat API
            messages = get_messages(option, prompt, command)

            # Call OpenAI API with streaming enabled
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
                temperature=0.5,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            # Process streamed response
            collected_messages = []  # Store messages as a list
            def generate_response():
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        chunk_message = chunk.choices[0].delta.content  # extract the message
                        collected_messages.append(chunk_message)
                        yield chunk_message
            result = StreamingHttpResponse(generate_response(), status=200, content_type="text/event-stream")
            return result

        except Exception as e:
            print(f"Error occurred: {e}")  # Log the error for debugging
            return JsonResponse({'error': 'An internal error occurred. Please try again later.'}, status=500)

    # Handle invalid request method
    return JsonResponse({'error': 'Method not allowed'}, status=400)

# get chats by scroll pagination

def get_first_chats(request): 
    if request.method == 'GET':
        data = request.GET
        chats = AIChat.objects.filter(user_id=data.get('user_id')).order_by('session_id', 'created_at')

        # Group by session_id and get the first chat in each session
        grouped_chats = {}
        for chat in chats:
            if chat.session_id not in grouped_chats:
                grouped_chats[chat.session_id] = chat
        first_chats = list(grouped_chats.values())
        # Handle cursor-based pagination
        cursor = data.get('cursor')  # Use get to avoid KeyError
        if cursor:
            cursor_data = parse_datetime(cursor)
            first_chats = [chat for chat in first_chats if chat.created_at > cursor_data]
        else:
            # If no cursor, just use the first page
            first_chats = first_chats

        # Paginate the results (e.g., 10 items per page)
        page_size = 28
        paginated_chats = first_chats[:page_size]

        # Prepare the response data
        response_data = {
            'chats': [{'session_id': chat.session_id, 'created_at': chat.created_at, 'content': chat.content, 'user_question': chat.user_question} for chat in paginated_chats],
            'has_next': len(first_chats) > page_size,
            'has_previous': cursor is not None,
        }

        # Add the next_cursor if there are more chats
        if len(first_chats) > page_size:
            next_cursor_chat = first_chats[page_size]
            response_data['next_cursor'] = next_cursor_chat.created_at.isoformat()
        else:
            response_data['next_cursor'] = None

        # Add the previous_cursor if applicable
        if cursor:
            response_data['previous_cursor'] = cursor
        else:
            response_data['previous_cursor'] = None

        return JsonResponse(response_data)

def get_chats_by_session_id(request):
    if request.method == "GET":
        session_id = request.GET['session_id']
        user_id = request.GET['user_id']
        if not session_id or not user_id:
            return JsonResponse({'error': 'session_id is required'}, status=400)
        try:
            chats = AIChat.objects.filter(session_id=session_id, user_id=user_id).values()
            return JsonResponse({'chats': list(chats)}, status=200)
        except AIChat.DoesNotExist:
            return JsonResponse({'error': 'No chats found for this session ID'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=400)