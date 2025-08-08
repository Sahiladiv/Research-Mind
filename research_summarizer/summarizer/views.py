import uuid
import os
import boto3
import tempfile
from io import BytesIO
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from dotenv import load_dotenv

from .models import UploadedPaper
from .generate_response import generate_response_using_llm
from .create_database import CreateChromaDatabase
from .query_engine import query_the_data

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def generate_presigned_url(filename, expiration=600):

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': filename},
        ExpiresIn=expiration
    )


# Upload to S3 bucket
def upload_to_s3(file_obj, filename):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    response = s3.list_buckets()
    print([bucket['Name'] for bucket in response['Buckets']])
    s3.upload_fileobj(file_obj, settings.AWS_STORAGE_BUCKET_NAME, filename, ExtraArgs={'ContentType': 'application/pdf'})
    return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{filename}"

# Upload View
def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['pdf_file']
        paper_id = str(uuid.uuid4())
        filename = f"papers/{paper_id}.pdf"

        # Read file into memory once
        file_bytes = uploaded_file.read()
        file_for_s3 = BytesIO(file_bytes)
        file_for_temp = BytesIO(file_bytes)

        # Upload to S3
        s3_url = upload_to_s3(file_for_s3, filename)

        # Save metadata to MySQL
        UploadedPaper.objects.create(
            paper_id=paper_id,
            original_filename=uploaded_file.name,
            s3_url=s3_url
        )

        # Save to a temporary file for ChromaDB processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_for_temp.read())
            tmp_path = tmp_file.name

        # Process using ChromaDB
        chroma_db = CreateChromaDatabase(openai_api_key)
        chroma_db.process_single_paper(
            paper_path=tmp_path,
            paper_id=paper_id,
            original_filename=uploaded_file.name
        )

        return redirect('chat_summary', paper_id=paper_id)

    # GET request: show previously uploaded papers
    prev_papers = UploadedPaper.objects.all()
    return render(request, 'upload.html', {'uploaded_papers': prev_papers})



# Chat Summary View
def chat_summary(request, paper_id):
    try:
        paper = UploadedPaper.objects.get(paper_id=paper_id)
        # pdf_url = paper.s3_url
        pdf_url = generate_presigned_url(f"papers/{paper.paper_id}.pdf")

    except UploadedPaper.DoesNotExist:
        return HttpResponse("Paper not found", status=404)

    # Load chat history
    chat_history = request.session.get(f'chat_history_{paper_id}', [])

    if request.method == 'POST':
        question = request.POST.get('question')
        print(openai_api_key)
        # Perform ChromaDB similarity search
        query_text, context_text = query_the_data(
            query_text=question,
            paper_id=paper_id,
            openai_api_key=openai_api_key
        )

        if context_text:
            answer = generate_response_using_llm(query_text, context_text, openai_api_key, request)
        else:
            answer = "Sorry, I couldn't find relevant content in this paper."

        # Append to chat history
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": answer})
        request.session[f'chat_history_{paper_id}'] = chat_history
        request.session[f'last_question_{paper_id}'] = question

        return redirect('chat_summary', paper_id=paper_id)

    return render(request, 'chat_summary.html', {
        "pdf_url": pdf_url,
        "chat_history": chat_history,
        "original_filename": paper.original_filename
    })

# Set LLM Dropdown
def set_lm(request):
    if request.method == 'POST':
        request.session['selected_lm'] = request.POST.get('selected_lm', 'gpt-4')
        print(request.session['selected_lm'])
    return redirect(request.META.get('HTTP_REFERER', '/'))
