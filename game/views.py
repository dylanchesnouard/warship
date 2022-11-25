from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.urls import reverse_lazy
from .models import Grid
from .forms import ShotForm
from django.http import Http404


# Create your views here.
class GridCreateView(CreateView):
    """
    Allows the creation of a new Grid and see the list of grid already created
    """
    model = Grid
    fields = ["nb_rows", "nb_columns"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add grid history to context
        context["grid_history"] = Grid.objects.all()
        return context

    def get_success_url(self):
        # If the grid is created successfully, redirect to the grid page
        return reverse("game:grid-detail-hidden", args=(self.object.id,))


class GridDeleteView(DeleteView):
    """
    Allows to delete a grid, then redirect to the creation grid page
    """
    model = Grid
    success_url = reverse_lazy("game:grid-form")


class GridDetailView(FormMixin, DetailView):
    """
    Only used by HiddenGridDetailView and VisibleGridDetailView !
    Allow to see the grid and shoot
    """
    model = Grid
    form_class = ShotForm

    def get_object(self, queryset=None):
        # Get the grid that match the UUID in the url
        try:
            my_grid = Grid.objects.get(id=self.kwargs.get("pk"))
            return my_grid
        except self.model.DoesNotExist:
            raise Http404("No grid matches the given query.")

    def get_initial(self):
        # Fill the 'grid' field of the ShotForm
        return {"grid": self.object}

    def post(self, request, *args, **kwargs):
        # Validation of the ShotForm
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class HiddenGridDetailView(GridDetailView):
    """
    Inherits from GridDetailView
    Display a hidden grid, only water and shot are visible
    """
    template_name = "game/grid_detail_hidden.html"

    def get_success_url(self):
        return reverse("game:grid-detail-hidden", args={self.object.id})

    def form_valid(self, form):
        form.save()
        return super(HiddenGridDetailView, self).form_valid(form)


class VisibleGridDetailView(GridDetailView):
    """
    Inherits from GridDetailView
    Display a visible grid (ships and ships safe space are visible)
    Display a detailed ships list
    """
    template_name = "game/grid_detail_visible.html"

    def get_success_url(self):
        return reverse("game:grid-detail-visible", args={self.object.id})

    def form_valid(self, form):
        form.save()
        return super(VisibleGridDetailView, self).form_valid(form)


@require_http_methods(["GET"])
def grid_regenerate(request, pk):
    """
    Allow to (re)generate ships placement
    :param request:
    :param pk: UUID : grid's UUID
    :return: redirect to HiddenGridDetailView
    """
    grid = get_object_or_404(Grid, id=pk)
    grid.regenerate_grid()
    return HttpResponseRedirect(reverse("game:grid-detail-hidden", args=(pk,)))
