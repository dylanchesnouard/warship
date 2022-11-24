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
    model = Grid
    fields = ["nb_rows", "nb_columns"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["grid_history"] = Grid.objects.all()
        return context

    def get_success_url(self):
        return reverse("game:grid-detail-hidden", args=(self.object.id,))


class GridDeleteView(DeleteView):
    model = Grid
    success_url = reverse_lazy("game:grid-form")


class GridDetailView(FormMixin, DetailView):
    model = Grid
    form_class = ShotForm

    def get_object(self, queryset=None):
        try:
            my_grid = Grid.objects.get(id=self.kwargs.get("pk"))
            return my_grid
        except self.model.DoesNotExist:
            raise Http404("No grid matches the given query.")

    def get_initial(self):
        return {"grid": self.object}

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class HiddenGridDetailView(GridDetailView):
    template_name = "game/grid_detail_hidden.html"

    def get_success_url(self):
        return reverse("game:grid-detail-hidden", args={self.object.id})

    def form_valid(self, form):
        form.save()
        return super(HiddenGridDetailView, self).form_valid(form)


class VisibleGridDetailView(GridDetailView):
    template_name = "game/grid_detail_visible.html"

    def get_success_url(self):
        return reverse("game:grid-detail-visible", args={self.object.id})

    def form_valid(self, form):
        form.save()
        return super(VisibleGridDetailView, self).form_valid(form)


@require_http_methods(["GET", "POST"])
def grid_regenerate(request, pk):
    grid = get_object_or_404(Grid, id=pk)
    grid.regenerate_grid()
    return HttpResponseRedirect(reverse("game:grid-detail-hidden", args=(pk,)))
