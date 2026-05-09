from django.contrib.sitemaps import Sitemap
from jobapp.models import Job
from django.shortcuts import get_object_or_404
from jobapp.models import Job, Applicant, BookmarkJob
from account.models import User
from django.db.models import QuerySet
from jobapp.models import Job

def get_listed_jobs() -> QuerySet[Job]:
    """Return all published jobs that are not closed."""
    return Job.objects.prefetch_related('skills').select_related('user').filter(is_published=True, is_closed=False).order_by('-updated_at')

def search_jobs(title_or_company: str | None = None, location: str | None = None, job_type: str | None = None) -> QuerySet[Job]:
    """Search for jobs based on dynamic filters."""
    job_list = Job.objects.prefetch_related('skills').select_related('user').order_by('-updated_at')

    if title_or_company:
        job_list = job_list.filter(title__icontains=title_or_company) | job_list.filter(company_name__icontains=title_or_company)

    if location:
        job_list = job_list.filter(location__icontains=location)

    if job_type:
        job_list = job_list.filter(job_type__iexact=job_type)

    return job_list




def toggle_job_status(user_id: int, job_id: int) -> bool:
    """Marks a job as closed."""
    job = get_object_or_404(Job, id=job_id, user=user_id)
    job.is_closed = True
    job.save()
    return True





class JobSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Job.objects.filter(is_published=True, is_closed=False).order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        from django.urls import reverse
        return reverse('jobapp:single-job', kwargs={'id': obj.id})
