from django.contrib import messages
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from jobapp.forms import JobEditForm, JobForm
from jobapp.models import Applicant, Skill, Job
from jobapp.permission import EmployerRequiredMixin
from jobapp.services import toggle_job_status, get_skill_match_count, get_job_required_skills_count

User = get_user_model()


class CreateJobView(EmployerRequiredMixin, CreateView):
    """Employer creates a new job post."""
    model = Job
    form_class = JobForm
    template_name = 'jobapp/post-job.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = Skill.objects.all()
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        form.save_m2m()
        messages.success(self.request, 'You are successfully posted your job! Please wait for review.')
        return redirect(reverse_lazy('jobapp:single-job', kwargs={'id': instance.id}))


class JobEditView(EmployerRequiredMixin, UpdateView):
    """Employer edits an existing job post."""
    model = Job
    form_class = JobEditForm
    template_name = 'jobapp/job-edit.html'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = Skill.objects.all()
        return context

    def form_valid(self, form):
        instance = form.save()
        messages.success(self.request, 'Your Job Post Was Successfully Updated!')
        return redirect(reverse_lazy('jobapp:single-job', kwargs={'id': instance.id}))


class DeleteJobView(EmployerRequiredMixin, DeleteView):
    """Employer deletes a job post."""
    model = Job
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('jobapp:dashboard')

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user)

    def form_valid(self, form):
        # Invalidate cache before deleting
        cache.delete(str(self.get_object().id))
        messages.success(self.request, 'Your Job Post was successfully deleted!')
        return super().form_valid(form)


class MakeCompleteJobView(EmployerRequiredMixin, View):
    """Employer marks a job as closed. (Custom action — kept as View subclass)"""
    def post(self, request, id):
        try:
            toggle_job_status(request.user.id, id)
            messages.success(request, 'Your Job was marked closed!')
        except Exception:
            messages.error(request, 'Something went wrong!')
        return redirect('jobapp:dashboard')

    # Allow GET as well for compatibility with existing links
    def get(self, request, id):
        return self.post(request, id)


class AllApplicantsView(EmployerRequiredMixin, ListView):
    """Employer views all applicants for a specific job."""
    template_name = 'jobapp/all-applicants.html'
    context_object_name = 'all_applicants'

    def get_queryset(self):
        applicants = Applicant.objects.filter(job_id=self.kwargs['id']).select_related('user', 'job', 'user__employee_profile')
        # Sort by skill match in Python (after fetching from DB)
        applicants = list(applicants)
        applicants.sort(
            key=lambda a: get_skill_match_count(a.user_id, a.job_id),
            reverse=True
        )
        return applicants
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_id = self.kwargs['id']
        job = get_object_or_404(Job, id=job_id)
        required_skills_count = get_job_required_skills_count(job_id)
        
        # Add skill match info to each applicant
        for applicant in context['all_applicants']:
            matched_count = get_skill_match_count(applicant.user_id, job_id)
            applicant.matched_skills = matched_count
            applicant.required_skills = required_skills_count
            if required_skills_count > 0:
                applicant.match_percentage = round((matched_count / required_skills_count) * 100, 1)
            else:
                applicant.match_percentage = 0
        
        context['job'] = job
        context['required_skills_count'] = required_skills_count
        return context


class ApplicantDetailsView(EmployerRequiredMixin, DetailView):
    """Employer views details of a specific applicant."""
    model = User
    template_name = 'jobapp/applicant-details.html'
    context_object_name = 'applicant'
    pk_url_kwarg = 'id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the application record to find the job
        applicant_id = self.request.GET.get('applicant_id')
        if applicant_id:
            applicant_record = get_object_or_404(Applicant, id=applicant_id)
            context['applicant_record'] = applicant_record
            context['job'] = applicant_record.job
            
            # Add skill matching information
            matched_count = get_skill_match_count(self.object.id, applicant_record.job_id)
            required_count = get_job_required_skills_count(applicant_record.job_id)
            
            context['matched_skills'] = matched_count
            context['required_skills'] = required_count
            if required_count > 0:
                context['match_percentage'] = round((matched_count / required_count) * 100, 1)
            else:
                context['match_percentage'] = 0
        
        return context


class UpdateApplicantStatusView(EmployerRequiredMixin, View):
    """Employer updates the status of an application (Accepted/Rejected)."""
    def post(self, request, id):
        applicant = get_object_or_404(Applicant, id=id)
        # Ensure the employer owns the job
        if applicant.job.user != request.user:
            messages.error(request, 'You are not authorized to perform this action.')
            return redirect('jobapp:dashboard')
        
        status = request.POST.get('status')
        if status in ['accepted', 'rejected']:
            applicant.status = status
            applicant.save()
            messages.success(request, f'Applicant has been {status}!')
        else:
            messages.error(request, 'Invalid status.')
            
        return redirect('jobapp:applicants', id=applicant.job.id)



