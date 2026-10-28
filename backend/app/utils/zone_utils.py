from shapely.geometry import Polygon

# ============================================================
# Restricted Zone Configuration
# Modify these coordinates based on your camera view.
#
# Example:
#
# (200,150) ---------------------- (500,150)
#      |                               |
#      |                               |
#      |                               |
#      |                               |
# (200,450) ---------------------- (500,450)
#
# ============================================================

RESTRICTED_ZONE = Polygon(
    [
        (200, 150),
        (500, 150),
        (500, 450),
        (200, 450),
    ]
)


def get_zone():
    """
    Returns the configured restricted polygon.
    """
    return RESTRICTED_ZONE


def point_inside_zone(x: int, y: int) -> bool:
    """
    Check whether a single point lies inside the
    restricted polygon.
    """
    return RESTRICTED_ZONE.contains(
        Polygon(
            [
                (x, y),
                (x + 1, y),
                (x + 1, y + 1),
                (x, y + 1),
            ]
        )
    )


def bbox_intersects_zone(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
) -> bool:
    """
    Returns True if ANY PART of the person's
    bounding box overlaps the restricted zone.

    This is preferred over center-point detection
    because even a hand or foot entering the zone
    will trigger an intrusion.
    """

    person_box = Polygon(
        [
            (x1, y1),
            (x2, y1),
            (x2, y2),
            (x1, y2),
        ]
    )

    return RESTRICTED_ZONE.intersects(person_box)


def bbox_inside_zone(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
) -> bool:
    """
    Returns True only if the ENTIRE bounding box
    lies inside the restricted zone.
    """

    person_box = Polygon(
        [
            (x1, y1),
            (x2, y1),
            (x2, y2),
            (x1, y2),
        ]
    )

    return RESTRICTED_ZONE.contains(person_box)