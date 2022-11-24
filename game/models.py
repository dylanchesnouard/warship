from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
import logging
import random
import uuid

logger = logging.getLogger("__name__")

MAX_PLACEMENT_TRY = 500

NB_CRUISER = 1
NB_ESCORTSHIP = 2
NB_TORPEDOBOAT = 3
NB_SUBMARINE = 4


# Create your models here.
class Grid(models.Model):
    class Cell(models.TextChoices):
        WATER = "~", "Water"
        SHIP = "S", "Ship"
        SHIP_SAFE_SPACE = "-", "Ship safe space"
        SHOT_SUCCESS = "X", "Success shot"
        SHOT_MISS = "O", "Miss shot"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nb_columns = models.PositiveSmallIntegerField(
        default=8, validators=[MinValueValidator(8)], verbose_name="Number of columns"
    )  # x Axis
    nb_rows = models.PositiveSmallIntegerField(
        default=8, validators=[MinValueValidator(8)], verbose_name="Number of rows"
    )  # y Axis
    created_at = models.DateTimeField(auto_now_add=True)

    def place_ships_randomly(self):
        # logger.info("Start placing the ships")
        nb_placement_try = 0
        error_occurred = True

        while error_occurred and nb_placement_try < MAX_PLACEMENT_TRY:
            # logger.info("\tAttempt n°" + str(nb_placement_try))
            placement_grid = self.empty_grid()
            error_occurred = False

            ships_to_create = []
            ships_to_place = []
            ships_to_place.extend([Ship.Size.CRUISER for _ in range(NB_CRUISER)])
            ships_to_place.extend([Ship.Size.ESCORTSHIP for _ in range(NB_ESCORTSHIP)])
            ships_to_place.extend(
                [Ship.Size.TORPEDOBOAT for _ in range(NB_TORPEDOBOAT)]
            )
            ships_to_place.extend([Ship.Size.SUBMARINE for _ in range(NB_SUBMARINE)])
            random.shuffle(ships_to_place)

            for ship_to_place in ships_to_place:
                try:
                    ship_to_create = self.place_ship_randomly(
                        placement_grid, ship_to_place
                    )
                    placement_grid = self.add_ship_to_grid(
                        placement_grid, ship_to_create
                    )
                    ships_to_create.append(ship_to_create)
                except ValueError:
                    # logger.error("A ship can't be placed !")
                    error_occurred = True
                    nb_placement_try += 1
                    break

            if not error_occurred:
                Ship.objects.bulk_create(ships_to_create)
        if error_occurred:
            raise ValueError("Too small")

    def place_ship_randomly(self, placement_grid, ship_size):
        available_cells = [
            (row_index, cell_index)
            for (row_index, row) in enumerate(placement_grid)
            for (cell_index, cell) in enumerate(row)
            if cell == Grid.Cell.WATER
        ]

        while len(available_cells) > ship_size:
            starting_cell = random.choice(available_cells)
            orientations = Ship.Orientation.choices
            random.shuffle(orientations)
            for orientation in orientations:
                can_be_placed = True
                if orientation[0] == Ship.Orientation.HORIZONTAL:
                    for cell_x_axis in range(ship_size):
                        if starting_cell[1] + cell_x_axis >= self.nb_columns:
                            can_be_placed = False
                            break
                        if (
                            placement_grid[starting_cell[0]][
                                starting_cell[1] + cell_x_axis
                            ]
                            != Grid.Cell.WATER
                        ):
                            can_be_placed = False
                            break
                else:
                    for cell_y_axis in range(ship_size):
                        if starting_cell[0] + cell_y_axis >= self.nb_rows:
                            can_be_placed = False
                            break
                        if (
                            placement_grid[starting_cell[0] + cell_y_axis][
                                starting_cell[1]
                            ]
                            != Grid.Cell.WATER
                        ):
                            can_be_placed = False
                            break

                if can_be_placed:
                    # logger.info(
                    #     "OK\tShip size "
                    #     + str(ship_size)
                    #     + "\t("
                    #     + str(starting_cell[0])
                    #     + ", "
                    #     + str(starting_cell[1])
                    #     + ")\t"
                    #     + orientation[1]
                    # )
                    ship_to_create = Ship(
                        grid=self,
                        x=starting_cell[1],
                        y=starting_cell[0],
                        orientation=orientation[0],
                        ship_size=ship_size,
                    )
                    return ship_to_create
                else:
                    # logger.info(
                    #     "NOK\tShip size "
                    #     + str(ship_size)
                    #     + "\t("
                    #     + str(starting_cell[0])
                    #     + ", "
                    #     + str(starting_cell[1])
                    #     + ")\t"
                    #     + orientation[1]
                    # )
                    available_cells.remove(starting_cell)
        # logger.info("NOK\tShip size " + str(ship_size) + "\tCan't be placed")
        raise ValueError("Impossible de placer le navire !")

    def regenerate_grid(self):
        """
        Remove all shots and ships from the grid, then place new ships randoml
        """
        # Remove all shots
        self.shots.all().delete()
        # Remove all ships
        self.ships.all().delete()
        # Place new ships randomly
        self.place_ships_randomly()

    @property
    def visible_grid(self):
        """
        Return a grid with headers where all cells are visible
        :return: list[list[Cell]] : representing the grid with headers
        """
        # Get the grid
        grid_to_return = self.grid
        # Add headers to grid
        grid_to_return = self.add_headers(grid_to_return)
        return grid_to_return

    @property
    def hidden_grid(self):
        """
        Return a grid with headers where ships and ships safe spaces are hidden
        :return: list[list[Cell]] : representing the grid with headers
        """
        # Get the grid
        grid_to_return = self.grid
        # Check each grid rows
        for row_index in range(len(grid_to_return)):
            for cell_index in range(len(grid_to_return[row_index])):
                if grid_to_return[row_index][cell_index] in (
                    Grid.Cell.SHIP,
                    Grid.Cell.SHIP_SAFE_SPACE,
                ):
                    grid_to_return[row_index][cell_index] = Grid.Cell.WATER
        # Add headers to grid
        grid_to_return = self.add_headers(grid_to_return)
        return grid_to_return

    @property
    def grid(self):
        """
        Return a grid with all cells visible
        :return: list[list[Cell]] : representing the grid
        """
        # Start with an empty grid
        grid = self.empty_grid()

        # Add all ships to the grid
        for ship in self.ships.all():
            self.add_ship_to_grid(grid, ship)

        # Add all shots to the grid
        for shot in self.shots.all():
            self.add_shot_to_grid(grid, shot)

        # Return the grid with ships and shots
        return grid

    @property
    def is_game_over(self):
        """
        Return true if all the ships are sunk
        :return: bool : True if all the ships are sunk
        """
        if self.ships.all().exists():
            for ship in self.ships.all():
                if not ship.is_sunk:
                    return False
            return True
        else:
            return False

    def add_headers(self, grid):
        """
        Add headers to the grid passed in param
        :param grid: list[list[Cell]] : representing the grid without headers
        :return: list[list[Cell]] : representing the grid with headers
        """
        # Get the grid without headers
        grid_to_return = grid
        # For each row, insert a header cell in first position
        for y_index in range(self.nb_rows):
            grid_to_return[y_index].insert(0, y_index + 1)
        # Create the first row with the first cell empty
        header_x_row = [""]
        # For each column, add a header cell
        for x_index in range(self.nb_columns):
            header_x_row.append(x_index + 1)
        grid_to_return.insert(0, header_x_row)
        return grid_to_return

    def add_ship_to_grid(self, grid, ship):
        """
        Return a grid with the ship that have been passed in param
        :param grid: list[list[Cell]] : representing the grid before the shot
        :param ship: Ship object
        :return: list[list[Cell]] : representing the grid after the ship have been placed
        """
        # Get the grid before the ship have been placed
        grid_to_return = grid
        # Get ship tiles
        ship_tiles = ship.get_tiles
        # Draw each tile in the grid
        for row_index in range(len(ship_tiles)):
            if 0 < ship.y + row_index <= self.nb_rows:
                for cell_index in range(len(ship_tiles[row_index])):
                    if 0 < ship.x + cell_index <= self.nb_columns:
                        grid_to_return[ship.y - 1 + row_index][
                            ship.x - 1 + cell_index
                        ] = ship_tiles[row_index][cell_index]
        return grid_to_return

    def add_shot_to_grid(self, grid, shot):
        """
        Return a grid with the shot that have been passed in param
        :param grid: list[list[Cell]] : representing the grid before the shot
        :param shot: Shot object
        :return: list[list[Cell]] : representing the grid after the shot have been placed
        """
        # Get the grid before the shot have been placed
        grid_to_return = grid
        # The shot is missed as long as no ship has been hit
        grid_to_return[shot.y - 1][shot.x - 1] = Grid.Cell.SHOT_MISS
        # Check for each ship if it has been hit
        for ship in self.ships.all():
            if ship.is_hit(shot):
                # Replace the original cell by a SHOT_SUCCESS cell
                grid_to_return[shot.y - 1][shot.x - 1] = Grid.Cell.SHOT_SUCCESS
                break
        return grid_to_return

    def empty_grid(self):
        """
        Return an empty grid based on the number of columns and rows of the object.
        :return: list[list[Cell]] : representing the grid
        """
        return [
            [Grid.Cell.WATER for _ in range(self.nb_columns)]
            for _ in range(self.nb_rows)
        ]

    def save(self, *args, **kwargs):
        super(Grid, self).save(*args, **kwargs)
        # self.place_ships_randomly()

    def __str__(self):
        return "Grid (" + str(self.id) + ")"

    class Meta:
        verbose_name = "Grid"
        verbose_name_plural = "Grids"
        ordering = ["-created_at"]


class Ship(models.Model):
    class Orientation(models.TextChoices):
        HORIZONTAL = "H", "Horizontal"
        VERTICAL = "V", "Vertical"

    class Size(models.IntegerChoices):
        CRUISER = 4, "Cruiser"
        ESCORTSHIP = 3, "Escortship"
        TORPEDOBOAT = 2, "Torpedoboat"
        SUBMARINE = 1, "Submarine"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grid = models.ForeignKey(Grid, on_delete=models.CASCADE, related_name="ships")
    x = models.PositiveSmallIntegerField(default=0)
    y = models.PositiveSmallIntegerField(default=0)
    orientation = models.CharField(
        max_length=1, choices=Orientation.choices, default=Orientation.HORIZONTAL
    )
    ship_size = models.PositiveSmallIntegerField(
        choices=Size.choices, default=Size.SUBMARINE
    )

    def is_hit(self, shot):
        if self.orientation[0] == Ship.Orientation.HORIZONTAL:
            if shot.y - 1 == self.y and self.x <= shot.x - 1 < self.x + self.ship_size:
                return True
        else:
            if shot.x - 1 == self.x and self.y <= shot.y - 1 < self.y + self.ship_size:
                return True
        return False

    @property
    def is_sunk(self):
        if self.orientation[0] == Ship.Orientation.HORIZONTAL:
            ship_cells = [(self.y, self.x + offset) for offset in range(self.ship_size)]
        else:
            ship_cells = [(self.y + offset, self.x) for offset in range(self.ship_size)]

        for cell in ship_cells:
            if not Shot.objects.filter(Q(x=cell[1] + 1) & Q(y=cell[0] + 1)).exists():
                return False
        return True

    @property
    def location(self):
        return self.x + 1, self.y + 1

    @property
    def get_tiles(self):
        if self.orientation[0] == Ship.Orientation.HORIZONTAL:
            ship_tiles = [
                [Grid.Cell.SHIP_SAFE_SPACE for _ in range(self.ship_size + 2)]
                for _ in range(3)
            ]
            for column in range(self.ship_size):
                ship_tiles[1][column + 1] = Grid.Cell.SHIP
        else:
            ship_tiles = [
                [Grid.Cell.SHIP_SAFE_SPACE for _ in range(3)]
                for _ in range(self.ship_size + 2)
            ]
            for row in range(self.ship_size):
                ship_tiles[row + 1][1] = Grid.Cell.SHIP
        return ship_tiles

    def __str__(self):
        return self.get_ship_size_display()

    class Meta:
        verbose_name = "Ship"
        verbose_name_plural = "Ships"


class Shot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grid = models.ForeignKey(Grid, on_delete=models.CASCADE, related_name="shots")
    x = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    y = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_successful:
            return "Successful shot (" + str(self.x) + ", " + str(self.y) + ")"
        else:
            return "Missed shot (" + str(self.x) + ", " + str(self.y) + ")"

    def clean(self):
        if self.grid.is_game_over:
            raise ValidationError("You already win !")
        if self.x > self.grid.nb_columns or self.y > self.grid.nb_rows:
            raise ValidationError("You shot out of the grid.")

    @property
    def is_successful(self):
        """
        Return True if the shot hit a ship
        :return: bool : True if the shot hit a ship
        """
        for ship in self.grid.ships.all():
            if ship.is_hit(self):
                return True

    class Meta:
        verbose_name = "Shot"
        verbose_name_plural = "Shots"
        ordering = ["-created_at"]
        unique_together = ("grid", "x", "y")
