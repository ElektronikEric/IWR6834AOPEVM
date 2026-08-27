'''
Created on 13.08.2026

@author: ezuehlke
'''
import matplotlib.pyplot as plt
from matplotlib import colormaps
import numpy as np

# Room dimensions
ROOM_WIDTH  = 8.0   # X-Achse: -4.0 bis +4.0 m
ROOM_DEPTH  = 5.0   # Y-Achse:  0.0 bis +5.0 m
ROOM_HEIGHT = 3.0   # Z-Achse:  0.0 bis +3.0 m (Annahme)

# Radar position: Mitte der 8m-Kante, Rand des Raumes
RADAR_X =  0.0
RADAR_Y =  0.0
RADAR_Z =  1.0


class RadarVisualizer:
    """
    Visualizes detected radar objects in a 3D room.

    Usage:
        visualizer = RadarVisualizer()

        while True:
            frame = parser.get_frame()
            if frame:
                visualizer.update(frame)
    """

    def __init__(self):

        self._fig      = None
        self._ax_3d    = None
        self._colorbar = None

        self._cmap = colormaps["plasma"]
        
        self._last_draw_time = 0.0
        self._draw_interval = 0.1  # maximal 10 Plot-Updates pro Sekunde

        self._init_figure()

    # =========================================================
    # Setup
    # =========================================================

    def _init_figure(self):
        """
        Create the figure and axes once.
        """

        plt.ion()

        self._fig = plt.figure(figsize=(10, 8))
        self._ax_3d = self._fig.add_subplot(111, projection="3d")

        # Dummy-Scatter für initiale Colorbar
        dummy = self._ax_3d.scatter(
            [], [], [],
            c=[],
            cmap=self._cmap,
            vmin=0,
            vmax=1
        )
        self._colorbar = self._fig.colorbar(
            dummy,
            ax=self._ax_3d,
            label="SNR (normalized)",
            shrink=0.6
        )

    # =========================================================
    # Public API
    # =========================================================

    def update(self, frame):
        """
        Update the visualization with a new frame.

        Args:
            frame (dict): Decoded radar frame from FrameParser.get_frame()
        """

        objects      = frame.get("objects",      [])
        presence     = frame.get("presence",     None)
        frame_number = frame.get("frame_number", "?")
        tracks       = frame.get("tracks",       [])
        
        MIN_TRACK_CONFIDENCE = 0.5

        persons = [
            track
            for track in tracks
            if track.get("confidenceLevel", 0.0) >= MIN_TRACK_CONFIDENCE
        ]
        
        person_count = len(persons)

        self._ax_3d.cla()

        self._update_title(
            frame_number=frame_number,
            object_count=len(objects),
            presence=presence,
            track_count=len(tracks),
            person_count=person_count
        )
        self._draw_room()
        self._draw_presence_box()
        self._draw_radar()

        if objects:
            self._draw_objects(objects)

        if tracks:
            self._draw_tracks(tracks)

        self._fig.canvas.draw()
        self._fig.canvas.flush_events()

    def close(self):
        """
        Close the visualization window.
        """
        plt.close(self._fig)

    # =========================================================
    # Internal – Title
    # =========================================================

    def _update_title(
        self,
        frame_number,
        object_count,
        presence,
        track_count,
        person_count
    ):
    
        if presence is None:
            presence_str = "N/A"
        elif presence:
            presence_str = "YES"
        else:
            presence_str = "NO"
    
        self._fig.suptitle(
            f"Radar Frame {frame_number}  |  "
            f"Persons: {person_count}  |  "
            f"Tracks: {track_count}  |  "
            f"Objects: {object_count}  |  "
            f"Presence: {presence_str}",
            fontsize=12,
            fontweight="bold"
        )

    # =========================================================
    # Internal – Room
    # =========================================================

    def _draw_room(self):
        """
        Draw the room as a wireframe box.

        Coordinate system:
            X: -4.0 (left wall) to +4.0 (right wall)
            Y:  0.0 (radar/front wall) to +5.0 (back wall)
            Z:  0.0 (floor) to +3.0 (ceiling)
        """

        x_min, x_max = -ROOM_WIDTH  / 2, ROOM_WIDTH  / 2
        y_min, y_max =  0.0,              ROOM_DEPTH
        z_min, z_max =  0.0,              ROOM_HEIGHT

        # 12 edges of the box
        edges = [
            # Floor
            ([x_min, x_max], [y_min, y_min], [z_min, z_min]),
            ([x_min, x_max], [y_max, y_max], [z_min, z_min]),
            ([x_min, x_min], [y_min, y_max], [z_min, z_min]),
            ([x_max, x_max], [y_min, y_max], [z_min, z_min]),
            # Ceiling
            ([x_min, x_max], [y_min, y_min], [z_max, z_max]),
            ([x_min, x_max], [y_max, y_max], [z_max, z_max]),
            ([x_min, x_min], [y_min, y_max], [z_max, z_max]),
            ([x_max, x_max], [y_min, y_max], [z_max, z_max]),
            # Vertical edges
            ([x_min, x_min], [y_min, y_min], [z_min, z_max]),
            ([x_max, x_max], [y_min, y_min], [z_min, z_max]),
            ([x_min, x_min], [y_max, y_max], [z_min, z_max]),
            ([x_max, x_max], [y_max, y_max], [z_min, z_max]),
        ]

        for xs, ys, zs in edges:
            self._ax_3d.plot(
                xs, ys, zs,
                color="steelblue",
                linewidth=0.8,
                alpha=0.5
            )

        # Axis limits
        self._ax_3d.set_xlim(x_min, x_max)
        self._ax_3d.set_ylim(y_min, y_max)
        self._ax_3d.set_zlim(z_min, z_max)

        self._ax_3d.set_xlabel("X (m)")
        self._ax_3d.set_ylabel("Y (m)")
        self._ax_3d.set_zlabel("Z (m)")
        self._ax_3d.set_title("3D View")

    # =========================================================
    # Internal – Radar
    # =========================================================

    def _draw_radar(self):
        """
        Draw the radar position as a marker.
        """

        self._ax_3d.scatter(
            [RADAR_X], [RADAR_Y], [RADAR_Z],
            color="red",
            s=100,
            marker="^",
            zorder=5,
            label="Radar"
        )

        self._ax_3d.text(
            RADAR_X, RADAR_Y, RADAR_Z + 0.15,
            "Radar",
            color="red",
            fontsize=8,
            ha="center"
        )

    # =========================================================
    # Internal – Objects
    # =========================================================

    def _draw_objects(self, objects):

        xs   = np.array([o["x"]   for o in objects])
        ys   = np.array([o["y"]   for o in objects])
        zs   = np.array([o["z"]   for o in objects])
        snrs = np.array([o["snr"] for o in objects])

        snr_norm = self._normalize(snrs)

        sc = self._ax_3d.scatter(
            xs, ys, zs,
            c=snr_norm,
            cmap=self._cmap,
            vmin=0,
            vmax=1,
            s=60,
            depthshade=True,
            zorder=4
        )

        self._colorbar.update_normal(sc)

        # for i, obj in enumerate(objects):
        #     self._ax_3d.text(
        #         obj["x"], obj["y"], obj["z"] + 0.08,
        #         str(i + 1),
        #         fontsize=7,
        #         ha="center",
        #         color="white"
        #     )

    # =========================================================
    # Internal – Tracks
    # =========================================================

    def _draw_tracks(self, tracks):
        """
        Draw track positions as green markers with Track ID label.
        """

        for track in tracks:
            self._ax_3d.scatter(
                [track["posX"]],
                [track["posY"]],
                [track["posZ"]],
                color="lime",
                s=120,
                marker="o",
                zorder=5
            )

            self._ax_3d.text(
                track["posX"],
                track["posY"],
                track["posZ"] + 0.12,
                f"T{track['tid']}",
                fontsize=8,
                color="lime",
                ha="center"
            )

    # =========================================================
    # Internal – Helpers
    # =========================================================

    def _normalize(self, values):

        vmin = values.min()
        vmax = values.max()

        if vmax > vmin:
            return (values - vmin) / (vmax - vmin)

        return np.ones_like(values)
    
    
    def _draw_presence_box(self):
        """
        Draw the configured presence area.
    
        presenceBoundaryBox -3 3 0.5 7.5 -1 2
        Coordinates are relative to the radar.
        """
    
        x_min, x_max = -3.0, 3.0
        y_min, y_max = 0.5, 4.5
        z_min, z_max = -1.0, 2.0
    
        edges = [
            ([x_min, x_max], [y_min, y_min], [z_min, z_min]),
            ([x_min, x_max], [y_max, y_max], [z_min, z_min]),
            ([x_min, x_min], [y_min, y_max], [z_min, z_min]),
            ([x_max, x_max], [y_min, y_max], [z_min, z_min]),
            ([x_min, x_max], [y_min, y_min], [z_max, z_max]),
            ([x_min, x_max], [y_max, y_max], [z_max, z_max]),
            ([x_min, x_min], [y_min, y_max], [z_max, z_max]),
            ([x_max, x_max], [y_min, y_min], [z_max, z_max]),
            ([x_min, x_min], [y_max, y_max], [z_min, z_max]),
            ([x_max, x_max], [y_max, y_max], [z_min, z_max]),
        ]
    
        for xs, ys, zs in edges:
            self._ax_3d.plot(
                xs,
                ys,
                zs,
                color="green",
                linestyle="--",
                linewidth=0.8,
                alpha=0.45
            )