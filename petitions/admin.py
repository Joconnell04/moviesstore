from django.contrib import admin
from .models import Petition, PetitionVote


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'proposed_movie_title', 'created_by', 'created_at', 'yes_vote_count')
    list_filter = ('created_at',)
    search_fields = ('title', 'proposed_movie_title', 'reason')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(PetitionVote)
class PetitionVoteAdmin(admin.ModelAdmin):
    list_display = ('petition', 'voter', 'yes', 'voted_at')
    list_filter = ('yes', 'voted_at')
    search_fields = ('petition__title', 'voter__username')
    readonly_fields = ('voted_at',)
