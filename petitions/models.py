from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Petition(models.Model):
    """
    Represents a petition to include a movie in the store.
    """
    title = models.CharField(max_length=255, help_text="Short title for the petition")
    proposed_movie_title = models.CharField(max_length=255, help_text="Movie title being petitioned")
    reason = models.TextField(help_text="Reason for including this movie")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='petitions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.proposed_movie_title}"

    def get_absolute_url(self):
        return reverse('petitions:detail', kwargs={'pk': self.pk})

    def yes_vote_count(self):
        """Return the total number of YES votes."""
        return self.votes.filter(yes=True).count()


class PetitionVote(models.Model):
    """
    Represents a vote on a petition. Each user can vote once per petition.
    """
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='petition_votes')
    yes = models.BooleanField(default=True)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('petition', 'voter')
        ordering = ['-voted_at']

    def __str__(self):
        return f"{self.voter.username} voted {'YES' if self.yes else 'NO'} on {self.petition.title}"
