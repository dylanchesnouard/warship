from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from .views import GridCreateView
from .models import Grid, Ship, Shot


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
        # Generate a 10x10 grid
        self.grid = Grid(nb_columns=20, nb_rows=20)
        self.grid.save()

    def test_empty_grid(self):
        # Get an empty grid of the Grid size
        empty_grid = self.grid.empty_grid()
        # Check that size is the same
        self.assertEqual(len(empty_grid), self.grid.nb_rows)
        self.assertEqual(len(empty_grid[0]), self.grid.nb_columns)

    def test_grid_place_ships_randomly(self):
        # Place ships randomly in the grid
        self.grid.place_ships_randomly()
        # Check that the 10 ships are placed
        self.assertEqual(self.grid.ships.all().count(), 10)
        # Delete the ships
        self.grid.ships.all().delete()

    def test_grid_place_ship_randomly(self):
        # Get an empty grid of the Grid size
        empty_grid = self.grid.empty_grid()
        # Try to place a 4 size ship in the grid
        ship_to_create = self.grid.place_ship_randomly(empty_grid, 4)
        ship_to_create.save()
        # Check that the ship location is in the grid
        self.assertIn(ship_to_create.x, range(self.grid.nb_columns))
        self.assertIn(ship_to_create.y, range(self.grid.nb_rows))
        # Delete the ships
        self.grid.ships.all().delete()

    def test_grid_grid(self):
        # Regenerate the grid
        self.grid.regenerate_grid()
        # Add a shot
        Shot.objects.create(
            grid=self.grid,
            x=1,
            y=1,
        )
        # Get the grid
        grid = self.grid.grid
        # Get a ship of the grid
        a_random_ship = self.grid.ships.all().first()
        # Check that the ship is visible
        self.assertEqual(Grid.Cell.SHIP, grid[a_random_ship.y][a_random_ship.x])
        # Check that the shot is visible (missed or successful)
        self.assertIn(grid[0][0], (Grid.Cell.SHOT_MISS, Grid.Cell.SHOT_SUCCESS))

    def test_grid_visible_grid(self):
        # Regenerate the grid
        self.grid.regenerate_grid()
        # Get the visible grid with headers
        visible_grid = self.grid.visible_grid
        # Check that the grid size has increased due to headers
        self.assertEqual(len(visible_grid), self.grid.nb_rows + 1)
        self.assertEqual(len(visible_grid[1]), self.grid.nb_columns + 1)
        # Check that the first cell of the first row is empty
        self.assertEqual(visible_grid[0][0], "")
        # Get a ship of the grid
        a_random_ship = self.grid.ships.all().first()
        # Check that the ship is visible
        # Add offset due to headers
        self.assertEqual(Grid.Cell.SHIP, visible_grid[a_random_ship.y + 1][a_random_ship.x + 1])

    def test_grid_hidden_grid(self):
        # Regenerate the grid
        self.grid.regenerate_grid()
        # Get the hidden grid with headers
        hidden_grid = self.grid.hidden_grid
        # Get a ship of the grid
        a_random_ship = self.grid.ships.all().first()
        # Check that the ship is not visible
        # Add offset due to headers
        self.assertIn(Grid.Cell.WATER, hidden_grid[a_random_ship.y + 1][a_random_ship.x + 1])

    def test_grid_is_game_over(self):
        # Generate a ships list of 1 submarine to be placed
        ships_list = Grid.ships_to_be_placed(nb_cruiser=0, nb_torpedoboat=0, nb_escortship=0, nb_submarine=1)
        # Regenerate the grid with the ships list
        self.grid.regenerate_grid(ships_list=ships_list)
        # Check that there is only 1 ship in the grid
        self.assertEqual(self.grid.ships.count(), 1)
        # Get the submarine location
        the_submarine = self.grid.ships.all().first()
        # Shoot the submarine
        # Offset due to the 0 index grid
        Shot.objects.create(
            grid=self.grid,
            x=the_submarine.x + 1,
            y=the_submarine.y + 1,
        )
        # Check if the game is over
        self.assertEqual(self.grid.is_game_over, True)

    def test_grid_ships_to_be_placed(self):
        ships_list = Grid.ships_to_be_placed(nb_cruiser=1, nb_torpedoboat=0, nb_escortship=0, nb_submarine=0)
        self.assertEqual(ships_list, [Ship.Size.CRUISER])

    def test_add_shot_to_grid(self):
        # Generate a ships list of 1 submarine to be placed
        ships_list = Grid.ships_to_be_placed(nb_cruiser=0, nb_torpedoboat=0, nb_escortship=0, nb_submarine=1)
        # Regenerate the grid with the ships list
        self.grid.regenerate_grid(ships_list=ships_list)
        # Get the submarine location
        the_submarine = self.grid.ships.all().first()
        # Shoot the submarine
        # Offset due to the 0 index grid
        Shot.objects.create(
            grid=self.grid,
            x=the_submarine.x + 1,
            y=the_submarine.y + 1,
        )
        # Check the cell after the shoot
        self.assertEqual(self.grid.grid[the_submarine.y][the_submarine.x], Grid.Cell.SHOT_SUCCESS)


class ShipModelTest(TestCase):
    def setUp(self):
        self.grid = Grid()
        self.grid.save()
        self.ship = Ship(
            grid=self.grid,
            x=0,
            y=0,
            orientation=Ship.Orientation.HORIZONTAL,
            ship_size=Ship.Size.TORPEDOBOAT,
        )
        self.ship.save()

    def test_ship_is_hit_and_sunk(self):
        # Add a shot on the ship
        a_shot = Shot(
            grid=self.grid,
            x=self.ship.x + 1,
            y=self.ship.y + 1,
        )
        a_shot.save()
        # Check that the ship was hit
        self.assertEqual(self.ship.is_hit(a_shot), True)
        # Check that the ship is not sunk
        self.assertEqual(self.ship.is_sunk, False)
        # Add a second shot on the ship
        a_second_shot = Shot(
            grid=self.grid,
            x=self.ship.x + 2,
            y=self.ship.y + 1,
        )
        a_second_shot.save()
        # Check that the ship was hit
        self.assertEqual(self.ship.is_hit(a_second_shot), True)
        # Check that the ship is sunk
        self.assertEqual(self.ship.is_sunk, True)

    def test_ship_location(self):
        self.assertEqual(self.ship.location, (self.ship.x + 1, self.ship.y + 1))


class ShotModelTest(TestCase):
    def setUp(self):
        self.grid = Grid()
        self.grid.save()
        self.ship = Ship(
            grid=self.grid,
            x=0,
            y=0,
            orientation=Ship.Orientation.HORIZONTAL,
            ship_size=Ship.Size.TORPEDOBOAT,
        )
        self.ship.save()

    def test_shot_is_successful(self):
        # Add a shot on the ship
        a_shot = Shot(
            grid=self.grid,
            x=self.ship.x + 1,
            y=self.ship.y + 1,
        )
        a_shot.save()
        # Check that the shot was successful
        self.assertEqual(a_shot.is_successful, True)
