from django.conf import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_application_note(job, user):
    prompt = f"""Write a consise, professional application note/cover letter (100-150 words) for this applicant Do not include information like phone numner, email, date, and address. Including the applicant's name is fine.
    
    Job title: {job.title}
    Applicant name: {user.get_full_name()}
    Job description: {job.description}
    Applicant skills: {", ".join(user.skills or [])}
    Applicant education: {user.education}
    Applicant work experience: {user.work_experience}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content