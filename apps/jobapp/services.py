from django.shortcuts import get_object_or_404
from jobapp.models import Job, Applicant, BookmarkJob
from account.models import User

def toggle_job_status(user_id: int, job_id: int) -> bool:
    """Marks a job as closed."""
    job = get_object_or_404(Job, id=job_id, user=user_id)
    job.is_closed = True
    job.save()
    return True

def get_skill_match_count(employee_id: int, job_id: int) -> int:
    """
    Calculate how many skills the employee has that match the job requirements.
    Returns count of matching skills.
    """
    user = get_object_or_404(User, id=employee_id)
    job = get_object_or_404(Job, id=job_id)
    
    # Get employee's skills
    try:
        employee_skills = set(user.employee_profile.skills.values_list('id', flat=True))
    except:
        employee_skills = set()
    
    # Get job required skills
    job_skills = set(job.skills.values_list('id', flat=True))
    
    # Find matching skills
    matching_skills = employee_skills & job_skills
    
    return len(matching_skills)

def get_job_required_skills_count(job_id: int) -> int:
    """Get total number of required skills for a job."""
    job = get_object_or_404(Job, id=job_id)
    return job.skills.count()

def get_applicant_skill_stats(applicant_id: int) -> dict:
    """
    Get skill matching statistics for an applicant.
    Returns dict with: matched_count, required_count, percentage.
    """
    applicant = get_object_or_404(Applicant, id=applicant_id)
    
    matched_count = get_skill_match_count(applicant.user_id, applicant.job_id)
    required_count = get_job_required_skills_count(applicant.job_id)
    
    percentage = 0
    if required_count > 0:
        percentage = (matched_count / required_count) * 100
    
    return {
        'matched_count': matched_count,
        'required_count': required_count,
        'percentage': round(percentage, 1)
    }

# def delete_user_job(user_id: int, job_id: int) -> bool:
#     """Deletes a job created by an employer."""
#     job = get_object_or_404(Job, id=job_id, user=user_id)
#     job.delete()
#     return True

# def remove_bookmark(user_id: int, bookmark_id: int) -> bool:
#     """Deletes a saved bookmark."""
#     bookmark = get_object_or_404(BookmarkJob, id=bookmark_id, user=user_id)
#     bookmark.delete()
#     return True
