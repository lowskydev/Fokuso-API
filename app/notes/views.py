"""
Serializers for the Note model.
"""
from rest_framework import generics, permissions
from core.models import Note
from .serializers import NoteSerializer
from rest_framework.authentication import TokenAuthentication


# Handles GET (list all notes) and POST (create notes)
class NoteListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only returns notes for logged-in user"""
        return Note.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Assign the new notes to the logged-in user"""
        serializer.save(owner=self.request.user)


# Handles GET(retreive one note), PUT (Edit whole note),
# PATCH (update part of note), DELETE
class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only the user's notes are accessible"""
        return Note.objects.filter(owner=self.request.user)
