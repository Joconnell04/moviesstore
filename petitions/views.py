from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.views import View
from .models import Petition, PetitionVote


class PetitionListView(ListView):
    """
    Public view showing all petitions with YES vote counts.
    """
    model = Petition
    template_name = 'petitions/list.html'
    context_object_name = 'petitions'
    paginate_by = 20


class PetitionDetailView(DetailView):
    """
    Public view showing petition details and YES vote count.
    Displays whether current user has already voted.
    """
    model = Petition
    template_name = 'petitions/detail.html'
    context_object_name = 'petition'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Check if user has already voted
            context['user_has_voted'] = PetitionVote.objects.filter(
                petition=self.object,
                voter=self.request.user
            ).exists()
        else:
            context['user_has_voted'] = False
        return context


class PetitionCreateView(LoginRequiredMixin, CreateView):
    """
    Login-required view for creating a new petition.
    """
    model = Petition
    template_name = 'petitions/create.html'
    fields = ['title', 'proposed_movie_title', 'reason']
    success_url = reverse_lazy('petitions:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Your petition has been created successfully!')
        return super().form_valid(form)


class PetitionYesVoteView(LoginRequiredMixin, View):
    """
    POST-only view for casting a YES vote on a petition.
    Idempotent: if user already voted, shows message but doesn't error.
    Enforces one vote per user via unique_together constraint.
    """
    def post(self, request, pk):
        petition = get_object_or_404(Petition, pk=pk)

        try:
            # Try to create the vote
            PetitionVote.objects.create(
                petition=petition,
                voter=request.user,
                yes=True
            )
            messages.success(request, f'Your YES vote has been recorded for "{petition.title}"!')
        except IntegrityError:
            # User already voted
            messages.info(request, 'You have already voted on this petition.')

        return redirect('petitions:detail', pk=petition.pk)
