from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from .views import GridCreateView
from .models import Grid


# Create your tests here.
class GameTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_homepage(self):
        request = self.factory.get("/")
        response = GridCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class GridModelTest(TestCase):
    def setUp(self):
        self.grid = Grid(nb_columns=10, nb_rows=10)
        self.grid.save()

    def test_empty_grid(self):
        empty_grid = self.grid.empty_grid()
        self.assertEqual(len(empty_grid), self.grid.nb_rows)
        self.assertEqual(len(empty_grid[0]), self.grid.nb_columns)

    def test_grid_place_ships_randomly(self):
        self.grid.place_ships_randomly()
        self.assertEqual(self.grid.ships.all().count(), 10)

    def test_grid_place_ship_randomly(self):
        empty_grid = self.grid.empty_grid()
        ship_to_create = self.grid.place_ship_randomly(empty_grid, 4)
        ship_to_create.save()
        self.assertIn(ship_to_create.x, range(self.grid.nb_columns))
        self.assertIn(ship_to_create.y, range(self.grid.nb_rows))

    def test_grid_regenerate_grid(self):
        ships_before_regenerate = self.grid.ships.all()
        self.grid.regenerate_grid()
        self.assertEqual(self.grid.shots.all().count(), 0)
        self.assertNotEqual(self.grid.ships.all(), ships_before_regenerate)

    def test_grid(self):
        self.grid.regenerate_grid()
        self.assertEqual(len(self.grid.grid), self.grid.nb_rows)
        self.assertEqual(len(self.grid.grid[0]), self.grid.nb_columns)
