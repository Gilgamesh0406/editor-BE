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

# ai prompt key for ai chat

def get_messages(option, prompt, command=None):
    messages_map = {
        "improve": [
            {
                "role": "system",
                "content": (
                    "You are an AI writing assistant that improves existing text. "
                    "make sure to construct complete sentences. "
                ),
            },
            {
                "role": "user",
                "content": f"The existing text is: {prompt}. You have to respect the command: {command} and generate text in a more professional tone what to improve",
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
                "content": f"The existing text is: {prompt}. You have to respect the command: {command} ",
            },
        ],
        "zap": [
            {
                "role": "system",
                "content": (
                    "You are an AI writing assistant that generates text based on a prompt. "
                    "make sure to construct complete sentences. "
                    "You take an input from the user and a command for manipulating the text. "
                ),
            },
            {
                "role": "user",
                "content": f"make it Professional, structured, and respectful. fact-based, and educational. For this text: {prompt}. You have to respect the command: {command}",
            },
        ],
        "chart": [
            {
                "role": "system",
                "content": (
                    "You are an AI writing assistant that generates text based on a prompt. "
                    "You take an input from the user and a command for manipulating the text. "
                ),
            },
            {
                "role": "user",
                "content": f"For this text: {prompt}. Please provide only the labels and datasets with the JSON object format received from OpenAI, converted into a format compatible with Notion. The output must include two arrays: one for the labels and one for the datasets. Format the response as a valid only JavaScript object for using with Chart.js, and do not include instructions for chart or language. and You have to respect the command: {command},",
            },            
        ],
    }

    return messages_map.get(option, [])

# delete session

def delete_session(request):
    if request.method == 'DELETE':   
        session_id = request.GET.get('session_id')
        if not session_id:
            return JsonResponse({'error': 'Missing session_id!'})
        try:
            if not AIChat.objects.filter(session_id=session_id).exists():
                return JsonResponse({'error': f'Session ID {session_id} does not exist!'}, status=404)
            AIChat.objects.filter(session_id=session_id).delete()
            return JsonResponse({'success': f'Session ID {session_id} deleted successfully!'})
        except Exception as e:
            print(f"Error occurred: {e}")
            return JsonResponse({"error": 'An Internal error occurred. Please try again later'}, status=500)
    return  JsonResponse({'error': 'Method not allowed'}, status=400)

# save ai chat stream

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
                'title': get_meaningful_chat_history(res.user_question),
                'user_question':res.user_question
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

# get chat stream

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

# To generate a meaningful chat history title from the first message of a conversation using OpenAI,

def get_meaningful_chat_history(content):
    try:
        prompt = f"""
        You are an AI that generates concise chat history titles. Given the first message of a chat, create a short and meaningful title (3-7 words). Examples:

        1. Input: Hey, can you help me with my React project? 
           Output: React Project Assistance
        2. Input: What's the best way to structure a database for a marketplace?  
           Output: Marketplace Database Design
        3. Input: I need advice on choosing between Flutter and React Native for my app.  
           Output: Flutter vs. React Native Choice

        Now, generate a title for: "{content}"
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.5,
            max_tokens=20,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Untitled Chat"

# get chats by scroll pagination

def get_first_chats(request): 
    if request.method == 'GET':
        data = request.GET
        chats = AIChat.objects.filter(user_id=data.get('user_id')).order_by('session_id', 'created_at')

        # Group by session_id and get the first chat in each session
        grouped_chats = {}
        for chat in chats:
            if chat.session_id not in grouped_chats:
                 grouped_chats[chat.session_id] = {
                    'session_id': chat.session_id,
                    'created_at': chat.created_at.isoformat(),
                    'content': chat.content,  # Keep original content
                    'title': get_meaningful_chat_history(chat.content),  # Generate title
                    'user_question': chat.user_question
                }
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
            'chats': paginated_chats,
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

# get chats history

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

# rewrite_text

def rewrite_text(request):
    if request.method == "POST":
        data = json.loads(request.body)
            # Extract data from request
        text = data['text']
        level = data['level']

        if not text or not level:
            return JsonResponse({"error": "Text and level are required"}, status=400)
        prompt = f"You are an AI that rewrites text according to different reading levels. Rewrite the following text at a a {level} reading level:\n\n{text}."
        response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
        )
        new_text = response.choices[0].message.content
        return JsonResponse({"rewritten_text": new_text})
    return JsonResponse({'error': 'Method not allowed'}, status=400)